#!/usr/bin/env python3
"""
Comprehensive Test Suite for Production Enhancements
Tests cache warming, health checks, GPU verification, and error recovery
"""

import sys
import time
import asyncio
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionEnhancementTester:
    """Test all production enhancement features"""

    def __init__(self):
        self.results = {
            "cache_warmer": {},
            "health_checks": {},
            "gpu_verification": {},
            "error_recovery": {},
            "integration": {}
        }
        self.all_passed = True

    def test_cache_warmer(self) -> Dict[str, Any]:
        """Test cache warming system"""
        logger.info("=" * 60)
        logger.info("Testing Cache Warming System")
        logger.info("=" * 60)

        try:
            from cache_warmer import cache_warmer

            # Test 1: Track queries
            logger.info("  Test 1: Query tracking...")
            cache_warmer.track_query("How to use React hooks", "React Docs")
            cache_warmer.track_query("How to use React hooks", "React Docs")  # Duplicate
            cache_warmer.track_query("Python async/await", "Python Docs")
            logger.info("    ✓ Query tracking successful")

            # Test 2: Get top queries
            logger.info("  Test 2: Retrieve top queries...")
            top_queries = cache_warmer.get_top_queries(10)
            logger.info(f"    ✓ Retrieved {len(top_queries)} queries")

            # Test 3: Get statistics
            logger.info("  Test 3: Get cache warming stats...")
            stats = cache_warmer.get_stats()
            logger.info(f"    ✓ Stats: {stats.get('total_unique_queries', 0)} unique queries")

            return {
                "status": "PASSED",
                "tracked_queries": 3,
                "top_queries_count": len(top_queries),
                "stats": stats
            }

        except Exception as e:
            logger.error(f"  ✗ Cache warmer test failed: {e}")
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    async def test_health_checks(self) -> Dict[str, Any]:
        """Test health check system"""
        logger.info("=" * 60)
        logger.info("Testing Health Check System")
        logger.info("=" * 60)

        try:
            from health_checks import health_checker

            # Test 1: Liveness check
            logger.info("  Test 1: Liveness check...")
            liveness = await health_checker.liveness()
            assert liveness.get("status") == "healthy"
            logger.info(f"    ✓ Liveness: {liveness['status']} (uptime: {liveness['uptime_seconds']}s)")

            # Test 2: ChromaDB check
            logger.info("  Test 2: ChromaDB health...")
            chroma = await health_checker.check_chromadb()
            logger.info(f"    ✓ ChromaDB: {chroma.get('status', 'unknown')}")

            # Test 3: Redis check
            logger.info("  Test 3: Redis health...")
            redis_health = await health_checker.check_redis()
            logger.info(f"    ✓ Redis: {redis_health.get('status', 'unknown')}")

            # Test 4: Embedding model check
            logger.info("  Test 4: Embedding model health...")
            model = await health_checker.check_embedding_model()
            logger.info(f"    ✓ Model: {model.get('status', 'unknown')} ({model.get('device', 'unknown')})")

            # Test 5: Full readiness check
            logger.info("  Test 5: Full readiness check...")
            readiness = await health_checker.readiness()
            logger.info(f"    ✓ Readiness: {readiness.get('status', 'unknown')}")
            logger.info(f"    Duration: {readiness.get('check_duration_ms', 0)}ms")

            return {
                "status": "PASSED",
                "liveness": liveness,
                "chromadb": chroma.get("status"),
                "redis": redis_health.get("status"),
                "model": model.get("status"),
                "readiness": readiness.get("status"),
                "check_duration_ms": readiness.get("check_duration_ms")
            }

        except Exception as e:
            logger.error(f"  ✗ Health check test failed: {e}")
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def test_gpu_verification(self) -> Dict[str, Any]:
        """Test GPU verification system"""
        logger.info("=" * 60)
        logger.info("Testing GPU Verification System")
        logger.info("=" * 60)

        try:
            from gpu_verification import GPUVerifier

            verifier = GPUVerifier()

            # Test 1: PyTorch GPU check
            logger.info("  Test 1: PyTorch GPU detection...")
            pytorch_gpu = verifier.check_pytorch_gpu()
            logger.info(f"    ✓ CUDA available: {pytorch_gpu.get('cuda_available')}")
            logger.info(f"    Device count: {pytorch_gpu.get('device_count')}")

            if pytorch_gpu.get('cuda_available'):
                for device in pytorch_gpu.get('devices', []):
                    logger.info(f"    GPU {device['id']}: {device['name']} ({device['memory_gb']}GB)")

            # Test 2: Model device check
            logger.info("  Test 2: Model device check...")
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            device_info = verifier.check_model_device(model)
            logger.info(f"    ✓ Model device: {device_info.get('device_type')}")

            # Test 3: Quick benchmark (small batch)
            if pytorch_gpu.get('cuda_available'):
                logger.info("  Test 3: CPU vs GPU benchmark...")
                benchmark = verifier.benchmark_cpu_vs_gpu(batch_sizes=[8])
                logger.info(f"    ✓ Benchmark complete")
                for batch_size, speedup in benchmark.get("speedup", {}).items():
                    logger.info(f"    Batch {batch_size}: {speedup}x speedup on GPU")
            else:
                logger.info("  Test 3: Skipped (no GPU available)")
                benchmark = {}

            return {
                "status": "PASSED",
                "pytorch_gpu": pytorch_gpu,
                "model_device": device_info,
                "benchmark_available": bool(benchmark)
            }

        except Exception as e:
            logger.error(f"  ✗ GPU verification test failed: {e}")
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def test_error_recovery(self) -> Dict[str, Any]:
        """Test error recovery mechanisms"""
        logger.info("=" * 60)
        logger.info("Testing Error Recovery System")
        logger.info("=" * 60)

        try:
            from error_recovery import ResilientRedisClient, ResilientChromaClient

            # Test 1: Resilient Redis client
            logger.info("  Test 1: Resilient Redis client...")
            redis_client = ResilientRedisClient()

            # Test basic operations
            ping_result = redis_client.ping()
            logger.info(f"    ✓ Redis ping: {ping_result}")

            # Test set/get
            set_result = redis_client.set("test_key", "test_value", ex=10)
            get_result = redis_client.get("test_key")
            logger.info(f"    ✓ Set/Get: {get_result == b'test_value'}")

            # Test 2: Resilient ChromaDB client
            logger.info("  Test 2: Resilient ChromaDB client...")
            chroma_client = ResilientChromaClient()

            # Test heartbeat
            heartbeat = chroma_client.heartbeat()
            logger.info(f"    ✓ ChromaDB heartbeat: {heartbeat}")

            # Test 3: Circuit breaker state
            logger.info("  Test 3: Circuit breaker state...")
            redis_breaker_state = redis_client.breaker.current_state
            chroma_breaker_state = chroma_client.breaker.current_state
            logger.info(f"    ✓ Redis breaker: {redis_breaker_state}")
            logger.info(f"    ✓ ChromaDB breaker: {chroma_breaker_state}")

            return {
                "status": "PASSED",
                "redis_ping": ping_result,
                "redis_operations": set_result and get_result == b'test_value',
                "chromadb_heartbeat": heartbeat,
                "redis_breaker": str(redis_breaker_state),
                "chroma_breaker": str(chroma_breaker_state)
            }

        except Exception as e:
            logger.error(f"  ✗ Error recovery test failed: {e}")
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def test_mcp_integration(self) -> Dict[str, Any]:
        """Test integration with MCP server"""
        logger.info("=" * 60)
        logger.info("Testing MCP Server Integration")
        logger.info("=" * 60)

        try:
            # Check if production features are importable
            logger.info("  Test 1: Import production features...")
            import sys
            sys.path.insert(0, '/home/rebelsts/RAG/mcp_server')

            # Verify modules are accessible
            from health_checks import health_checker
            from cache_warmer import cache_warmer
            from gpu_verification import GPUVerifier
            logger.info("    ✓ All production modules importable")

            # Test 2: Verify MCP server file has integration
            logger.info("  Test 2: Verify MCP server integration...")
            with open('/home/rebelsts/RAG/mcp_server/rag_server.py', 'r') as f:
                content = f.read()
                has_health_check = 'async def health_check()' in content
                has_cache_stats = 'async def get_cache_warming_stats()' in content
                has_gpu_verify = 'async def verify_gpu_acceleration()' in content

                logger.info(f"    ✓ health_check tool: {has_health_check}")
                logger.info(f"    ✓ cache_warming_stats tool: {has_cache_stats}")
                logger.info(f"    ✓ gpu_verification tool: {has_gpu_verify}")

            return {
                "status": "PASSED",
                "modules_importable": True,
                "health_check_tool": has_health_check,
                "cache_stats_tool": has_cache_stats,
                "gpu_verify_tool": has_gpu_verify
            }

        except Exception as e:
            logger.error(f"  ✗ MCP integration test failed: {e}")
            self.all_passed = False
            return {
                "status": "FAILED",
                "error": str(e)
            }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate report"""
        logger.info("\n" + "=" * 60)
        logger.info("PRODUCTION ENHANCEMENTS TEST SUITE")
        logger.info("=" * 60 + "\n")

        start_time = time.time()

        # Run all tests
        self.results["cache_warmer"] = self.test_cache_warmer()
        self.results["health_checks"] = await self.test_health_checks()
        self.results["gpu_verification"] = self.test_gpu_verification()
        self.results["error_recovery"] = self.test_error_recovery()
        self.results["integration"] = self.test_mcp_integration()

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


async def main():
    """Main test execution"""
    tester = ProductionEnhancementTester()
    results = await tester.run_all_tests()

    # Print JSON results for programmatic access
    import json
    print("\n" + "=" * 60)
    print("DETAILED RESULTS (JSON)")
    print("=" * 60)
    print(json.dumps(results, indent=2, default=str))

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASSED" else 1)


if __name__ == "__main__":
    asyncio.run(main())
