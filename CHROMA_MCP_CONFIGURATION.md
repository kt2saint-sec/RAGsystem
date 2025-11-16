# ChromaDB MCP Server Configuration Guide

## Overview

You're configuring the **Chroma MCP server** in Docker Desktop MCP Toolkit to connect to your **local ChromaDB** running at `localhost:8001`.

---

## Configuration Steps (Docker Desktop UI)

### 1. Open Docker Desktop MCP Toolkit
- Open Docker Desktop
- Navigate to **MCP Toolkit** tab (left sidebar)
- Find **Chroma** in the server list
- Click **Configuration** tab

### 2. Configure Secrets

In the **Secrets** section, fill in:

**Field: `chroma_api_key`**
```
local-no-auth-required
```

**Why this value?**
- Your local ChromaDB runs **without authentication**
- The Docker Desktop UI requires *something* in this field
- This placeholder value satisfies the UI requirement
- The actual connection uses environment variables, not this API key

---

## Environment Variables (Already Configured)

I've added these to `~/.claude/.env.mcp`:

```bash
# ChromaDB MCP Server Configuration (HTTP Client for Local ChromaDB)
CHROMA_CLIENT_TYPE=http
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_SSL=false
CHROMA_API_KEY=local-no-auth-required
```

These variables tell the Chroma MCP server:
- **Type**: Use HTTP client (not Cloud, not Persistent)
- **Host**: Connect to localhost
- **Port**: Use port 8001 (where your ChromaDB Docker container is listening)
- **SSL**: Disabled (local development)
- **API Key**: Placeholder (authentication not enabled)

---

## Testing the Connection

### Method 1: Docker Desktop MCP Toolkit UI

After configuring:
1. Click **"Save"** or **"Apply"** in Docker Desktop
2. Look for status indicator (should show green/connected)
3. Check **Tools** tab to see available Chroma MCP tools

### Method 2: Test via Claude Code CLI

```bash
# The Chroma MCP server should now be available to Claude Code
# Test by asking Claude to list ChromaDB collections
```

Example query:
```
"List all ChromaDB collections using the Chroma MCP server"
```

Expected tools available:
- `chroma_create_collection`
- `chroma_list_collections`
- `chroma_get_collection`
- `chroma_add_documents`
- `chroma_query_collection`
- `chroma_update_documents`
- `chroma_delete_documents`
- ...and 5 more tools

---

## Verify ChromaDB is Running

Before using the MCP server, ensure your ChromaDB Docker container is running:

```bash
# Check container status
docker ps | grep chromadb-server

# Expected output:
# 11c6924fe834   chromadb/chroma:latest   ...   Up X minutes   0.0.0.0:8001->8000/tcp   chromadb-server

# Test heartbeat
curl http://localhost:8001/api/v2/heartbeat

# Expected output:
# {"nanosecond heartbeat":1763140168152516319}
```

---

## Common Issues & Solutions

### Issue 1: "Connection Refused"

**Symptoms**: MCP server can't connect to ChromaDB

**Solutions**:
1. Verify ChromaDB container is running:
   ```bash
   docker start chromadb-server
   ```

2. Check port is accessible:
   ```bash
   curl http://localhost:8001/api/v2/heartbeat
   ```

3. Verify Docker network settings (ensure localhost binding)

---

### Issue 2: "Authentication Required"

**Symptoms**: Error about missing or invalid credentials

**Solutions**:
1. Our ChromaDB runs **without authentication** (default)
2. Ensure `CHROMA_API_KEY` is set to `local-no-auth-required` (placeholder)
3. Verify `CHROMA_CLIENT_TYPE=http` (not `cloud`)

---

### Issue 3: "Wrong Port"

**Symptoms**: Connection timeout or wrong endpoint

**Solutions**:
1. ChromaDB container **listens on port 8000 internally**
2. Mapped to **port 8001 externally**: `0.0.0.0:8001->8000/tcp`
3. MCP server should connect to **port 8001** (external mapping)

---

## Advanced: Using Chroma Cloud Instead

If you later migrate to Chroma Cloud (managed service):

**Update `.env.mcp`**:
```bash
CHROMA_CLIENT_TYPE=cloud
CHROMA_TENANT=your-tenant-id
CHROMA_DATABASE=your-database-name
CHROMA_API_KEY=your-actual-chroma-cloud-api-key
```

**Docker Desktop UI**:
- Enter your **actual Chroma Cloud API key** in `chroma_api_key` field

---

## Current RAG Ingestion Status

While configuring this, your ingestion is running in the background:

**Check progress**:
```bash
# Batch 6
tail -f /home/rebelsts/RAG/batch_6_ingestion_clean.log | grep "Stored batch"

# Batch 7
tail -f /home/rebelsts/RAG/batch_7_ingestion_clean.log | grep "Stored batch"

# Quick count
grep -c "Stored batch" /home/rebelsts/RAG/batch_*_clean.log
```

**Current data**:
- Collection: `coding_knowledge`
- ChromaDB: `http://localhost:8001`
- Data directory: `/mnt/nvme-fast/docker-volumes/chromadb/`

---

## Next Steps

1. ✅ Environment variables configured in `~/.claude/.env.mcp`
2. ⏳ **You**: Enter `local-no-auth-required` in Docker Desktop UI (`chroma_api_key` field)
3. ⏳ **You**: Save configuration in Docker Desktop
4. ⏳ Test connection by asking Claude Code to list collections

Once configured, you'll be able to:
- Query your RAG knowledge base via MCP tools
- Add/update/delete collections programmatically
- Use ChromaDB directly from Claude Code conversations
- Build more advanced RAG workflows

---

## Documentation References

- **ChromaDB Cookbook**: https://cookbook.chromadb.dev/
- **Chroma MCP Server GitHub**: https://github.com/chroma-core/chroma-mcp
- **MCP Protocol Docs**: https://modelcontextprotocol.io/
- **Docker Desktop MCP Toolkit**: Managed via Docker Desktop UI
