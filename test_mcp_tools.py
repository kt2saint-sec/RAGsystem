#!/usr/bin/env python3
"""
MCP Tool Integration Validation
Tests the new production enhancement tools through MCP
"""

import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_tools():
    """Test MCP tools integration"""
    logger.info("=" * 60)
    logger.info("MCP TOOL INTEGRATION VALIDATION")
    logger.info("=" * 60)

    try:
        # Import the MCP server module
        sys.path.insert(0, '/home/rebelsts/RAG/mcp_server')
        import rag_server

        logger.info("\n✓ MCP server module loaded successfully")

        # Test 1: Check PRODUCTION_FEATURES flag
        logger.info("\nTest 1: Production features availability")
        if hasattr(rag_server, 'PRODUCTION_FEATURES'):
            logger.info(f"  ✓ PRODUCTION_FEATURES = {rag_server.PRODUCTION_FEATURES}")
        else:
            logger.warning("  ✗ PRODUCTION_FEATURES not found")

        # Test 2: Check tool definitions exist
        logger.info("\nTest 2: Verify tool definitions")
        tools_to_check = [
            'health_check',
            'get_cache_warming_stats',
            'verify_gpu_acceleration'
        ]

        tools_found = []
        for tool_name in tools_to_check:
            if hasattr(rag_server, tool_name):
                tools_found.append(tool_name)
                logger.info(f"  ✓ {tool_name} tool found")
            else:
                logger.warning(f"  ✗ {tool_name} tool not found")

        # Test 3: Verify imports are available
        logger.info("\nTest 3: Verify production imports")
        try:
            from health_checks import health_checker
            from cache_warmer import cache_warmer
            from gpu_verification import GPUVerifier
            logger.info("  ✓ All production modules imported successfully")
            modules_ok = True
        except ImportError as e:
            logger.error(f"  ✗ Import failed: {e}")
            modules_ok = False

        # Test 4: Call the tools if PRODUCTION_FEATURES is enabled
        if hasattr(rag_server, 'PRODUCTION_FEATURES') and rag_server.PRODUCTION_FEATURES:
            logger.info("\nTest 4: Call MCP tools")

            # Test health_check
            try:
                logger.info("  Testing health_check()...")
                health_result = await rag_server.health_check()
                logger.info(f"    ✓ Status: {health_result.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"    ✗ health_check failed: {e}")

            # Test get_cache_warming_stats
            try:
                logger.info("  Testing get_cache_warming_stats()...")
                cache_stats = await rag_server.get_cache_warming_stats()
                logger.info(f"    ✓ Unique queries: {cache_stats.get('total_unique_queries', 0)}")
            except Exception as e:
                logger.error(f"    ✗ get_cache_warming_stats failed: {e}")

            # Test verify_gpu_acceleration
            try:
                logger.info("  Testing verify_gpu_acceleration()...")
                gpu_result = await rag_server.verify_gpu_acceleration()
                if 'pytorch_gpu' in gpu_result:
                    cuda_available = gpu_result['pytorch_gpu'].get('cuda_available', False)
                    logger.info(f"    ✓ CUDA available: {cuda_available}")
                else:
                    logger.info(f"    ✓ Result received (no error)")
            except Exception as e:
                logger.error(f"    ✗ verify_gpu_acceleration failed: {e}")
        else:
            logger.warning("\nTest 4: Skipped (PRODUCTION_FEATURES not enabled)")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Tools found: {len(tools_found)}/{len(tools_to_check)}")
        logger.info(f"Modules importable: {modules_ok}")
        logger.info(f"Overall: {'PASSED' if len(tools_found) == len(tools_to_check) and modules_ok else 'FAILED'}")
        logger.info("=" * 60)

        return len(tools_found) == len(tools_to_check) and modules_ok

    except Exception as e:
        logger.error(f"\n✗ MCP tool validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main execution"""
    success = await test_mcp_tools()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
