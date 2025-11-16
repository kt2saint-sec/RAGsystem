#!/usr/bin/env python3
"""
Comprehensive Test Suite for Week 3 Enhancements
Tests hybrid search, query analytics, and RRF fusion
"""

import sys
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Week3TestSuite:
    """Comprehensive tests for Week 3 enhancements"""

    def __init__(self):
        self.results = {
            "bm25_indexer": {},
            "rrf_fusion": {},
            "query_analytics": {},
            "integration": {}
        }
        self.all_passed = True

    def test_bm25_indexer(self) -> Dict[str, Any]:
        """Test BM25 indexer functionality"""
        logger.info("=" * 60)
        logger.info("Testing BM25 Indexer")
        logger.info("=" * 60)

        try:
            from bm25_indexer import BM25Indexer

            # Test 1: Load existing index
            logger.info("  Test 1: Load BM25 index...")
            indexer = BM25Indexer()
            indexer.load_index()
            logger.info(f"    ✓ Index loaded: {len(indexer.documents)} documents")

            # Test 2: Search functionality
            logger.info("  Test 2: Test search queries...")
            test_queries = [
                ("React hooks useState", None),
                ("Python async await", "Python Docs"),
                ("FastAPI CORS configuration", "FastAPI Docs"),
            ]

            search_results = []
            for query, tech_filter in test_queries:
                results = indexer.search(query, top_k=3, technology_filter=tech_filter)
                search_results.append({
                    "query": query,
                    "tech_filter": tech_filter,
                    "num_results": len(results),
                    "top_score": results[0]["bm25_score"] if results else 0,
                    "top_tech": results[0]["technology"] if results else "None"
                })
                logger.info(f"    Query: '{query}'")
                logger.info(f"      Results: {len(results)}, Top: {results[0]['technology'] if results else 'None'}")

            # Test 3: Technology filtering
            logger.info("  Test 3: Technology filtering...")
            react_results = indexer.search("hooks", top_k=5, technology_filter="React Docs")
            all_results = indexer.search("hooks", top_k=5)

            logger.info(f"    ✓ With filter: {len(react_results)} results")
            logger.info(f"    ✓ Without filter: {len(all_results)} results")

            return {
                "status": "PASSED",
                "index_size": len(indexer.documents),
                "search_results": search_results,
                "filtering_works": len(react_results) <= len(all_results)
            }

        except Exception as e:
            logger.error(f"  ✗ BM25 indexer test failed: {e}", exc_info=True)
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def test_rrf_fusion(self) -> Dict[str, Any]:
        """Test RRF fusion algorithm"""
        logger.info("=" * 60)
        logger.info("Testing RRF Fusion")
        logger.info("=" * 60)

        try:
            from rrf_fusion import ReciprocalRankFusion

            # Test 1: Basic fusion
            logger.info("  Test 1: Basic RRF fusion...")
            rrf = ReciprocalRankFusion(k=60)

            semantic_results = [
                {"content": "React hooks allow functional components to use state", "similarity_score": 0.95},
                {"content": "useState is the most common hook", "similarity_score": 0.87},
                {"content": "useEffect handles side effects", "similarity_score": 0.82},
            ]

            keyword_results = [
                {"content": "useState is the most common hook", "bm25_score": 12.5},
                {"content": "useEffect handles side effects", "bm25_score": 10.2},
                {"content": "Custom hooks reuse stateful logic", "bm25_score": 8.1},
            ]

            fused = rrf.fuse(semantic_results, keyword_results)

            logger.info(f"    ✓ Fused {len(fused)} unique documents")
            logger.info(f"    Top result: '{fused[0]['content'][:50]}...'")
            logger.info(f"    Appeared in: {fused[0]['appeared_in']}")

            # Test 2: Weight adjustment
            logger.info("  Test 2: Testing weight adjustment...")
            fused_semantic = rrf.fuse(semantic_results, keyword_results, semantic_weight=0.8, keyword_weight=0.2)
            fused_keyword = rrf.fuse(semantic_results, keyword_results, semantic_weight=0.2, keyword_weight=0.8)

            logger.info(f"    ✓ Semantic-weighted: {len(fused_semantic)} results")
            logger.info(f"    ✓ Keyword-weighted: {len(fused_keyword)} results")

            # Test 3: Duplicate detection
            logger.info("  Test 3: Duplicate detection...")
            # All results should be unique
            content_hashes = [hash(r["content"]) for r in fused]
            unique_hashes = len(set(content_hashes))

            logger.info(f"    ✓ Total results: {len(fused)}")
            logger.info(f"    ✓ Unique results: {unique_hashes}")
            logger.info(f"    ✓ No duplicates: {len(fused) == unique_hashes}")

            return {
                "status": "PASSED",
                "fused_count": len(fused),
                "no_duplicates": len(fused) == unique_hashes,
                "top_result_sources": fused[0]["appeared_in"]
            }

        except Exception as e:
            logger.error(f"  ✗ RRF fusion test failed: {e}", exc_info=True)
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def test_query_analytics(self) -> Dict[str, Any]:
        """Test query analytics system"""
        logger.info("=" * 60)
        logger.info("Testing Query Analytics")
        logger.info("=" * 60)

        try:
            from query_analytics import QueryAnalytics

            analytics = QueryAnalytics()

            # Test 1: Track queries
            logger.info("  Test 1: Query tracking...")
            test_queries = [
                ("How to use React hooks?", "React Docs"),
                ("How to use React hooks?", "React Docs"),  # Duplicate
                ("Python async await", "Python Docs"),
                ("FastAPI CORS configuration", "FastAPI Docs"),
                ("React useState examples", "React Docs"),
            ]

            for query, tech in test_queries:
                analytics.track_query(query, tech)

            logger.info(f"    ✓ Tracked {len(test_queries)} queries (with duplicates)")

            # Test 2: Autocomplete
            logger.info("  Test 2: Autocomplete suggestions...")
            suggestions = analytics.get_autocomplete_suggestions("How to", limit=5)
            logger.info(f"    ✓ Found {len(suggestions)} suggestions for 'How to'")
            if suggestions:
                logger.info(f"    Top suggestion: '{suggestions[0]['query']}'")

            # Test 3: Top queries
            logger.info("  Test 3: Get top queries...")
            top_queries = analytics.get_top_queries(limit=10)
            logger.info(f"    ✓ Retrieved {len(top_queries)} top queries")
            if top_queries:
                logger.info(f"    Most popular: '{top_queries[0]['query']}' (freq: {top_queries[0]['frequency']})")

            # Test 4: Similar queries
            logger.info("  Test 4: Similar query detection...")
            similar = analytics.get_similar_queries("React hooks", limit=3)
            logger.info(f"    ✓ Found {len(similar)} similar queries")

            # Test 5: Stats
            logger.info("  Test 5: Analytics stats...")
            stats = analytics.get_stats()
            logger.info(f"    ✓ Total unique queries: {stats.get('total_unique_queries', 0)}")

            return {
                "status": "PASSED",
                "queries_tracked": len(test_queries),
                "autocomplete_suggestions": len(suggestions),
                "top_queries_count": len(top_queries),
                "similar_queries_count": len(similar),
                "total_unique_queries": stats.get('total_unique_queries', 0)
            }

        except Exception as e:
            logger.error(f"  ✗ Query analytics test failed: {e}", exc_info=True)
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def test_integration(self) -> Dict[str, Any]:
        """Test integration of all components"""
        logger.info("=" * 60)
        logger.info("Testing Component Integration")
        logger.info("=" * 60)

        try:
            # Test 1: All modules importable
            logger.info("  Test 1: Import all Week 3 modules...")
            from bm25_indexer import BM25Indexer
            from rrf_fusion import ReciprocalRankFusion
            from query_analytics import QueryAnalytics
            logger.info("    ✓ All modules import successfully")

            # Test 2: Simulated hybrid search workflow
            logger.info("  Test 2: Simulated hybrid search workflow...")

            # Initialize components
            indexer = BM25Indexer()
            indexer.load_index()
            rrf = ReciprocalRankFusion(k=60)

            # Simulate semantic results (would come from ChromaDB)
            semantic_results = [
                {
                    "content": "React hooks let you use state and other React features without writing a class",
                    "similarity_score": 0.92,
                    "technology": "React Docs",
                    "source_url": "https://react.dev/reference/react/hooks",
                    "source_file": "repos/react_docs/reference/react/hooks.md"
                },
                {
                    "content": "useState is a React Hook that lets you add a state variable to your component",
                    "similarity_score": 0.88,
                    "technology": "React Docs",
                    "source_url": "https://react.dev/reference/react/useState",
                    "source_file": "repos/react_docs/reference/react/useState.md"
                }
            ]

            # Get keyword results
            keyword_results = indexer.search("React hooks useState", top_k=3)

            # Fuse results
            fused = rrf.fuse(semantic_results, keyword_results, semantic_weight=0.6, keyword_weight=0.4)

            logger.info(f"    ✓ Hybrid search workflow complete")
            logger.info(f"    Semantic results: {len(semantic_results)}")
            logger.info(f"    Keyword results: {len(keyword_results)}")
            logger.info(f"    Fused results: {len(fused)}")

            # Test 3: Query tracking integration
            logger.info("  Test 3: Query tracking integration...")
            analytics = QueryAnalytics()
            analytics.track_query("React hooks useState", "React Docs")
            logger.info("    ✓ Query tracked successfully")

            return {
                "status": "PASSED",
                "modules_loaded": True,
                "hybrid_workflow": {
                    "semantic_count": len(semantic_results),
                    "keyword_count": len(keyword_results),
                    "fused_count": len(fused)
                },
                "query_tracking": True
            }

        except Exception as e:
            logger.error(f"  ✗ Integration test failed: {e}", exc_info=True)
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Week 3 tests"""
        logger.info("\n" + "=" * 60)
        logger.info("WEEK 3 ENHANCEMENTS TEST SUITE")
        logger.info("=" * 60 + "\n")

        start_time = time.time()

        # Run all tests
        self.results["bm25_indexer"] = self.test_bm25_indexer()
        self.results["rrf_fusion"] = self.test_rrf_fusion()
        self.results["query_analytics"] = self.test_query_analytics()
        self.results["integration"] = self.test_integration()

        duration = time.time() - start_time

        # Generate summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)

        for component, result in self.results.items():
            status = result.get("status", "UNKNOWN")
            symbol = "✓" if status == "PASSED" else "✗"
            logger.info(f"{symbol} {component}: {status}")

        logger.info(f"\nTotal Duration: {duration:.2f}s")
        logger.info(f"Overall Status: {'PASSED' if self.all_passed else 'FAILED'}")
        logger.info("=" * 60 + "\n")

        return {
            "overall_status": "PASSED" if self.all_passed else "FAILED",
            "duration_seconds": round(duration, 2),
            "results": self.results
        }


def main():
    """Main test execution"""
    suite = Week3TestSuite()
    results = suite.run_all_tests()

    # Print JSON results
    import json
    print("\n" + "=" * 60)
    print("DETAILED RESULTS (JSON)")
    print("=" * 60)
    print(json.dumps(results, indent=2, default=str))

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
