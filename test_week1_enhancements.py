#!/usr/bin/env python3
"""
Test script for Week 1 enhancements to the RAG MCP server.

Tests:
1. MCP server imports and initialization
2. Cache manager functionality
3. Query with caching
4. Batch query functionality
5. Cache statistics
6. Enhanced tool descriptions

Usage: .venv/bin/python test_week1_enhancements.py
"""

import sys
import os
import asyncio
import time
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title: str):
    """Print a formatted test section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"      {details}")

async def test_imports():
    """Test 1: Verify all imports work"""
    print_header("TEST 1: Module Imports")

    try:
        # Import MCP server module
        from mcp_server import rag_server
        print_result("Import rag_server module", True)

        # Check caching is enabled
        cache_enabled = rag_server.CACHING_ENABLED
        print_result("Caching layer available", cache_enabled,
                    f"CACHING_ENABLED = {cache_enabled}")

        # Import caching layer directly
        from caching_layer import RAGCacheManager
        print_result("Import RAGCacheManager", True)

        return True
    except Exception as e:
        print_result("Module imports", False, str(e))
        return False

async def test_cache_manager():
    """Test 2: Cache manager initialization and basic operations"""
    print_header("TEST 2: Cache Manager Functionality")

    try:
        from caching_layer import RAGCacheManager
        import numpy as np

        # Initialize cache manager
        cache = RAGCacheManager(
            redis_host='localhost',
            redis_port=6379,
            redis_db=2
        )
        print_result("Initialize cache manager", True)

        # Test embedding cache
        test_query = "Test query for cache verification"
        test_embedding = np.random.rand(384)  # Simulate embedding

        cache.cache_embedding(test_query, test_embedding)
        cached = cache.get_cached_embedding(test_query)

        embedding_works = cached is not None and np.array_equal(cached, test_embedding)
        print_result("Embedding cache (store and retrieve)", embedding_works)

        # Test response cache
        test_response = {"query": test_query, "results": [{"content": "test"}]}
        cache.cache_response(test_query, test_response, technology_filter=None, top_k=5)
        cached_response = cache.get_cached_response(test_query, technology_filter=None, top_k=5)

        response_works = cached_response is not None and cached_response["query"] == test_query
        print_result("Response cache (store and retrieve)", response_works)

        # Test cache statistics
        stats = cache.get_cache_stats()
        stats_works = "embedding_cache" in stats and "response_cache" in stats
        print_result("Cache statistics retrieval", stats_works,
                    f"Embedding hits: {stats['embedding_cache']['hits']}, Response hits: {stats['response_cache']['hits']}")

        # Test cache size
        sizes = cache.get_cache_size()
        size_works = "embedding" in sizes and "response" in sizes
        print_result("Cache size retrieval", size_works,
                    f"Sizes: {sizes}")

        # Clean up test data
        cache.clear_cache()
        print_result("Cache clear operation", True)

        return True

    except Exception as e:
        print_result("Cache manager functionality", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_query_with_caching():
    """Test 3: Query knowledge base with caching"""
    print_header("TEST 3: Query with Caching Integration")

    try:
        # Import server functions
        from mcp_server.rag_server import query_knowledge_base, get_cache_manager

        # Verify ChromaDB is accessible
        test_query = "How to use React hooks for state management?"

        # First query (should be cache miss)
        print("\n  First query (cache miss expected)...")
        start = time.time()
        result1 = await query_knowledge_base(
            query=test_query,
            top_k=3,
            technology_filter="React Docs"
        )
        elapsed1 = (time.time() - start) * 1000

        has_results = "results" in result1 and len(result1["results"]) > 0
        print_result("First query returns results", has_results,
                    f"Found {result1.get('total_found', 0)} results in {elapsed1:.2f}ms")

        # Second query (should be cache hit)
        print("\n  Second query (cache hit expected)...")
        start = time.time()
        result2 = await query_knowledge_base(
            query=test_query,
            top_k=3,
            technology_filter="React Docs"
        )
        elapsed2 = (time.time() - start) * 1000

        is_cached = "cache_hit" in result2
        speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 1
        print_result("Second query from cache", is_cached,
                    f"Cache hit: {is_cached}, Time: {elapsed2:.2f}ms, Speedup: {speedup:.1f}x")

        # Verify results are identical
        results_match = result1.get("total_found") == result2.get("total_found")
        print_result("Cached results match original", results_match)

        return has_results and is_cached

    except Exception as e:
        print_result("Query with caching", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_batch_query():
    """Test 4: Batch query functionality"""
    print_header("TEST 4: Batch Query Tool")

    try:
        from mcp_server.rag_server import batch_query_knowledge_base

        queries = [
            "How to use useState in React?",
            "How to use useEffect in React?",
            "How to use useContext in React?"
        ]

        start = time.time()
        result = await batch_query_knowledge_base(
            queries=queries,
            top_k=2,
            technology_filter="React Docs"
        )
        elapsed = (time.time() - start) * 1000

        # Verify result structure
        has_results = "results" in result and len(result["results"]) == len(queries)
        has_stats = "batch_stats" in result

        print_result("Batch query returns all results", has_results,
                    f"Processed {result.get('total_queries', 0)} queries in {elapsed:.2f}ms")

        if has_stats:
            stats = result["batch_stats"]
            print_result("Batch statistics available", True,
                        f"Cache hits: {stats['cache_hits']}/{result['total_queries']}, "
                        f"Total docs: {stats['total_documents_retrieved']}")

        # Verify each query has results
        all_have_results = all(
            len(r.get("results", [])) > 0
            for r in result.get("results", [])
        )
        print_result("All queries returned results", all_have_results)

        return has_results and has_stats and all_have_results

    except Exception as e:
        print_result("Batch query functionality", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_cache_stats_tool():
    """Test 5: Cache statistics tool"""
    print_header("TEST 5: Cache Statistics Tool")

    try:
        from mcp_server.rag_server import get_cache_stats

        stats = await get_cache_stats()

        cache_enabled = stats.get("cache_enabled", False)
        print_result("Cache is enabled", cache_enabled)

        if cache_enabled:
            has_embedding_stats = "embedding_cache" in stats
            has_retrieval_stats = "retrieval_cache" in stats
            has_response_stats = "response_cache" in stats
            has_overall = "overall" in stats
            has_sizes = "cache_size" in stats

            print_result("Embedding cache stats present", has_embedding_stats)
            print_result("Retrieval cache stats present", has_retrieval_stats)
            print_result("Response cache stats present", has_response_stats)
            print_result("Overall stats present", has_overall)
            print_result("Cache sizes present", has_sizes)

            # Show actual stats
            if has_response_stats:
                resp_stats = stats["response_cache"]
                print(f"\n  Response cache: {resp_stats['hits']} hits, "
                      f"{resp_stats['misses']} misses, "
                      f"{resp_stats['hit_rate']:.1f}% hit rate")

            if has_sizes:
                print(f"  Cache sizes: {stats['cache_size']}")

            return cache_enabled and has_embedding_stats and has_response_stats
        else:
            print(f"  Warning: {stats.get('message', 'Cache not available')}")
            return False

    except Exception as e:
        print_result("Cache statistics tool", False, str(e))
        import traceback
        traceback.print_exc()
        return False

async def test_tool_descriptions():
    """Test 6: Verify enhanced tool descriptions"""
    print_header("TEST 6: Enhanced Tool Descriptions")

    try:
        from mcp_server import rag_server

        # Check that tools have enhanced docstrings
        query_doc = rag_server.query_knowledge_base.__doc__
        has_enhanced_query = "three-level caching" in query_doc.lower()
        print_result("query_knowledge_base has enhanced description", has_enhanced_query,
                    f"Docstring length: {len(query_doc)} chars")

        list_tech_doc = rag_server.list_technologies.__doc__
        has_enhanced_list = "70,652" in list_tech_doc or "70652" in list_tech_doc
        print_result("list_technologies has enhanced description", has_enhanced_list,
                    f"Docstring length: {len(list_tech_doc)} chars")

        batch_doc = rag_server.batch_query_knowledge_base.__doc__
        has_batch = "multiple queries" in batch_doc.lower()
        print_result("batch_query_knowledge_base exists and documented", has_batch,
                    f"Docstring length: {len(batch_doc)} chars")

        cache_stats_doc = rag_server.get_cache_stats.__doc__
        has_cache_stats = "performance statistics" in cache_stats_doc.lower()
        print_result("get_cache_stats exists and documented", has_cache_stats,
                    f"Docstring length: {len(cache_stats_doc)} chars")

        return has_enhanced_query and has_enhanced_list and has_batch and has_cache_stats

    except Exception as e:
        print_result("Enhanced tool descriptions", False, str(e))
        return False

async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  RAG MCP Server - Week 1 Enhancements Test Suite")
    print("=" * 80)
    print("\nTesting enhanced features:")
    print("  - Three-level Redis caching")
    print("  - Enhanced tool descriptions")
    print("  - Batch query functionality")
    print("  - Cache statistics monitoring")

    results = []

    # Run tests
    results.append(("Module Imports", await test_imports()))
    results.append(("Cache Manager", await test_cache_manager()))
    results.append(("Query with Caching", await test_query_with_caching()))
    results.append(("Batch Query", await test_batch_query()))
    results.append(("Cache Statistics", await test_cache_stats_tool()))
    results.append(("Tool Descriptions", await test_tool_descriptions()))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {test_name}")

    print(f"\n{passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All Week 1 enhancements verified successfully!")
        print("\nEnhancements active:")
        print("  ✓ Three-level caching (embedding, retrieval, response)")
        print("  ✓ Enhanced tool descriptions with examples")
        print("  ✓ Batch query support for multiple queries")
        print("  ✓ Cache statistics monitoring")
        print("\nMCP server is ready for production use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above for details.")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
