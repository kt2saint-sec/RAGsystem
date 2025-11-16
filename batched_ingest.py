#!/usr/bin/env python3
"""
Batched Ingestion Script for RAG Knowledge Base
Processes sources in smaller batches to avoid connection timeouts
"""

import json
import os
import sys
from pathlib import Path
import time
from typing import List, Dict
import argparse

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import logging

# Configuration
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
COLLECTION_NAME = "coding_knowledge"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
DATA_DIR = Path("data")
BATCH_SIZE = 100  # Chunks per batch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchedIngestionPipeline:
    def __init__(self, source_names: List[str] = None):
        self.source_names = source_names
        self.chroma_client = None
        self.collection = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        self.targets_map = {}
        self._load_targets_map()

    def _load_targets_map(self):
        """Load targets.json to map source names to metadata"""
        with open('targets.json', 'r') as f:
            targets = json.load(f)
            for target in targets:
                self.targets_map[target['name']] = {
                    'url': target.get('url', ''),
                    'type': target.get('type', ''),
                    'destination': target.get('destination', '')
                }
        logger.info(f"Loaded {len(self.targets_map)} target mappings")

    def initialize(self):
        """Initialize ChromaDB connection and embeddings"""
        logger.info("Initializing Batched Ingestion Pipeline...")

        # Initialize embeddings
        self.embeddings = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Connect to ChromaDB
        self.chroma_client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME
        )

        logger.info("Successfully connected to ChromaDB server.")
        logger.info("Initialization complete.")

    def get_processed_sources(self) -> set:
        """Get list of already processed source files"""
        try:
            results = self.collection.get()
            processed = set()
            for metadata in results['metadatas']:
                if 'source_file' in metadata:
                    processed.add(metadata['source_file'])
            logger.info(f"Found {len(processed)} existing sources in database.")
            return processed
        except Exception as e:
            logger.warning(f"Could not fetch existing sources: {e}")
            return set()

    def get_source_files(self, source_name: str) -> List[Path]:
        """Get all files for a specific source"""
        files = []
        extensions = ['.md', '.py', '.js', '.ts', '.json', '.txt', '.html', '.css']

        # Find source directory
        source_info = self.targets_map.get(source_name)
        if not source_info:
            logger.warning(f"Source '{source_name}' not found in targets.json")
            return files

        destination = source_info.get('destination', '')
        source_path = DATA_DIR / destination

        if not source_path.exists():
            logger.warning(f"Source path does not exist: {source_path}")
            return files

        # Collect files
        for ext in extensions:
            files.extend(source_path.rglob(f'*{ext}'))

        logger.info(f"Found {len(files)} files for source '{source_name}'")
        return files

    def process_source(self, source_name: str) -> int:
        """Process a single source"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing source: {source_name}")
        logger.info(f"{'='*60}")

        # Get files for this source
        files = self.get_source_files(source_name)
        if not files:
            logger.warning(f"No files found for source '{source_name}'")
            return 0

        # Get already processed files
        processed_files = self.get_processed_sources()

        # Filter new files
        new_files = [f for f in files if str(f.absolute()) not in processed_files]
        logger.info(f"New files to process: {len(new_files)}/{len(files)}")

        if not new_files:
            logger.info(f"All files already processed for '{source_name}'")
            return 0

        # Load documents
        documents = []
        for file_path in new_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if content.strip():
                        documents.append({
                            'content': content,
                            'path': str(file_path.absolute()),
                            'name': file_path.name
                        })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")

        logger.info(f"Loaded {len(documents)} documents")

        if not documents:
            return 0

        # Split into chunks
        all_chunks = []
        for doc in documents:
            chunks = self.text_splitter.split_text(doc['content'])
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk,
                    'metadata': {
                        'technology': source_name,
                        'source_url': self.targets_map[source_name].get('url', ''),
                        'source_file': doc['path'],
                        'chunk_index': i
                    }
                })

        logger.info(f"Created {len(all_chunks)} chunks")

        # Embed and store in batches
        total_stored = 0
        for i in range(0, len(all_chunks), BATCH_SIZE):
            batch = all_chunks[i:i + BATCH_SIZE]

            try:
                # Prepare batch data
                texts = [c['text'] for c in batch]
                metadatas = [c['metadata'] for c in batch]
                ids = [f"{source_name}_{i+j}" for j in range(len(batch))]

                # Add to ChromaDB
                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )

                total_stored += len(batch)
                logger.info(f"Stored batch {i//BATCH_SIZE + 1}/{(len(all_chunks)-1)//BATCH_SIZE + 1}: {len(batch)} chunks")

                # Small delay to avoid overwhelming the server
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Failed to store batch starting at {i}: {e}")
                continue

        logger.info(f"✓ Completed '{source_name}': {total_stored} chunks stored")
        return total_stored

    def run(self):
        """Run batched ingestion"""
        self.initialize()

        if not self.source_names:
            logger.error("No sources specified")
            return

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting batched ingestion for {len(self.source_names)} sources")
        logger.info(f"{'='*60}\n")

        total_chunks = 0
        successful = 0
        failed = []

        for idx, source_name in enumerate(self.source_names, 1):
            logger.info(f"\n[{idx}/{len(self.source_names)}] Processing: {source_name}")

            try:
                chunks_stored = self.process_source(source_name)
                total_chunks += chunks_stored
                successful += 1
            except Exception as e:
                logger.error(f"Failed to process '{source_name}': {e}")
                failed.append(source_name)
                continue

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("INGESTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Sources processed: {successful}/{len(self.source_names)}")
        logger.info(f"Total chunks stored: {total_chunks}")
        if failed:
            logger.warning(f"Failed sources ({len(failed)}): {', '.join(failed)}")
        logger.info(f"{'='*60}\n")


def get_all_source_names() -> List[str]:
    """Get all source names from targets.json"""
    with open('targets.json', 'r') as f:
        targets = json.load(f)
        return [t['name'] for t in targets]


def main():
    parser = argparse.ArgumentParser(description="Batched RAG ingestion by source")
    parser.add_argument(
        '--sources',
        nargs='+',
        help='Specific sources to process (e.g., "Ollama Documentation" "PyTorch Documentation")'
    )
    parser.add_argument(
        '--batch',
        type=int,
        help='Process batch N of sources (1-indexed, 10 sources per batch)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available sources'
    )

    args = parser.parse_args()

    all_sources = get_all_source_names()

    if args.list:
        print("\nAvailable sources:")
        for i, source in enumerate(all_sources, 1):
            print(f"  {i:3d}. {source}")
        print(f"\nTotal: {len(all_sources)} sources")
        print(f"Total batches (10 per batch): {(len(all_sources) - 1) // 10 + 1}")
        return

    # Determine which sources to process
    if args.sources:
        sources_to_process = args.sources
    elif args.batch:
        batch_num = args.batch - 1  # 0-indexed
        batch_size = 10
        start_idx = batch_num * batch_size
        end_idx = start_idx + batch_size
        sources_to_process = all_sources[start_idx:end_idx]

        if not sources_to_process:
            logger.error(f"Batch {args.batch} is out of range (max: {(len(all_sources)-1)//10 + 1})")
            return

        logger.info(f"Processing batch {args.batch} ({len(sources_to_process)} sources)")
    else:
        logger.error("Must specify --sources or --batch")
        parser.print_help()
        return

    # Run ingestion
    pipeline = BatchedIngestionPipeline(source_names=sources_to_process)
    pipeline.run()


if __name__ == "__main__":
    main()
