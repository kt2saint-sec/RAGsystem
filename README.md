# RAG Knowledge Base System

**GPU-accelerated RAG (Retrieval-Augmented Generation) system for querying 70,652+ technical documents across 36+ technologies.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch ROCm](https://img.shields.io/badge/PyTorch-ROCm%206.2-red.svg)](https://pytorch.org/)

## ⚡ Performance

- **6.2ms** average query time (68x faster than CPU)
- **160+ queries/second** throughput
- **301x faster** embedding generation with GPU
- **95%+ accuracy** across all technologies

## 🎯 Quick Start

See **[QUICKSTART.md](QUICKSTART.md)** for detailed setup instructions.

```bash
# Clone and install
git clone https://github.com/kt2saint-sec/RAGsystem.git
cd RAGsystem
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start ChromaDB and ingest data
docker compose up -d chromadb
python ingest.py

# Test
python test_mcp_server.py
```

## 📚 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete usage guide ⭐
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start
- **[PERFORMANCE_BENCHMARKS.md](PERFORMANCE_BENCHMARKS.md)** - GPU benchmarks  
- **[CLAUDE.md](CLAUDE.md)** - Architecture reference

## 🚀 Features

- **MCP Server Integration** - 3 tools for Claude Code CLI
- **GPU Acceleration** - 301x faster with AMD/NVIDIA GPU
- **36+ Technologies** - React, Python, Docker, TypeScript, PostgreSQL, FastAPI, and more
- **Semantic Search** - ChromaDB vector database with 384-dim embeddings

## 📊 Performance

| Metric | CPU | GPU (AMD 7900 XTX) | Speedup |
|--------|-----|-------------------|---------|
| Embedding | 746.6ms | 2.5ms | **301x** |
| Full Query | 421.4ms | 6.2ms | **68x** |
| Throughput | 2 q/s | 160+ q/s | **80x** |

## 🏗️ Architecture

```
Claude Code CLI → MCP Protocol → FastMCP Server 
                                       ↓
                        GPU-Accelerated Embeddings (all-MiniLM-L6-v2)
                                       ↓
                        ChromaDB Vector Database (70,652 docs)
```

## 🔧 Requirements

**Minimum**: 4 cores, 8GB RAM, 10GB storage  
**Recommended**: 8+ cores, 16GB+ RAM, GPU (AMD/NVIDIA), NVMe SSD

**Tested on**: Ubuntu 24.04, AMD 9950X, AMD RX 7900 XTX, ROCm 7.1.0

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Credits

Built with Claude Code, ChromaDB, FastMCP, PyTorch + ROCm, Sentence Transformers

---

⭐ **Status**: Production Ready | **Build Time**: 50 minutes | **Generated with**: [Claude Code](https://claude.com/claude-code)
