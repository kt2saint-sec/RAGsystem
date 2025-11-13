import os
import json
import chromadb
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import logging
import time

# --- Configuration ---
DATA_DIR = 'data'
TARGETS_FILE = 'targets.json'
CHROMA_HOST = 'localhost'
CHROMA_PORT = '8001'
COLLECTION_NAME = 'coding_knowledge'
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IngestionPipeline:
    def __init__(self):
        logging.info("Initializing Ingestion Pipeline...")
        self.targets_map = self._load_targets_map()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        try:
            self.chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            self.collection = self.chroma_client.get_or_create_collection(name=COLLECTION_NAME)
            logging.info("Successfully connected to ChromaDB server.")
        except Exception as e:
            logging.error(f"Failed to connect to ChromaDB server: {e}")
            logging.error(f"Please ensure the ChromaDB server is running and accessible at {CHROMA_HOST}:{CHROMA_PORT}.")
            raise
        logging.info("Initialization complete.")

    def _load_targets_map(self):
        """Loads the targets.json file and creates a map for easy lookup."""
        if not os.path.exists(TARGETS_FILE):
            logging.error(f"Targets file not found: {TARGETS_FILE}")
            return {}
        
        with open(TARGETS_FILE, 'r') as f:
            targets = json.load(f)
        
        # Create a map from destination directory to target info
        targets_map = {}
        for target in targets:
            # Use the first part of the destination path as the key
            key = target['destination'].split('/')[1]
            targets_map[key] = {
                "name": target["name"],
                "url": target["url"]
            }
        return targets_map

    def _get_metadata_for_file(self, file_path):
        """Generates metadata for a file based on its path and the targets map."""
        try:
            # e.g., 'data/repos/react_dev' -> 'react_dev'
            path_parts = file_path.split(os.path.sep)
            if len(path_parts) > 2:
                key = path_parts[2]
                target_info = self.targets_map.get(key)
                if target_info:
                    return {
                        "technology": target_info["name"],
                        "source_url": target_info["url"],
                        "source_file": file_path
                    }
        except Exception:
            pass
        
        # Fallback metadata
        return {"source_file": file_path}

    def _get_existing_sources(self):
        """Gets a set of all 'source_file' paths already in the database."""
        try:
            existing_metadata = self.collection.get(include=["metadatas"])
            sources = set(meta['source_file'] for meta in existing_metadata['metadatas'] if 'source_file' in meta)
            logging.info(f"Found {len(sources)} existing sources in the database.")
            return sources
        except Exception as e:
            logging.warning(f"Could not retrieve existing sources, will perform a full ingest. Error: {e}")
            return set()

    def run(self):
        """
        Executes the full ingestion pipeline.
        """
        logging.info("--- Starting Ingestion Process ---")
        
        # Get a set of already processed source files
        existing_sources = self._get_existing_sources()

        # 1. Load all documents from the data directory, only picking allowed file types
        logging.info(f"Scanning '{DATA_DIR}' for new documents...")
        
        ALLOWED_EXTENSIONS = [".md", ".py", ".js", ".ts", ".json", ".txt", ".html", ".css"]
        all_docs = []

        for ext in ALLOWED_EXTENSIONS:
            glob_pattern = f"**/*{ext}"
            try:
                loader = DirectoryLoader(
                    DATA_DIR,
                    glob=glob_pattern,
                    loader_cls=TextLoader,
                    recursive=True,
                    show_progress=True,
                    use_multithreading=True,
                    # Silently ignore errors on individual files that can't be read
                    silent_errors=True
                    # Note: file_filter parameter not supported in this langchain version
                    # tokenizer.json files will be filtered manually if needed
                )
                loaded_docs = loader.load()
                all_docs.extend(loaded_docs)
                logging.info(f"Found {len(loaded_docs)} documents with extension {ext}")
            except Exception as e:
                logging.warning(f"Error loading files with extension {ext}: {e}")
        
        # Filter out documents that have already been ingested
        documents = [doc for doc in all_docs if doc.metadata['source'] not in existing_sources]
        logging.info(f"Found {len(all_docs)} total files. After filtering, there are {len(documents)} new documents to ingest.")

        logging.info(f"Loaded {len(documents)} documents.")

        if not documents:
            logging.warning("No documents found to ingest.")
            return

        # 2. Add metadata to each document
        logging.info("Attaching metadata to documents...")
        for doc in documents:
            doc.metadata = self._get_metadata_for_file(doc.metadata['source'])

        # 3. Split documents into chunks
        logging.info("Splitting documents into chunks...")
        chunks = self.text_splitter.split_documents(documents)
        logging.info(f"Created {len(chunks)} chunks.")

        if not chunks:
            logging.warning("No chunks created from documents.")
            return

        # 4. Embed and store in ChromaDB
        logging.info("Embedding chunks and storing in ChromaDB. This may take a while...")
        batch_size = 100  # Process in batches to manage memory
        total_chunks = len(chunks)
        
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i:i+batch_size]
            
            ids = [f"{chunk.metadata['source_file']}-{i+j}" for j, chunk in enumerate(batch_chunks)]
            documents_to_embed = [chunk.page_content for chunk in batch_chunks]
            metadatas = [chunk.metadata for chunk in batch_chunks]

            start_time = time.time()
            embeddings = self.embedding_model.encode(documents_to_embed, show_progress_bar=False).tolist()
            end_time = time.time()
            
            logging.info(f"Batch {i//batch_size + 1}/{(total_chunks-1)//batch_size + 1}: Embedded {len(batch_chunks)} chunks in {end_time - start_time:.2f} seconds.")

            self.collection.add(
                embeddings=embeddings,
                documents=documents_to_embed,
                metadatas=metadatas,
                ids=ids
            )
        
        logging.info("--- Ingestion Process Finished ---")
        logging.info(f"Successfully added {total_chunks} chunks to the '{COLLECTION_NAME}' collection.")
        logging.info(f"Database is stored at: '{DB_PATH}'")


if __name__ == "__main__":
    pipeline = IngestionPipeline()
    pipeline.run()
