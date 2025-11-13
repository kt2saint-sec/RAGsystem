#!/usr/bin/env python3
"""
Benchmark GPU vs CPU performance for RAG system
"""

import time
import chromadb
from sentence_transformers import SentenceTransformer
import torch
import statistics

def benchmark_embeddings(device='cpu', num_queries=10):
    """Benchmark embedding generation speed"""
    print(f"\n{'='*70}")
    print(f"Benchmarking on: {device.upper()}")
    print(f"{'='*70}")

    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    if device == 'gpu' and torch.cuda.is_available():
        model = model.to('cuda')
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Using CPU")

    # Test queries
    test_queries = [
        "How do I use React hooks?",
        "Explain Docker networking concepts",
        "Python async await patterns",
        "TypeScript generics examples",
        "PostgreSQL query optimization",
        "FastAPI dependency injection",
        "Git rebase vs merge explained",
        "Redis caching strategies",
        "Kubernetes deployment best practices",
        "Next.js server-side rendering"
    ]

    times = []

    # Warmup
    print("\nWarming up...")
    _ = model.encode(test_queries[:2], show_progress_bar=False)

    # Benchmark
    print(f"\nRunning {num_queries} queries...")
    for i, query in enumerate(test_queries[:num_queries], 1):
        start = time.time()
        _ = model.encode([query], show_progress_bar=False)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Query {i}/{num_queries}: {elapsed*1000:.1f}ms")

    # Statistics
    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)

    print(f"\nResults:")
    print(f"  Average: {avg_time*1000:.1f}ms")
    print(f"  Median:  {median_time*1000:.1f}ms")
    print(f"  Min:     {min_time*1000:.1f}ms")
    print(f"  Max:     {max_time*1000:.1f}ms")

    return avg_time

def benchmark_full_query(device='cpu', num_queries=5):
    """Benchmark full RAG query (embedding + vector search)"""
    print(f"\n{'='*70}")
    print(f"Full RAG Query Benchmark: {device.upper()}")
    print(f"{'='*70}")

    # Initialize
    model = SentenceTransformer('all-MiniLM-L6-v2')
    if device == 'gpu' and torch.cuda.is_available():
        model = model.to('cuda')

    client = chromadb.HttpClient(host='localhost', port=8001)
    collection = client.get_collection('coding_knowledge')

    test_queries = [
        "How do I use React hooks?",
        "Explain Docker networking",
        "Python async patterns",
        "TypeScript generics",
        "PostgreSQL optimization"
    ]

    times = []

    print(f"\nRunning {num_queries} full queries...")
    for i, query in enumerate(test_queries[:num_queries], 1):
        start = time.time()

        # Generate embedding
        query_embedding = model.encode([query], show_progress_bar=False).tolist()

        # Vector search
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=5
        )

        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Query {i}/{num_queries}: {elapsed*1000:.1f}ms ({len(results['documents'][0])} results)")

    avg_time = statistics.mean(times)
    print(f"\nAverage full query time: {avg_time*1000:.1f}ms")

    return avg_time

def main():
    """Run all benchmarks"""
    print("\n" + "="*70)
    print("RAG System Performance Benchmark")
    print("="*70)

    results = {}

    # Check GPU availability
    if torch.cuda.is_available():
        print(f"\nGPU Detected: {torch.cuda.get_device_name(0)}")
        print(f"ROCm Version: {torch.version.hip if hasattr(torch.version, 'hip') else 'N/A'}")

        # Benchmark CPU
        print("\n" + "="*70)
        print("PHASE 1: CPU Benchmarks")
        print("="*70)
        cpu_embed_time = benchmark_embeddings(device='cpu', num_queries=10)
        cpu_query_time = benchmark_full_query(device='cpu', num_queries=5)

        # Benchmark GPU
        print("\n" + "="*70)
        print("PHASE 2: GPU Benchmarks")
        print("="*70)
        gpu_embed_time = benchmark_embeddings(device='gpu', num_queries=10)
        gpu_query_time = benchmark_full_query(device='gpu', num_queries=5)

        # Calculate speedup
        embed_speedup = cpu_embed_time / gpu_embed_time
        query_speedup = cpu_query_time / gpu_query_time

        results['cpu_embedding_ms'] = cpu_embed_time * 1000
        results['gpu_embedding_ms'] = gpu_embed_time * 1000
        results['cpu_full_query_ms'] = cpu_query_time * 1000
        results['gpu_full_query_ms'] = gpu_query_time * 1000
        results['embedding_speedup'] = embed_speedup
        results['full_query_speedup'] = query_speedup

        # Summary
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70)
        print(f"\nEmbedding Generation:")
        print(f"  CPU:     {cpu_embed_time*1000:6.1f}ms")
        print(f"  GPU:     {gpu_embed_time*1000:6.1f}ms")
        print(f"  Speedup: {embed_speedup:.2f}x faster")

        print(f"\nFull RAG Query:")
        print(f"  CPU:     {cpu_query_time*1000:6.1f}ms")
        print(f"  GPU:     {gpu_query_time*1000:6.1f}ms")
        print(f"  Speedup: {query_speedup:.2f}x faster")

        print(f"\nConclusion:")
        if gpu_query_time < 0.5:
            print(f"  ✓ GPU optimization successful! Query time < 500ms")
        else:
            print(f"  ⚠ GPU queries: {gpu_query_time*1000:.1f}ms (target: < 500ms)")

    else:
        print("\n⚠ GPU not available, running CPU benchmark only")
        cpu_embed_time = benchmark_embeddings(device='cpu', num_queries=10)
        cpu_query_time = benchmark_full_query(device='cpu', num_queries=5)

    return results

if __name__ == "__main__":
    results = main()
