# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **RAG (Retrieval-Augmented Generation) Knowledge Base System** designed to provide AI agents with accurate, fact-based technical documentation and code examples. The system uses a vector database (ChromaDB) with semantic search to retrieve relevant context for code generation tasks.

The system operates in a **client-server architecture** where ChromaDB runs as a standalone server, allowing multiple AI agents (Gemini CLI, Claude Code CLI, etc.) to query the same knowledge base concurrently.

## Core Architecture

The project follows a **three-stage data pipeline**:

1. **Acquisition** (`acquisition_agent.py`): Downloads documentation and code repositories
2. **Ingestion** (`ingest.py`): Processes files, creates embeddings, stores in vector database
3. **Query** (`coding_knowledge_tool.py`): Provides semantic search interface for AI agents

### Data Flow

```
targets.json → acquisition_agent.py → data/ directory
                                          ↓
                                    ingest.py → ChromaDB Server (port 8001)
                                                      ↓
                                            coding_knowledge_tool.py (query interface)
```

### Key Components

- **`targets.json`**: Configuration file defining data sources (git repos and websites)
  - Each target has a `name` field used as the `technology_filter` in queries
  - Supports two types: `git` (clones repositories) and `web_scrape` (scrapes documentation sites)

- **`acquisition_agent.py`**: Automated data acquisition
  - Clones git repositories with `--depth 1` for efficiency
  - Scrapes web content using BeautifulSoup
  - Stores data in `data/repos/` and `data/scraped/`

- **`ingest.py`**: Vector database ingestion pipeline
  - Connects to ChromaDB server (NOT embedded mode)
  - Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings
  - Processes files: `.md`, `.py`, `.js`, `.ts`, `.json`, `.txt`, `.html`, `.css`
  - Chunks text using `RecursiveCharacterTextSplitter` (1000 chars, 150 overlap)
  - **Incremental ingestion**: Tracks processed files by `source_file` metadata to avoid reprocessing

- **`coding_knowledge_tool.py`**: Query interface for MCP agents
  - Connects to ChromaDB server via HTTP client
  - Registers `query_knowledge_base` function with MCP framework
  - Supports `technology_filter` parameter for domain-specific queries
  - Instrumented with OpenTelemetry for observability

## Common Development Tasks

### Initial Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install langchain chromadb sentence-transformers pypdf beautifulsoup4 requests gitpython langchain-community langchain-text-splitters opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http opentelemetry-exporter-console
```

### Running ChromaDB Server

**CRITICAL**: The ChromaDB server MUST be running before ingestion or queries can work.

```bash
# In a dedicated terminal (must remain open)
source /home/rebelsts/RAG/.venv/bin/activate
chroma run --path /home/rebelsts/RAG/db --port 8001
```

### Data Acquisition

```bash
# Download all sources defined in targets.json
./.venv/bin/python acquisition_agent.py

# The script is idempotent - it skips existing repositories
# To add new sources: edit targets.json and re-run
```

### Data Ingestion

```bash
# Ingest data into ChromaDB (incremental - only processes new files)
./.venv/bin/python ingest.py

# After adding new targets: run acquisition_agent.py first, then ingest.py
```

### Testing

```bash
# Standalone test of the query interface (requires ChromaDB server)
./.venv/bin/python coding_knowledge_tool.py

# Automated test suite
./.venv/bin/python test_rag_system.py
```

## Technology Filters

When querying the knowledge base, use the `technology_filter` parameter to narrow results to specific domains. These correspond to the `name` field in `targets.json`:

**Programming Languages**:
- "Python Docs", "Rust Book", "Java SE Tutorials", "TypeScript Docs"
- "cppreference.com C++", "cppreference.com C"
- "Eloquent JavaScript Book"

**Web Development**:
- "React Docs", "Next.js Docs (Vercel)", "MDN HTML Docs", "MDN Web Dev Guide"
- "FastAPI Docs", "TypeScript Docs"

**AI/ML**:
- "Google Gemini Docs", "Anthropic Docs", "OpenAI Docs"
- "LangChain Docs", "ComfyUI Repo", "Stability AI Docs (SD/SDXL)"

**Mobile/Desktop**:
- "Flutter Docs", "Flutter Samples"

**Databases & Backend**:
- "Supabase Docs", "Firebase Docs"

**Security & Networking**:
- "Kali Linux Docs", "Kali Linux Tools List", "Wireshark User's Guide"
- "Ghidra Book", "Radare2 Book", "Reverse Engineering for Beginners Book"

**Business & Automation**:
- "Stripe Docs", "HubSpot API Docs", "n8n Docs"

**Design & Graphics**:
- "Figma API Docs", "GIMP Docs", "DTF Printing Guide"
- "Wikipedia - Raster Graphics", "Wikipedia - Halftone"

**Other**:
- "DigitalOcean Hosting Docs", "Refactoring Guru Design Patterns", "The Odin Project"

## Integration with MCP Agents

The `CodingKnowledgeTool` class is designed to integrate with MCP (Model Context Protocol) agent frameworks:

```python
from RAG.coding_knowledge_tool import CodingKnowledgeTool

# In your agent initialization code (where FastMCP is set up)
knowledge_tool = CodingKnowledgeTool(mcp)
# This automatically registers the 'query_knowledge_base' tool

# The agent can now call:
# query_knowledge_base(
#     query="How to fetch data from an API in React",
#     technology_filter="React Docs",
#     n_results=5
# )
```

## Observability

The system is instrumented with **OpenTelemetry** (`telemetry_setup.py`):

- **Traces**: Detailed query execution spans with attributes (query text, filters, results count)
- **Metrics**:
  - `rag.queries.total`: Total query counter
  - `rag.queries.no_results`: Queries returning empty results
  - `rag.query.latency`: Query duration histogram (milliseconds)

By default, telemetry exports to console. For production, configure OTLP exporters for Jaeger/Prometheus.

## File Processing Details

### Metadata Enrichment

During ingestion, each chunk receives metadata:
- `technology`: Extracted from `targets.json` based on file path
- `source_url`: Original URL from `targets.json`
- `source_file`: Absolute path to the source file

### Incremental Processing

The `ingest.py` script tracks processed files to avoid reprocessing:
1. Queries ChromaDB for all existing `source_file` metadata values
2. Filters out already-processed files
3. Only embeds and stores new files

This allows safe re-runs after adding new data sources.

## Important Notes

- **ChromaDB Server Requirement**: This system uses ChromaDB in server mode (HTTP client), NOT embedded mode. The server must be running at `localhost:8001` for all operations.

- **Embedding Model**: Uses `all-MiniLM-L6-v2` from Sentence Transformers. This model runs locally and does not require API keys.

- **Chunking Strategy**: 1000 characters per chunk with 150-character overlap balances context size and retrieval granularity.

- **File Filtering**: The ingestion pipeline excludes `tokenizer.json` files (not semantic content) and ignores read errors on individual files.

- **Adding New Sources**:
  1. Edit `targets.json` to add new git repos or websites
  2. Run `acquisition_agent.py` to download
  3. Run `ingest.py` to process and embed
  4. No need to rebuild existing data

## Configuration Constants

If you need to modify system behavior, key constants are at the top of each script:

**`ingest.py`**:
- `CHROMA_HOST`, `CHROMA_PORT`: ChromaDB server location
- `COLLECTION_NAME`: Vector DB collection name
- `EMBEDDING_MODEL_NAME`: Sentence Transformers model
- `CHUNK_SIZE`, `CHUNK_OVERLAP`: Text splitting parameters

**`coding_knowledge_tool.py`**:
- Same ChromaDB and embedding model constants
- Default `n_results=5` in query method

**`acquisition_agent.py`**:
- `DATA_DIR`, `REPOS_DIR`, `SCRAPED_DIR`: Data storage paths
