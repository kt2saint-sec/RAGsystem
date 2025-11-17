"""
Diagnostic script to inspect ChromaDB metadata structure

This script examines actual chunks in the ChromaDB database to understand
what metadata fields are available and their values, so we can fix the
filtering logic in EnhancedRAGAgent.
"""

import chromadb
import json

def diagnose_chromadb():
    """Examine ChromaDB metadata structure and content"""

    print("=" * 80)
    print("CHROMADB METADATA STRUCTURE DIAGNOSIS")
    print("=" * 80)

    try:
        # Connect to ChromaDB
        client = chromadb.HttpClient(host="localhost", port=8001)
        collection = client.get_collection("coding_knowledge")

        print(f"\n✓ Connected to ChromaDB at localhost:8001")
        print(f"✓ Collection: coding_knowledge")

        # Get collection count
        count = collection.count()
        print(f"✓ Total chunks in collection: {count}")

        # Retrieve a sample of chunks to inspect metadata
        print("\n" + "=" * 80)
        print("SAMPLE CHUNKS (First 5)")
        print("=" * 80)

        results = collection.get(limit=5, include=["documents", "metadatas"])

        if results and results["metadatas"]:
            for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"]), 1):
                print(f"\n--- Chunk {i} ---")
                print(f"Document preview: {doc[:100]}...")
                print(f"Metadata: {json.dumps(metadata, indent=2)}")

                # Analyze metadata keys
                if i == 1:
                    print(f"\nMetadata Keys Available: {list(metadata.keys())}")

        # Query with sample text to see metadata in query results
        print("\n" + "=" * 80)
        print("QUERY RESULT STRUCTURE")
        print("=" * 80)

        query_results = collection.query(
            query_texts=["How do I use React?"],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )

        print(f"\nQuery: 'How do I use React?'")
        print(f"Results returned: {len(query_results['documents'][0])}")

        if query_results["metadatas"] and query_results["metadatas"][0]:
            print(f"\nFirst result metadata:")
            print(json.dumps(query_results["metadatas"][0][0], indent=2))

            # Analyze all metadata keys across results
            all_keys = set()
            for metadata_list in query_results["metadatas"]:
                for metadata in metadata_list:
                    all_keys.update(metadata.keys())

            print(f"\nAll available metadata keys across results:")
            for key in sorted(all_keys):
                print(f"  - {key}")

        # Test filter syntax
        print("\n" + "=" * 80)
        print("FILTER SYNTAX TESTING")
        print("=" * 80)

        # Get actual metadata values to test filters
        if query_results["metadatas"] and query_results["metadatas"][0]:
            first_metadata = query_results["metadatas"][0][0]

            # Test with actual values from metadata
            print(f"\nTesting filters with actual metadata values...")
            print(f"First result metadata keys: {list(first_metadata.keys())}")

            # Try different filter syntaxes
            test_filters = []

            if "technology" in first_metadata:
                tech_value = first_metadata["technology"]
                print(f"\n1. Filter by 'technology': {tech_value}")
                test_filters.append({
                    "name": "technology exact match",
                    "filter": {"technology": tech_value}
                })
                test_filters.append({
                    "name": "technology in list",
                    "filter": {"technology": {"$in": [tech_value]}}
                })

            if "source_url" in first_metadata:
                source = first_metadata["source_url"]
                print(f"\n2. Filter by 'source_url': {source}")
                test_filters.append({
                    "name": "source_url exact match",
                    "filter": {"source_url": source}
                })

            if "source_file" in first_metadata:
                source_file = first_metadata["source_file"]
                print(f"\n3. Filter by 'source_file': {source_file}")
                test_filters.append({
                    "name": "source_file contains",
                    "filter": {"source_file": {"$regex": ".*"}}
                })

            # Execute test filters
            print(f"\nExecuting {len(test_filters)} filter tests...\n")

            for test in test_filters:
                try:
                    result = collection.query(
                        query_texts=["test"],
                        n_results=1,
                        where=test["filter"]
                    )
                    count = len(result["documents"][0]) if result["documents"] else 0
                    status = "✓" if count > 0 else "✗"
                    print(f"{status} {test['name']}: {count} results")
                except Exception as e:
                    print(f"✗ {test['name']}: ERROR - {str(e)[:60]}")

        # Summary and recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        print("""
Based on the diagnostic results:

1. Check which metadata fields are actually present in chunks
2. Verify the correct field names for technology/source filtering
3. Test different filter syntaxes:
   - Exact match: {"field": "value"}
   - In list: {"field": {"$in": ["value1", "value2"]}}
   - Regex: {"field": {"$regex": "pattern"}}
   - Comparison: {"field": {"$gt": 5}}

4. Consider filtering by different fields if technology/source_url not available:
   - source_file
   - Other custom metadata fields

5. May need to re-ingest chunks with proper metadata if fields are missing
        """)

    except Exception as e:
        print(f"\n✗ Error connecting to ChromaDB: {str(e)}")
        print("\nMake sure ChromaDB is running:")
        print("  source /home/rebelsts/RAG/.venv/bin/activate")
        print("  chroma run --path /mnt/nvme-fast/databases/chromadb --port 8001")

if __name__ == "__main__":
    diagnose_chromadb()
