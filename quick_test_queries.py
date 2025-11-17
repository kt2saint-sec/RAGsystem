#!/usr/bin/env python3
"""Quick test queries for tech stack verification"""

import chromadb
from sentence_transformers import SentenceTransformer

# Connect to ChromaDB
client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_collection(name="coding_knowledge")

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Test queries
test_queries = [
    ("How to use server actions in Next.js 16?", "Next.js 16 Documentation"),
    ("React 19 use hook examples", "React 19 Documentation"),
    ("Next.js app router file conventions", "Next.js 16 Documentation"),
]

print("=" * 70)
print("TECH STACK VERIFICATION TESTS")
print("=" * 70)

for query, tech_filter in test_queries:
    print(f"\nQuery: '{query}'")
    print(f"Filter: {tech_filter}")
    print("-" * 70)

    # Generate embedding
    query_embedding = model.encode(query).tolist()

    # Search with filter
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={"technology": tech_filter}
    )

    if results['documents'][0]:
        print(f"✓ Found {len(results['documents'][0])} results")
        print(f"  Top result: {results['documents'][0][0][:150]}...")
        print(f"  Technology: {results['metadatas'][0][0].get('technology', 'Unknown')}")
    else:
        print(f"✗ NO RESULTS FOUND")

# Get database stats
count = collection.count()
print("\n" + "=" * 70)
print(f"DATABASE STATUS: {count:,} total chunks")
print("=" * 70)
