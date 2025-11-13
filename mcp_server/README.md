# RAG Knowledge Base MCP Server

FastMCP-based server for querying the RAG knowledge base via Claude Code CLI.

## Features

- **3 MCP Tools**:
  - `query_knowledge_base`: Semantic search across 70,652 documents
  - `list_technologies`: List all 41+ available technology filters
  - `get_collection_stats`: Get collection statistics

- **3 MCP Resources**:
  - `config://embedding-model`: Embedding model information
  - `config://chromadb-connection`: ChromaDB connection details
  - `config://available-technologies`: List of available technologies

## Installation

Already installed as part of Phase 2. Configuration file located at:
```
~/.config/claude-code/mcp_servers.json
```

## Usage

### From Claude Code CLI

The MCP server is automatically available in any Claude Code session:

```python
# Example queries:
"Use the RAG knowledge base to search for React hooks examples"
"Query the knowledge base for Docker networking best practices"
"List all available technologies in the knowledge base"
```

### Manual Testing

```bash
# Start the server manually
.venv/bin/python mcp_server/rag_server.py

# Run validation tests
.venv/bin/python test_mcp_server.py
```

## MCP Tools Reference

### 1. query_knowledge_base

Query the RAG knowledge base for relevant documentation.

**Parameters:**
- `query` (string, required): Natural language question
- `collection_name` (string, optional): Collection to search (default: "coding_knowledge")
- `top_k` (integer, optional): Number of results (default: 5, max: 20)
- `technology_filter` (string, optional): Filter by technology (e.g., "React Docs")

**Returns:**
```json
{
  "query": "How do I use React hooks?",
  "results": [
    {
      "rank": 1,
      "content": "...",
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

**Examples:**
```python
query_knowledge_base("How do I use React hooks?")
query_knowledge_base("Python async await examples", technology_filter="Python Docs")
query_knowledge_base("Docker compose networking", top_k=10)
```

### 2. list_technologies

List all available technology filters in the knowledge base.

**Returns:**
```json
{
  "total_technologies": 41,
  "total_documents": 70652,
  "technologies": [
    {"name": "React Docs", "document_count": 15234},
    {"name": "Python Docs", "document_count": 12456},
    ...
  ]
}
```

### 3. get_collection_stats

Get statistics about a ChromaDB collection.

**Parameters:**
- `collection_name` (string, optional): Collection name (default: "coding_knowledge")

**Returns:**
```json
{
  "collection_name": "coding_knowledge",
  "document_count": 70652,
  "metadata": {}
}
```

## Available Technologies

The knowledge base includes documentation for 41+ technologies:

- **Frontend**: React, Vue, Angular, TypeScript, JavaScript
- **Backend**: Python, Node.js, FastAPI, Django, Express
- **Databases**: PostgreSQL, MongoDB, Redis, ChromaDB
- **DevOps**: Docker, Kubernetes, GitHub Actions, CI/CD
- **Cloud**: AWS, Azure, GCP
- **Tools**: Git, VS Code, Webpack, Vite
- And many more...

Run `list_technologies()` for the complete list.

## Configuration

**Environment Variables:**
- `CHROMA_HOST`: ChromaDB host (default: localhost)
- `CHROMA_PORT`: ChromaDB port (default: 8001)
- `EMBEDDING_MODEL`: Sentence transformer model (default: all-MiniLM-L6-v2)

**Current Configuration:**
```json
{
  "command": "/home/rebelsts/RAG/.venv/bin/python",
  "args": ["/home/rebelsts/RAG/mcp_server/rag_server.py"],
  "env": {
    "CHROMA_HOST": "localhost",
    "CHROMA_PORT": "8001",
    "EMBEDDING_MODEL": "all-MiniLM-L6-v2"
  }
}
```

## Troubleshooting

### Server won't start
```bash
# Check ChromaDB is running
docker ps | grep chromadb-server

# Check port 8001 is accessible
curl http://localhost:8001/api/v2/heartbeat

# Check logs
docker logs chromadb-server
```

### No results from queries
```bash
# Verify collection exists and has data
.venv/bin/python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8001)
col = client.get_collection('coding_knowledge')
print(f'Documents: {col.count()}')
"
```

### MCP server not detected by Claude Code
```bash
# Verify configuration file
cat ~/.config/claude-code/mcp_servers.json

# Restart Claude Code session
# Exit current session and start new one
```

## Performance

- **Query latency**: ~1-2 seconds (CPU embedding)
- **GPU acceleration**: Available (see Phase 3 for setup)
- **Concurrent queries**: Supported
- **Memory usage**: ~2GB (model loaded)

## Next Steps

- **Phase 3**: Enable GPU acceleration for 5-10x faster queries
- **Phase 4**: Add comprehensive test coverage
- **Phase 5**: Production hardening (auth, monitoring, backups)

## Files

```
mcp_server/
├── rag_server.py          # MCP server implementation
├── requirements.txt       # Python dependencies
└── README.md             # This file

~/.config/claude-code/
└── mcp_servers.json      # MCP configuration
```
