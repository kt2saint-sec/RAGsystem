#!/usr/bin/env python3
"""
BM25 Indexer for Hybrid Search
Builds and maintains BM25 keyword search index for RAG system
"""

import sys
import chromadb
from rank_bm25 import BM25Okapi
import pickle
import logging
from typing import List, Dict, Any
import re
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BM25Indexer:
    """
    Build and maintain BM25 index for keyword search in RAG system.
    """

    def __init__(self, chroma_host: str = "localhost", chroma_port: int = 8001):
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        self.bm25_index = None
        self.documents = []
        self.metadatas = []
        self.doc_ids = []

    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        # Lowercase, split on non-alphanumeric, remove short tokens
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [t for t in tokens if len(t) > 2]

    def build_index(self, collection_name: str = "coding_knowledge"):
        """
        Build BM25 index from all documents in ChromaDB collection.

        This is a one-time operation. Run after ingestion or periodically.
        """
        logger.info(f"Building BM25 index for collection: {collection_name}")

        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Failed to get collection: {e}")
            raise

        # Get all documents (this may take time for large collections)
        logger.info("Fetching all documents from ChromaDB...")
        all_data = collection.get(include=["documents", "metadatas"])

        self.documents = all_data["documents"]
        self.metadatas = all_data["metadatas"]
        self.doc_ids = all_data["ids"]

        logger.info(f"Retrieved {len(self.documents)} documents")

        # Tokenize all documents
        logger.info("Tokenizing documents...")
        tokenized_corpus = [self.tokenize(doc) for doc in self.documents]

        # Build BM25 index
        logger.info("Building BM25 index...")
        self.bm25_index = BM25Okapi(tokenized_corpus)

        logger.info(f"✓ BM25 index built with {len(self.documents)} documents")

    def save_index(self, filepath: str = None):
        """Save BM25 index to disk for fast loading"""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "bm25_index.pkl")

        logger.info(f"Saving BM25 index to {filepath}...")

        with open(filepath, 'wb') as f:
            pickle.dump({
                'bm25_index': self.bm25_index,
                'documents': self.documents,
                'metadatas': self.metadatas,
                'doc_ids': self.doc_ids
            }, f)

        # Get file size
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"✓ BM25 index saved ({size_mb:.1f} MB)")

    def load_index(self, filepath: str = None):
        """Load pre-built BM25 index from disk"""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "bm25_index.pkl")

        logger.info(f"Loading BM25 index from {filepath}...")

        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.bm25_index = data['bm25_index']
            self.documents = data['documents']
            self.metadatas = data['metadatas']
            self.doc_ids = data['doc_ids']

        logger.info(f"✓ BM25 index loaded ({len(self.documents)} docs)")

    def search(self, query: str, top_k: int = 5, technology_filter: str = None) -> List[Dict[str, Any]]:
        """
        Search BM25 index for keyword matches.

        Returns: List of results with scores, sorted by BM25 relevance
        """
        if not self.bm25_index:
            raise ValueError("BM25 index not loaded. Call build_index() or load_index() first.")

        # Tokenize query
        tokenized_query = self.tokenize(query)

        if not tokenized_query:
            logger.warning(f"Query '{query}' produced no tokens after tokenization")
            return []

        # Get BM25 scores for all documents
        scores = self.bm25_index.get_scores(tokenized_query)

        # Create results with metadata
        results = []
        for idx, score in enumerate(scores):
            if score > 0:  # Only include documents with non-zero scores
                metadata = self.metadatas[idx]

                # Apply technology filter
                if technology_filter and metadata.get("technology") != technology_filter:
                    continue

                results.append({
                    "doc_id": self.doc_ids[idx],
                    "content": self.documents[idx],
                    "bm25_score": float(score),
                    "technology": metadata.get("technology", "Unknown"),
                    "source_url": metadata.get("source_url", ""),
                    "source_file": metadata.get("source_file", "")
                })

        # Sort by BM25 score (descending) and return top_k
        results.sort(key=lambda x: x["bm25_score"], reverse=True)
        return results[:top_k]


def main():
    """Build and save BM25 index"""
    logger.info("=" * 60)
    logger.info("BM25 Index Builder for RAG System")
    logger.info("=" * 60)

    # Check ChromaDB is accessible
    try:
        indexer = BM25Indexer()

        # Build index
        indexer.build_index()

        # Save to disk
        indexer.save_index()

        # Test the index
        logger.info("\n" + "=" * 60)
        logger.info("Testing BM25 Index")
        logger.info("=" * 60)

        test_queries = [
            "React hooks useState",
            "Python async await",
            "PostgreSQL connection pooling"
        ]

        for query in test_queries:
            logger.info(f"\nTest query: '{query}'")
            results = indexer.search(query, top_k=3)
            logger.info(f"  Found {len(results)} results")
            if results:
                logger.info(f"  Top result: {results[0]['technology']} (score: {results[0]['bm25_score']:.2f})")

        logger.info("\n" + "=" * 60)
        logger.info("✓ BM25 index created successfully!")
        logger.info("=" * 60)
        logger.info(f"Index location: {os.path.dirname(__file__)}/bm25_index.pkl")
        logger.info(f"Total documents: {len(indexer.documents)}")
        logger.info("\nNext steps:")
        logger.info("1. Integrate hybrid_search tool into MCP server")
        logger.info("2. Test hybrid search queries")
        logger.info("3. Rebuild index after adding new data sources")

        return 0

    except Exception as e:
        logger.error(f"Failed to build BM25 index: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
