#!/usr/bin/env python3
"""
Test script to validate MCP server functionality
"""

import subprocess
import json
import sys

def test_mcp_server():
    """Test the MCP server by simulating MCP protocol messages"""

    print("=" * 70)
    print("Testing RAG Knowledge Base MCP Server")
    print("=" * 70)

    # Test 1: Server can start
    print("\n[Test 1] Starting MCP server...")
    try:
        proc = subprocess.Popen(
            ["./.venv/bin/python", "mcp_server/rag_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send initialize request (MCP protocol)
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        # Send request
        proc.stdin.write(json.dumps(initialize_request) + "\n")
        proc.stdin.flush()

        # Wait a bit and check if process is still running
        import time
        time.sleep(2)

        if proc.poll() is None:
            print("✓ MCP server started successfully")
            proc.terminate()
            proc.wait(timeout=5)
            return True
        else:
            stderr = proc.stderr.read()
            print(f"✗ MCP server failed to start")
            print(f"Error: {stderr}")
            return False

    except Exception as e:
        print(f"✗ Error testing MCP server: {e}")
        return False

def test_direct_query():
    """Test direct query to ChromaDB to verify data is accessible"""
    print("\n[Test 2] Testing direct ChromaDB query...")

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer

        # Connect to ChromaDB
        client = chromadb.HttpClient(host='localhost', port=8001)
        collection = client.get_collection('coding_knowledge')

        # Load model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Test query
        query = "How do I use React hooks?"
        query_embedding = model.encode([query]).tolist()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=3
        )

        if results and len(results['documents'][0]) > 0:
            print(f"✓ ChromaDB query successful")
            print(f"  Query: '{query}'")
            print(f"  Results: {len(results['documents'][0])} documents found")
            print(f"  Top result: {results['metadatas'][0][0].get('technology', 'Unknown')}")
            return True
        else:
            print("✗ No results from ChromaDB")
            return False

    except Exception as e:
        print(f"✗ ChromaDB query failed: {e}")
        return False

def test_collection_stats():
    """Test collection statistics"""
    print("\n[Test 3] Testing collection statistics...")

    try:
        import chromadb

        client = chromadb.HttpClient(host='localhost', port=8001)
        collection = client.get_collection('coding_knowledge')

        count = collection.count()
        print(f"✓ Collection stats retrieved")
        print(f"  Collection: coding_knowledge")
        print(f"  Documents: {count:,}")

        return True

    except Exception as e:
        print(f"✗ Collection stats failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("RAG MCP Server - Validation Tests")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("MCP Server Startup", test_mcp_server()))
    results.append(("ChromaDB Direct Query", test_direct_query()))
    results.append(("Collection Statistics", test_collection_stats()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! MCP server is ready for use.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
