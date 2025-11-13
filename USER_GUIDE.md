# RAG Knowledge Base - User Guide

**Version**: 1.0
**Last Updated**: 2025-11-13
**System**: GPU-Accelerated (AMD 7900 XTX)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Using the RAG System](#using-the-rag-system)
3. [MCP Tools Reference](#mcp-tools-reference)
4. [System Management](#system-management)
5. [Performance](#performance)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Quick Start

### What is This?

A **GPU-accelerated RAG (Retrieval-Augmented Generation) system** that gives Claude Code access to 70,652 documents across 36 technologies:

- React, Python, Docker, TypeScript, PostgreSQL, FastAPI, and 30+ more
- 6.2ms average query time (68x faster than CPU)
- Integrated with Claude Code CLI via MCP

### Prerequisites

- ✅ Docker running (ChromaDB container)
- ✅ MCP server configured
- ✅ Claude Code CLI installed

### Verify System is Running

```bash
# Check ChromaDB is running
docker ps | grep chromadb-server

# Check ChromaDB health
curl http://localhost:8001/api/v2/heartbeat

# Test MCP server
./.venv/bin/python test_mcp_server.py
```

**Expected Output**:
```
✓ All tests passed! MCP server is ready for use.
```

---

## Using the RAG System

### Method 1: Via Claude Code CLI (Recommended)

**Start a Claude Code session**:
```bash
cd /home/rebelsts/RAG
claude
```

**Ask questions naturally**:

```
You: "Use the RAG knowledge base to search for React hooks examples"

Claude: [Automatically uses query_knowledge_base MCP tool]
        [Returns React hooks documentation with examples]
```

**More examples**:
```
"Query the knowledge base for Docker networking best practices"
"Search the RAG system for Python async/await patterns"
"Find FastAPI dependency injection examples in the knowledge base"
"List all technologies available in the knowledge base"
"How many documents are in the RAG system?"
```

**The MCP server automatically**:
- Generates GPU-accelerated embeddings (2.5ms)
- Searches 70,652 documents (3.7ms)
- Returns top 5 most relevant results
- Includes source URLs and technology tags

### Method 2: Direct MCP Tool Calls

**Claude Code can also invoke tools directly**:

```
You: "Use query_knowledge_base with query='React hooks' and top_k=10"

You: "Use list_technologies to show all available filters"

You: "Use get_collection_stats to show database info"
```

### Method 3: Python Script

**For automation or testing**:

```python
import chromadb
from sentence_transformers import SentenceTransformer

# Connect to ChromaDB
client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

# Load GPU-accelerated model
model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    model = model.to('cuda')

# Query
query = "How do I use React hooks?"
embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=embedding,
    n_results=5
)

# Display results
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"\n{i+1}. {meta.get('technology', 'Unknown')}")
    print(f"   {doc[:200]}...")
```

---

## MCP Tools Reference

### Tool 1: query_knowledge_base

**Description**: Search the RAG knowledge base for relevant documentation

**Parameters**:
- `query` (required): Natural language question
- `collection_name` (optional): Default "coding_knowledge"
- `top_k` (optional): Number of results (default: 5, max: 20)
- `technology_filter` (optional): Filter by technology name

**Examples**:

```python
# Basic query
query_knowledge_base("How do I create a React component?")

# With technology filter
query_knowledge_base(
    query="async functions",
    technology_filter="Python Docs",
    top_k=10
)

# More results
query_knowledge_base(
    query="Docker networking",
    top_k=20
)
```

**Returns**:
```json
{
  "query": "How do I create a React component?",
  "results": [
    {
      "rank": 1,
      "content": "Components are the building blocks...",
      "technology": "React Docs",
      "source_url": "https://github.com/reactjs/react.dev",
      "source_file": "data/repos/react_dev/...",
      "similarity_score": 0.8532,
      "distance": 0.1468
    }
  ],
  "total_found": 5
}
```

### Tool 2: list_technologies

**Description**: List all available technology filters

**Parameters**: None

**Example**:
```python
list_technologies()
```

**Returns**:
```json
{
  "total_technologies": 36,
  "total_documents": 70652,
  "technologies": [
    {"name": "React Docs", "document_count": 15234},
    {"name": "Python Docs", "document_count": 12456},
    {"name": "Docker Docs", "document_count": 8923},
    ...
  ]
}
```

### Tool 3: get_collection_stats

**Description**: Get database statistics

**Parameters**:
- `collection_name` (optional): Default "coding_knowledge"

**Example**:
```python
get_collection_stats()
```

**Returns**:
```json
{
  "collection_name": "coding_knowledge",
  "document_count": 70652,
  "metadata": {}
}
```

---

## System Management

### Starting the System

**ChromaDB is already running** (Docker container). Verify with:
```bash
docker ps | grep chromadb-server
```

If not running:
```bash
cd /home/rebelsts/RAG
docker compose up -d chromadb
```

### Stopping the System

```bash
docker compose stop chromadb
```

### Restarting the System

```bash
docker compose restart chromadb
```

### Viewing Logs

```bash
# Real-time logs
docker logs -f chromadb-server

# Last 50 lines
docker logs chromadb-server --tail 50
```

### Checking System Health

**Quick health check**:
```bash
curl http://localhost:8001/api/v2/heartbeat
# Should return: positive number (milliseconds)
```

**Comprehensive test**:
```bash
cd /home/rebelsts/RAG
./.venv/bin/python test_mcp_server.py
```

**Run full test suite**:
```bash
./.venv/bin/pytest tests/test_comprehensive.py -v
```

---

## Performance

### Current Performance Metrics

**GPU-Accelerated (AMD 7900 XTX)**:

| Metric | Performance |
|--------|-------------|
| Query Latency | 6.2ms average |
| Embedding Generation | 2.5ms |
| Vector Search | 3.7ms |
| Throughput | 160+ queries/second |
| GPU Utilization | <5% |

### Benchmark Your System

```bash
cd /home/rebelsts/RAG
./.venv/bin/python benchmark_gpu.py
```

**Expected output**:
```
Embedding Generation:
  CPU:     746.6ms
  GPU:       2.5ms
  Speedup: 301.38x faster

Full RAG Query:
  CPU:     421.4ms
  GPU:       6.2ms
  Speedup: 67.91x faster
```

### Performance Tips

1. **GPU is already optimized** - no action needed
2. **First query may be slower** (model loading) - subsequent queries are fast
3. **Batch queries when possible** - slightly more efficient
4. **Use technology filters** - reduces search space, slightly faster

---

## Troubleshooting

### ChromaDB Not Responding

**Symptom**: Queries fail with connection error

**Solution**:
```bash
# Check if running
docker ps | grep chromadb

# If not running, start it
docker compose up -d chromadb

# Check logs for errors
docker logs chromadb-server --tail 50

# Restart if needed
docker compose restart chromadb
```

### MCP Server Not Working

**Symptom**: Claude Code can't access RAG tools

**Solution**:
```bash
# 1. Verify MCP config exists
cat ~/.config/claude-code/mcp_servers.json

# 2. Test MCP server manually
./.venv/bin/python mcp_server/rag_server.py
# (Press Ctrl+C to stop)

# 3. Restart Claude Code session
# Exit current session and start new one
```

### Slow Query Performance

**Symptom**: Queries taking >100ms

**Solution**:
```bash
# 1. Check GPU is being used
./.venv/bin/python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"
# Should print: GPU available: True

# 2. Check GPU temperature
rocm-smi
# Temperature should be <80°C

# 3. Run benchmark
./.venv/bin/python benchmark_gpu.py
# Should show ~6ms queries
```

### No Results Found

**Symptom**: Queries return 0 results

**Possible causes**:

1. **Invalid technology filter**:
   ```bash
   # List valid technologies
   ./.venv/bin/python -c "
   import chromadb
   client = chromadb.HttpClient(host='localhost', port=8001)
   collection = client.get_collection('coding_knowledge')

   # Get all technologies
   all_meta = collection.get(include=['metadatas'], limit=1000)
   techs = set()
   for meta in all_meta['metadatas']:
       if 'technology' in meta:
           techs.add(meta['technology'])

   print('Available technologies:')
   for tech in sorted(techs):
       print(f'  - {tech}')
   "
   ```

2. **ChromaDB empty** (unlikely):
   ```bash
   # Check document count
   ./.venv/bin/python -c "
   import chromadb
   client = chromadb.HttpClient(host='localhost', port=8001)
   collection = client.get_collection('coding_knowledge')
   print(f'Documents: {collection.count()}')
   "
   # Should print: Documents: 70652
   ```

### GPU Not Detected

**Symptom**: System using CPU instead of GPU

**Solution**:
```bash
# 1. Check ROCm installation
rocm-smi
# Should show your GPU

# 2. Check PyTorch ROCm support
./.venv/bin/python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'ROCm available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')
"

# 3. Reinstall PyTorch with ROCm if needed
./.venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```

---

## Advanced Usage

### Technology Filtering

**Filter by specific technology**:
```python
# Via Claude Code
"Search the knowledge base for hooks, filtered to React Docs only"

# Via Python
results = collection.query(
    query_embeddings=embedding,
    n_results=5,
    where={"technology": "React Docs"}
)
```

**Available technologies** (36 total):
- React Docs, Python Docs, Docker Docs, TypeScript Docs
- PostgreSQL Docs, FastAPI Docs, Node.js Docs, Vue Docs
- Angular Docs, Next.js Docs, Express Docs, MongoDB Docs
- Redis Docs, n8n Docs, ComfyUI Repo, Figma API Docs
- ... and 20 more (use `list_technologies()` for full list)

### Batch Queries

**Process multiple queries efficiently**:
```python
import chromadb
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer('all-MiniLM-L6-v2')
if torch.cuda.is_available():
    model = model.to('cuda')

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

# Multiple queries
queries = [
    "React hooks examples",
    "Python async patterns",
    "Docker networking"
]

# Batch embedding (faster than one-by-one)
embeddings = model.encode(queries).tolist()

# Query all
for query, embedding in zip(queries, embeddings):
    results = collection.query(
        query_embeddings=[embedding],
        n_results=5
    )
    print(f"\nQuery: {query}")
    print(f"Top result: {results['metadatas'][0][0].get('technology')}")
```

### Custom Similarity Thresholds

**Filter by similarity score**:
```python
results = collection.query(
    query_embeddings=embedding,
    n_results=20  # Get more results
)

# Filter by score
threshold = 0.7
filtered_results = [
    (doc, meta, 1 - dist)
    for doc, meta, dist in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )
    if (1 - dist) >= threshold
]

print(f"Found {len(filtered_results)} results above {threshold} similarity")
```

### Export Results

**Save results to file**:
```python
import json

results = collection.query(
    query_embeddings=embedding,
    n_results=10
)

# Format for export
export_data = {
    "query": "Your query here",
    "timestamp": "2025-11-13T17:00:00",
    "results": [
        {
            "content": doc,
            "technology": meta.get('technology'),
            "source": meta.get('source_url'),
            "score": round(1 - dist, 4)
        }
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )
    ]
}

# Save to JSON
with open('query_results.json', 'w') as f:
    json.dump(export_data, f, indent=2)

print("Results saved to query_results.json")
```

---

## Data & Statistics

### System Overview

| Metric | Value |
|--------|-------|
| **Total Documents** | 70,652 |
| **Technologies** | 36 |
| **Total Source Files** | 4,484 |
| **Chunk Size** | 1,000 characters |
| **Chunk Overlap** | 150 characters |
| **Embedding Model** | all-MiniLM-L6-v2 |
| **Embedding Dimensions** | 384 |
| **Database Size** | ~2.5GB |

### Top Technologies by Document Count

Run to get current counts:
```python
import chromadb

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_collection('coding_knowledge')

all_meta = collection.get(include=['metadatas'])
tech_counts = {}

for meta in all_meta['metadatas']:
    tech = meta.get('technology', 'Unknown')
    tech_counts[tech] = tech_counts.get(tech, 0) + 1

# Sort and display top 10
for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{tech:30} {count:>6,} documents")
```

---

## File Locations

**Important Paths**:

```
/home/rebelsts/RAG/
├── mcp_server/
│   └── rag_server.py              # MCP server (GPU-accelerated)
├── tests/
│   └── test_comprehensive.py      # Test suite
├── data/                          # Source documentation (4,484 files)
├── benchmark_gpu.py               # Performance benchmarks
├── test_mcp_server.py             # Quick validation
├── docker-compose.yml             # ChromaDB configuration
└── USER_GUIDE.md                  # This file

~/.config/claude-code/
└── mcp_servers.json              # MCP configuration

/mnt/nvme-fast/
├── docker-volumes/chromadb/      # Database storage (2.5GB)
└── backups/chromadb/             # Backups (if configured)
```

---

## Getting Help

### Check Logs

```bash
# MCP server errors (if running in background)
tail -f ~/.claude/logs/mcp_*.log

# ChromaDB logs
docker logs chromadb-server --tail 100

# System health
docker ps
docker stats chromadb-server
```

### Run Diagnostics

```bash
cd /home/rebelsts/RAG

# Test everything
./.venv/bin/python test_mcp_server.py
./.venv/bin/pytest tests/test_comprehensive.py -v

# Benchmark performance
./.venv/bin/python benchmark_gpu.py

# Check GPU
rocm-smi
```

### Common Questions

**Q: How do I add new documents?**
A: Place files in `data/` directory and run `./.venv/bin/python ingest.py`

**Q: Can I use this without Claude Code?**
A: Yes, use the Python API directly (see examples above)

**Q: Why is the first query slow?**
A: GPU model loading takes 1-2 seconds. Subsequent queries are fast.

**Q: Can I run this on CPU only?**
A: Yes, but 68x slower (421ms vs 6.2ms). Remove GPU code from `mcp_server/rag_server.py`

**Q: How much RAM does this use?**
A: ~4GB total (2GB GPU VRAM + 2GB system RAM)

---

## Next Steps

**System is ready to use!**

Try these queries to get started:
```
"Use the RAG knowledge base to search for React component patterns"
"Query the knowledge base for Python decorators examples"
"Find Docker multi-stage build examples in the knowledge base"
"List all technologies in the RAG system"
```

For production deployment with authentication and monitoring, see Phase 5 & 6 options in IMPLEMENTATION_WORKFLOW.md.

---

**Questions or issues?** Check the troubleshooting section above or review the test results:
```bash
./.venv/bin/python test_mcp_server.py
```
