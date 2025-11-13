# RAG System - Errors and Issues Log

**Purpose**: Track all errors, warnings, and issues encountered during implementation for later review

---

## Phase 1: Foundation & Database Initialization

### Issues Encountered:

#### Issue #1: Permission Denied Creating Backup Directory
- **Time**: 2025-11-13 16:14
- **Command**: `mkdir -p /mnt/nvme-fast/backups/chromadb`
- **Error**: `Permission denied`
- **Root Cause**: /mnt/nvme-fast/backups requires sudo to create
- **Resolution**: Used `sudo mkdir` and `sudo chown -R rebelsts:rebelsts`
- **Status**: ✅ RESOLVED

#### Issue #2: ChromaDB Version Incompatibility
- **Time**: 2025-11-13 16:15
- **Command**: `python ingest.py`
- **Error**: `KeyError('_type')` - HTTP 500 from ChromaDB server
- **Root Cause**: ChromaDB Python client v1.3.4 incompatible with server v0.6.3
- **Details**: Client expects newer API format that server 0.6.3 doesn't provide
- **Resolution**: Upgraded Docker image from 0.6.3 to latest (1.x compatible)
- **Status**: ✅ RESOLVED

#### Issue #3: DirectoryLoader file_filter Parameter Not Supported
- **Time**: 2025-11-13 16:17
- **Command**: `python ingest.py`
- **Error**: `DirectoryLoader.__init__() got an unexpected keyword argument 'file_filter'`
- **Root Cause**: Langchain version doesn't support file_filter parameter
- **Details**: All file loading failing due to unsupported parameter
- **Resolution**: Removed file_filter parameter from ingest.py (line 121)
- **Status**: ✅ RESOLVED
- **Verification**: Ingestion completed successfully with 70,652 chunks

---

## Phase 2: MCP Integration

### Issues Encountered:

(Not started)

---

## Phase 3: Optimization & Performance

### Issues Encountered:

(Not started)

---

## Phase 4: Testing & Validation

### Issues Encountered:

(Not started)

---

## Phase 5: Production Hardening

### Issues Encountered:

(Not started)

---

## Phase 6: Documentation

### Issues Encountered:

(Not started)

---

## Summary

**Total Issues**: 3
**Critical**: 0
**Warnings**: 2
**Resolved**: 3
**Remaining**: 0

### Phase 1 Issues Summary:
- All issues successfully resolved
- No blocking errors remaining
- System fully operational
