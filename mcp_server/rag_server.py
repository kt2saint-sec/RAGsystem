#!/usr/bin/env python3
"""
RAG Knowledge Base MCP Server
Purpose: Production-ready MCP server for RAG queries using ChromaDB
Usage: fastmcp run rag_server.py
"""

import os
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
import chromadb
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("RAG Knowledge Base", dependencies=["chromadb", "sentence-transformers"])

# Global state
chroma_client = None
embedding_model = None


def get_chroma_client():
    """Initialize ChromaDB client (singleton pattern)"""
    global chroma_client
    if chroma_client is None:
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8001"))
        chroma_client = chromadb.HttpClient(host=host, port=port)
        logger.info(f"ChromaDB client initialized: {host}:{port}")
    return chroma_client


def get_embedding_model():
    """Load embedding model (cached) with GPU acceleration if available"""
    global embedding_model
    if embedding_model is None:
        import torch
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        embedding_model = SentenceTransformer(model_name)

        # Move to GPU if available
        if torch.cuda.is_available():
            embedding_model = embedding_model.to('cuda')
            logger.info(f"Embedding model loaded: {model_name} (GPU: {torch.cuda.get_device_name(0)})")
        else:
            logger.info(f"Embedding model loaded: {model_name} (CPU)")
    return embedding_model


@mcp.tool()
async def query_knowledge_base(
    query: str,
    collection_name: str = "coding_knowledge",
    top_k: int = 5,
    technology_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query the RAG knowledge base for relevant documentation.

    Args:
        query: The search query (natural language question)
        collection_name: ChromaDB collection to search (default: coding_knowledge)
        top_k: Number of results to return (default: 5, max: 20)
        technology_filter: Optional technology name to filter by (e.g., "React Docs", "Python Docs")

    Returns:
        Dictionary containing:
        - query: The original query
        - results: List of relevant documents with content, metadata, and scores
        - total_found: Number of results returned

    Examples:
        query_knowledge_base("How do I use React hooks?")
        query_knowledge_base("Python async await examples", technology_filter="Python Docs")
        query_knowledge_base("Docker compose networking", top_k=10)
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return {"error": "Query cannot be empty"}

        if top_k < 1 or top_k > 20:
            top_k = min(max(top_k, 1), 20)

        logger.info(f"Query: '{query}' | Filter: {technology_filter} | Top K: {top_k}")

        # Get ChromaDB client and collection
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)

        # Generate query embedding
        model = get_embedding_model()
        query_embedding = model.encode(query).tolist()

        # Build filter
        where_filter = None
        if technology_filter:
            where_filter = {"technology": technology_filter}

        # Perform vector search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = {
            "query": query,
            "collection": collection_name,
            "technology_filter": technology_filter,
            "results": [],
            "total_found": len(results["documents"][0])
        }

        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            formatted_results["results"].append({
                "rank": i + 1,
                "content": doc,
                "technology": metadata.get("technology", "Unknown"),
                "source_url": metadata.get("source_url", ""),
                "source_file": metadata.get("source_file", ""),
                "similarity_score": round(1 - distance, 4),
                "distance": round(distance, 4)
            })

        logger.info(f"Found {len(results['documents'][0])} results")
        return formatted_results

    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        return {"error": str(e), "query": query}


@mcp.tool()
async def list_technologies() -> Dict[str, Any]:
    """
    List all available technology filters in the knowledge base.

    Returns:
        Dictionary with:
        - total_technologies: Count of unique technologies
        - technologies: List of {name, document_count} sorted by count
        - total_documents: Total document count across all technologies

    Examples:
        list_technologies()
    """
    try:
        client = get_chroma_client()
        collection = client.get_collection(name="coding_knowledge")

        # Get all unique technologies
        all_metadata = collection.get(include=["metadatas"])
        technologies = {}

        for meta in all_metadata["metadatas"]:
            tech = meta.get("technology", "Unknown")
            technologies[tech] = technologies.get(tech, 0) + 1

        total_docs = sum(technologies.values())

        return {
            "total_technologies": len(technologies),
            "total_documents": total_docs,
            "technologies": [
                {"name": name, "document_count": count}
                for name, count in sorted(technologies.items(), key=lambda x: x[1], reverse=True)
            ]
        }
    except Exception as e:
        logger.error(f"List technologies failed: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
async def get_collection_stats(collection_name: str = "coding_knowledge") -> Dict[str, Any]:
    """
    Get statistics about a ChromaDB collection.

    Args:
        collection_name: Name of the collection (default: coding_knowledge)

    Returns:
        Dictionary with collection metadata and statistics

    Examples:
        get_collection_stats()
        get_collection_stats("coding_knowledge")
    """
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)

        return {
            "collection_name": collection.name,
            "document_count": collection.count(),
            "metadata": collection.metadata if hasattr(collection, 'metadata') else {}
        }
    except Exception as e:
        logger.error(f"Get collection stats failed: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.resource("config://embedding-model")
async def get_embedding_model_info() -> str:
    """Resource providing current embedding model information"""
    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    return f"Current embedding model: {model_name}\nDimensions: 384\nMax sequence length: 512"


@mcp.resource("config://chromadb-connection")
async def get_chromadb_info() -> str:
    """Resource providing ChromaDB connection information"""
    host = os.getenv("CHROMA_HOST", "localhost")
    port = os.getenv("CHROMA_PORT", "8001")
    return f"ChromaDB endpoint: http://{host}:{port}\nCollection: coding_knowledge"


@mcp.resource("config://available-technologies")
async def get_available_technologies() -> str:
    """Resource listing all available technology filters"""
    try:
        result = await list_technologies()
        if "error" in result:
            return f"Error: {result['error']}"

        tech_list = "\n".join([
            f"  - {tech['name']}: {tech['document_count']} documents"
            for tech in result["technologies"][:20]  # Top 20
        ])

        return f"Available Technologies ({result['total_technologies']} total):\n{tech_list}"
    except Exception as e:
        return f"Error loading technologies: {e}"


# Run server
if __name__ == "__main__":
    logger.info("Starting RAG Knowledge Base MCP Server...")
    mcp.run(transport="stdio")
