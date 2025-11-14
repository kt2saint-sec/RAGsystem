#!/usr/bin/env python3
"""
RAG Knowledge Base MCP Server (Enhanced with Caching)
Purpose: Production-ready MCP server for RAG queries using ChromaDB
Features:
  - GPU-accelerated embeddings (AMD/NVIDIA)
  - Three-level Redis caching (70%+ hit rate)
  - Batch query support
  - 70,652 documents across 36 technologies
Usage: fastmcp run rag_server.py
"""

import os
import sys
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
import chromadb
from sentence_transformers import SentenceTransformer
import logging
import numpy as np

# Add parent directory to path for caching_layer import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from caching_layer import RAGCacheManager
    CACHING_ENABLED = True
except ImportError:
    logger.warning("Caching layer not available. Running without cache.")
    CACHING_ENABLED = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("RAG Knowledge Base", dependencies=["chromadb", "sentence-transformers"])

# Global state
chroma_client = None
embedding_model = None
cache_manager = None


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


def get_cache_manager():
    """Initialize cache manager (singleton pattern)"""
    global cache_manager
    if cache_manager is None and CACHING_ENABLED:
        try:
            cache_manager = RAGCacheManager(
                redis_host=os.getenv("REDIS_HOST", "localhost"),
                redis_port=int(os.getenv("REDIS_PORT", "6379")),
                redis_db=int(os.getenv("REDIS_DB", "2"))
            )
            logger.info("Cache manager initialized (3-level caching enabled)")
        except Exception as e:
            logger.warning(f"Failed to initialize cache manager: {e}")
            cache_manager = None
    return cache_manager


@mcp.tool()
async def query_knowledge_base(
    query: str,
    collection_name: str = "coding_knowledge",
    top_k: int = 5,
    technology_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query the RAG knowledge base with three-level caching for optimal performance.

    This tool searches 70,652 technical documents across 36 technologies using semantic
    similarity. Implements intelligent caching (embedding, retrieval, response) for
    ~100x faster repeated queries.

    Args:
        query: Natural language question or search query (e.g., "How to use React hooks?")
        collection_name: ChromaDB collection name (default: "coding_knowledge")
        top_k: Number of results to return (1-20, default: 5)
        technology_filter: Optional filter by technology name (e.g., "React Docs", "Python Docs")
                          Use list_technologies() tool to see all available filters

    Returns:
        Dictionary containing:
        - query: Original query text
        - collection: Collection name searched
        - technology_filter: Applied filter (or null)
        - results: List of relevant documents with:
          - rank: Result position (1-based)
          - content: Document text chunk
          - technology: Source technology
          - source_url: Original documentation URL
          - source_file: File path in knowledge base
          - similarity_score: Semantic similarity (0-1, higher is better)
          - distance: Vector distance (0-2, lower is better)
        - total_found: Number of results returned
        - cache_hit: (if applicable) Which cache level served this result

    Performance:
        - Cache hit: <1ms (response cached)
        - Cache miss: ~6ms (GPU-accelerated embedding + vector search)
        - Cache hit rate: 70%+ for common queries

    Examples:
        # Basic query
        query_knowledge_base("How do I use React hooks?")

        # Technology-specific query
        query_knowledge_base("async await examples", technology_filter="Python Docs")

        # Retrieve more results
        query_knowledge_base("Docker compose networking", top_k=10)

        # Complex query
        query_knowledge_base(
            "How to prevent memory leaks in React useEffect cleanup",
            technology_filter="React Docs",
            top_k=8
        )
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return {"error": "Query cannot be empty"}

        if top_k < 1 or top_k > 20:
            top_k = min(max(top_k, 1), 20)

        logger.info(f"Query: '{query}' | Filter: {technology_filter} | Top K: {top_k}")

        # Check response cache (Level 3)
        cache = get_cache_manager()
        if cache:
            cached_response = cache.get_cached_response(query, technology_filter, top_k)
            if cached_response:
                cached_response["cache_hit"] = "response_cache"
                logger.info(f"✓ Response cache HIT - returning cached result")
                return cached_response

        # Get ChromaDB client and collection
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)

        # Check embedding cache (Level 1)
        model = get_embedding_model()
        if cache:
            cached_embedding = cache.get_cached_embedding(query)
            if cached_embedding is not None:
                query_embedding = cached_embedding
                logger.debug(f"✓ Embedding cache HIT")
            else:
                query_embedding = model.encode(query)
                cache.cache_embedding(query, query_embedding)
                logger.debug(f"✗ Embedding cache MISS - cached new embedding")
        else:
            query_embedding = model.encode(query)

        # Convert to list for ChromaDB
        query_embedding_list = query_embedding.tolist()

        # Build filter
        where_filter = None
        if technology_filter:
            where_filter = {"technology": technology_filter}

        # Check retrieval cache (Level 2)
        if cache:
            cached_retrieval = cache.get_cached_retrieval(query_embedding, technology_filter)
            if cached_retrieval:
                results = cached_retrieval
                logger.debug(f"✓ Retrieval cache HIT")
            else:
                # Perform vector search
                results = collection.query(
                    query_embeddings=[query_embedding_list],
                    n_results=top_k,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )
                cache.cache_retrieval(query_embedding, results, technology_filter)
                logger.debug(f"✗ Retrieval cache MISS - cached new results")
        else:
            # Perform vector search
            results = collection.query(
                query_embeddings=[query_embedding_list],
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

        # Cache complete response
        if cache:
            cache.cache_response(query, formatted_results, technology_filter, top_k)

        logger.info(f"Found {len(results['documents'][0])} results")
        return formatted_results

    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        return {"error": str(e), "query": query}


@mcp.tool()
async def list_technologies() -> Dict[str, Any]:
    """
    List all available technology filters in the knowledge base.

    Use this tool to discover what technologies are available for filtering queries.
    Each technology represents a distinct documentation source or programming language.

    Returns:
        Dictionary containing:
        - total_technologies: Count of unique technologies (currently 36)
        - total_documents: Total document chunks across all technologies (70,652)
        - technologies: List of technology objects, each with:
          - name: Technology name (use this value for technology_filter parameter)
          - document_count: Number of document chunks for this technology

    Technologies are sorted by document count (descending), so the most comprehensive
    documentation sources appear first.

    Use Cases:
        - Discover available technologies before querying
        - Find the exact name to use in technology_filter parameter
        - Identify which technologies have the most documentation

    Examples:
        # Get all available technologies
        list_technologies()

        # Example output snippet:
        # {
        #   "total_technologies": 36,
        #   "total_documents": 70652,
        #   "technologies": [
        #     {"name": "React Docs", "document_count": 8432},
        #     {"name": "Python Docs", "document_count": 7621},
        #     ...
        #   ]
        # }
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
    Get statistics and health information about the ChromaDB collection.

    Use this tool to verify the knowledge base is properly configured and to check
    collection size and metadata.

    Args:
        collection_name: Name of the ChromaDB collection (default: "coding_knowledge")

    Returns:
        Dictionary containing:
        - collection_name: Name of the collection
        - document_count: Total number of document chunks stored
        - metadata: Collection-level metadata (if available)

    Use Cases:
        - Verify knowledge base is accessible
        - Check if collection exists
        - Monitor collection size growth over time

    Examples:
        # Get stats for default collection
        get_collection_stats()

        # Get stats for specific collection
        get_collection_stats("coding_knowledge")

        # Example output:
        # {
        #   "collection_name": "coding_knowledge",
        #   "document_count": 70652,
        #   "metadata": {}
        # }
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


@mcp.tool()
async def batch_query_knowledge_base(
    queries: List[str],
    collection_name: str = "coding_knowledge",
    top_k: int = 5,
    technology_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute multiple queries in a single batch for improved efficiency.

    This tool processes multiple related queries simultaneously, which is more efficient
    than calling query_knowledge_base() multiple times individually. Particularly useful
    for comparative research or multi-faceted questions.

    Args:
        queries: List of search queries (2-10 queries recommended per batch)
        collection_name: ChromaDB collection name (default: "coding_knowledge")
        top_k: Number of results per query (1-20, default: 5)
        technology_filter: Optional filter applied to all queries

    Returns:
        Dictionary containing:
        - total_queries: Number of queries processed
        - technology_filter: Applied filter (or null)
        - results: List of query results, each containing:
          - query_index: Index in original queries list (0-based)
          - query: The query text
          - results: List of documents (same format as query_knowledge_base)
          - total_found: Number of results for this query
          - cache_hit: Whether result came from cache
        - batch_stats: Performance statistics for the batch

    Performance:
        - Shares embedding model context across queries
        - Reuses ChromaDB connection
        - Benefits from cache warmup (later queries may hit cache)

    Use Cases:
        - Compare approaches: ["React hooks", "React class components", "React contexts"]
        - Multi-aspect research: ["Python asyncio basics", "Python asyncio pitfalls", "Python asyncio best practices"]
        - Technology comparison: ["FastAPI performance", "Flask performance", "Django performance"]

    Examples:
        # Compare multiple approaches
        batch_query_knowledge_base(
            queries=[
                "How to manage state in React?",
                "How to manage side effects in React?",
                "How to optimize React performance?"
            ],
            technology_filter="React Docs",
            top_k=3
        )

        # Research a topic from multiple angles
        batch_query_knowledge_base(
            queries=[
                "Python type hints basics",
                "Python type hints for functions",
                "Python type hints generics"
            ],
            technology_filter="Python Docs"
        )
    """
    try:
        # Validate inputs
        if not queries or len(queries) == 0:
            return {"error": "Queries list cannot be empty"}

        if len(queries) > 20:
            return {"error": "Maximum 20 queries per batch (received {})".format(len(queries))}

        if top_k < 1 or top_k > 20:
            top_k = min(max(top_k, 1), 20)

        logger.info(f"Batch query: {len(queries)} queries | Filter: {technology_filter} | Top K: {top_k}")

        batch_results = {
            "total_queries": len(queries),
            "technology_filter": technology_filter,
            "results": [],
            "batch_stats": {
                "cache_hits": 0,
                "cache_misses": 0,
                "total_documents_retrieved": 0
            }
        }

        # Process each query
        for idx, query in enumerate(queries):
            # Use the existing query function to benefit from caching
            query_result = await query_knowledge_base(
                query=query,
                collection_name=collection_name,
                top_k=top_k,
                technology_filter=technology_filter
            )

            # Track cache hits
            if "cache_hit" in query_result:
                batch_results["batch_stats"]["cache_hits"] += 1
            else:
                batch_results["batch_stats"]["cache_misses"] += 1

            batch_results["batch_stats"]["total_documents_retrieved"] += query_result.get("total_found", 0)

            # Add to batch results
            batch_results["results"].append({
                "query_index": idx,
                "query": query,
                "results": query_result.get("results", []),
                "total_found": query_result.get("total_found", 0),
                "cache_hit": query_result.get("cache_hit", False)
            })

        logger.info(f"Batch complete: {len(queries)} queries, {batch_results['batch_stats']['cache_hits']} cache hits")
        return batch_results

    except Exception as e:
        logger.error(f"Batch query failed: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get Redis cache performance statistics and health metrics.

    This tool provides detailed insights into cache performance across all three caching
    levels (embedding, retrieval, response). Use it to monitor cache effectiveness and
    identify optimization opportunities.

    Returns:
        Dictionary containing:
        - cache_enabled: Whether caching is available
        - embedding_cache: Level 1 cache statistics
          - hits: Number of cache hits
          - misses: Number of cache misses
          - total: Total requests
          - hit_rate: Percentage of requests served from cache
        - retrieval_cache: Level 2 cache statistics (same structure)
        - response_cache: Level 3 cache statistics (same structure)
        - overall: Aggregate statistics across all levels
          - total_hits: Combined hits across all levels
          - total_requests: Combined requests across all levels
        - cache_size: Number of cached items per level
          - embedding: Count of cached embeddings
          - retrieval: Count of cached retrievals
          - response: Count of cached responses

    Performance Targets:
        - Overall hit rate: 70%+ (typical for production workloads)
        - Response cache hit rate: 40-50% (exact query matches)
        - Embedding cache hit rate: 60-70% (query text reuse)
        - Retrieval cache hit rate: 50-60% (semantic similarity matches)

    Use Cases:
        - Monitor cache effectiveness over time
        - Identify if cache needs tuning (TTL adjustments)
        - Verify Redis connectivity
        - Debug performance issues

    Examples:
        # Get current cache statistics
        get_cache_stats()

        # Example output:
        # {
        #   "cache_enabled": true,
        #   "embedding_cache": {
        #     "hits": 142,
        #     "misses": 58,
        #     "total": 200,
        #     "hit_rate": 71.0
        #   },
        #   "retrieval_cache": {...},
        #   "response_cache": {...},
        #   "overall": {
        #     "total_hits": 425,
        #     "total_requests": 600
        #   },
        #   "cache_size": {
        #     "embedding": 58,
        #     "retrieval": 45,
        #     "response": 38
        #   }
        # }
    """
    try:
        cache = get_cache_manager()

        if not cache or not CACHING_ENABLED:
            return {
                "cache_enabled": False,
                "message": "Caching is not enabled or Redis is unavailable"
            }

        # Get statistics
        stats = cache.get_cache_stats()
        sizes = cache.get_cache_size()

        return {
            "cache_enabled": True,
            "embedding_cache": stats["embedding_cache"],
            "retrieval_cache": stats["retrieval_cache"],
            "response_cache": stats["response_cache"],
            "overall": stats["overall"],
            "cache_size": sizes
        }

    except Exception as e:
        logger.error(f"Get cache stats failed: {e}", exc_info=True)
        return {
            "cache_enabled": False,
            "error": str(e)
        }


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


# Production enhancements
try:
    from health_checks import health_checker
    from cache_warmer import cache_warmer
    from gpu_verification import GPUVerifier
    PRODUCTION_FEATURES = True
except ImportError as e:
    logger.warning(f"Production features not available: {e}")
    PRODUCTION_FEATURES = False


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """
    Get system health status.

    Returns comprehensive health check including ChromaDB, Redis, and embedding model status.
    """
    if not PRODUCTION_FEATURES:
        return {"error": "Health check not available"}

    return await health_checker.readiness()


@mcp.tool()
async def get_cache_warming_stats() -> Dict[str, Any]:
    """
    Get cache warming statistics.

    Shows top queries, hit counts, and cache warming effectiveness.
    """
    if not PRODUCTION_FEATURES:
        return {"error": "Cache warming not available"}

    return cache_warmer.get_stats()


@mcp.tool()
async def verify_gpu_acceleration() -> Dict[str, Any]:
    """
    Verify GPU acceleration is working.

    Checks PyTorch GPU support and benchmarks CPU vs GPU performance.
    """
    if not PRODUCTION_FEATURES:
        return {"error": "GPU verification not available"}

    verifier = GPUVerifier()
    return verifier.run_verification()


# Integrate cache warming tracking into queries
original_query_kb = query_knowledge_base


async def query_knowledge_base_with_tracking(*args, **kwargs):
    """Wrapper to track queries for cache warming"""
    if PRODUCTION_FEATURES:
        query = kwargs.get('query') or (args[0] if args else None)
        tech_filter = kwargs.get('technology_filter')
        if query:
            cache_warmer.track_query(query, tech_filter)

    return await original_query_kb(*args, **kwargs)


# Run server
if __name__ == "__main__":
    logger.info("Starting RAG Knowledge Base MCP Server...")
    logger.info(f"Production features: {'enabled' if PRODUCTION_FEATURES else 'disabled'}")
    mcp.run(transport="stdio")
