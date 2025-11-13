# RAG System - Pre-Flight Checklist

**Date**: _______________
**Operator**: _______________
**Purpose**: Verify system readiness before implementation

---

## System Requirements ✓

### Hardware
- [ ] **CPU**: AMD 9950X (16C/32T) or equivalent
- [ ] **RAM**: 128GB+ available
- [ ] **Storage**: 50GB+ free on /mnt/nvme-fast
- [ ] **GPU**: AMD 7900 XTX (optional, for acceleration)

**Verification Commands:**
```bash
lscpu | grep "Model name"
free -h | grep "Mem:"
df -h /mnt/nvme-fast
lspci | grep -i vga
```

---

## Software Dependencies ✓

### Operating System
- [ ] **Ubuntu 24.04.03 LTS** (kernel 6.8+)
- [ ] **System up to date**: `sudo apt update && sudo apt upgrade`

### Core Tools
- [ ] **Python 3.8-3.12**: `python3 --version`
- [ ] **Docker 24.0+**: `docker --version`
- [ ] **Docker Compose**: `docker-compose --version` or `docker compose version`
- [ ] **Git**: `git --version`

### Python Packages (in venv)
```bash
cd /home/rebelsts/RAG
./.venv/bin/pip list | grep -E "chromadb|langchain|sentence-transformers|fastmcp"
```
- [ ] chromadb >= 0.6.0
- [ ] langchain >= 1.0.0
- [ ] sentence-transformers >= 2.5.0
- [ ] fastmcp >= 0.3.0

---

## Network & Ports ✓

### Port Availability
```bash
sudo lsof -i :8001  # ChromaDB
sudo lsof -i :6379  # Redis
sudo lsof -i :8080  # MCP Server (if HTTP)
```
- [ ] **Port 8001**: Available for ChromaDB
- [ ] **Port 6379**: Available for Redis (or Redis already running)
- [ ] **Port 8080**: Available for MCP HTTP (optional)

### Network Configuration
- [ ] **Internet access**: `ping -c 3 google.com`
- [ ] **Docker network**: Can create bridge networks

---

## Storage & Permissions ✓

### Directory Structure
```bash
cd /home/rebelsts/RAG
ls -la
```
- [ ] **Project root exists**: /home/rebelsts/RAG
- [ ] **Virtual environment**: .venv/ directory
- [ ] **Data directory**: data/ (with repos/ and scraped/)
- [ ] **Scripts directory**: scripts/

### NVMe Storage
```bash
ls -la /mnt/nvme-fast
touch /mnt/nvme-fast/test_write && rm /mnt/nvme-fast/test_write
```
- [ ] **/mnt/nvme-fast mounted**: Directory exists
- [ ] **Write permissions**: Can create/delete files
- [ ] **50GB+ free space**: `df -h /mnt/nvme-fast`

### Docker Volumes
```bash
mkdir -p /mnt/nvme-fast/docker-volumes/chromadb
mkdir -p /mnt/nvme-fast/backups/chromadb
```
- [ ] **Volume directory created**
- [ ] **Backup directory created**
- [ ] **Correct ownership**: `ls -la /mnt/nvme-fast/docker-volumes`

---

## Configuration Files ✓

### Required Files
- [ ] **targets.json**: Exists and valid JSON
- [ ] **docker-compose.yml**: Exists and valid YAML
- [ ] **acquisition_agent.py**: Python script exists
- [ ] **ingest.py**: Python script exists
- [ ] **mcp_server/rag_server.py**: MCP server script exists

### Validation
```bash
python3 -m json.tool targets.json >/dev/null && echo "✓ targets.json valid"
docker-compose config >/dev/null && echo "✓ docker-compose.yml valid"
python3 -m py_compile ingest.py && echo "✓ ingest.py syntax OK"
```

---

## Data Acquisition ✓

### Source Material
```bash
find data/repos -maxdepth 1 -type d | wc -l
find data/scraped -maxdepth 1 -type d | wc -l
find data -type f \( -name "*.md" -o -name "*.py" -o -name "*.js" \) | wc -l
```
- [ ] **10+ git repositories cloned**
- [ ] **30+ documentation sites scraped**
- [ ] **1000+ source files total**

**If not acquired:**
```bash
./.venv/bin/python acquisition_agent.py
```

---

## Optional: GPU Acceleration ✓

### ROCm Setup (AMD GPU)
```bash
rocm-smi
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```
- [ ] **ROCm installed**: rocm-smi shows GPU
- [ ] **PyTorch with ROCm**: torch.cuda.is_available() returns True
- [ ] **User in groups**: `groups | grep -q "render\|video"`

**If not working, GPU acceleration will be skipped (CPU fallback available)**

---

## Security Considerations ✓

### System Security
- [ ] **Firewall configured**: UFW or iptables rules set
- [ ] **SSH secured**: Key-based auth, no root login
- [ ] **System updates**: All security patches applied

### Application Security
- [ ] **Strong passwords ready**: For ChromaDB auth (16+ chars)
- [ ] **Backup plan**: Know where backups will be stored
- [ ] **Recovery plan**: Reviewed EMERGENCY_RECOVERY.md

---

## Pre-Implementation Tests ✓

### Quick Validation
```bash
# Run Phase 1 validation
./scripts/validate-phase1-foundation.sh
```
- [ ] **Validation passes**: Success rate >= 85%
- [ ] **All critical checks pass**: No red ✗ on critical items

### Docker Test
```bash
docker run --rm hello-world
docker-compose up -d chromadb
sleep 10
curl http://localhost:8001/api/v2/heartbeat
docker-compose down
```
- [ ] **Docker works**: hello-world runs successfully
- [ ] **ChromaDB starts**: Health check passes
- [ ] **Port binding works**: No errors

---

## Knowledge Transfer ✓

### Documentation Review
- [ ] **Read**: README.md
- [ ] **Read**: QUICKSTART.md
- [ ] **Read**: IMPLEMENTATION_WORKFLOW.md
- [ ] **Review**: RISK_MITIGATION_GUIDE.md
- [ ] **Bookmark**: EMERGENCY_RECOVERY.md

### Team Notification
- [ ] **Team informed**: Implementation starting
- [ ] **Maintenance window**: Scheduled (if applicable)
- [ ] **Contact info**: Emergency contacts available

---

## Final Go/No-Go Decision ✓

### Critical Requirements (Must Pass All)
- [ ] System requirements met (CPU, RAM, Disk)
- [ ] All dependencies installed
- [ ] Ports available
- [ ] Storage accessible with write permissions
- [ ] Configuration files valid
- [ ] Data acquired

### Optional Enhancements (Nice to Have)
- [ ] GPU acceleration ready
- [ ] Redis installed
- [ ] Monitoring tools available

### Overall Status

**Ready to Proceed**: YES / NO

**If NO, what's blocking:**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Estimated Fix Time**: _______________

**Go/No-Go Decision**: _______________

**Approved By**: _______________

**Start Time**: _______________

---

## Post-Checklist Actions

### If Ready (YES):
1. Start with Phase 1: Foundation
2. Run: `./scripts/validate-phase1-foundation.sh` after each major step
3. Document any deviations or issues
4. Take note of actual times vs. estimated times

### If Not Ready (NO):
1. Fix blocking issues
2. Re-run pre-flight checklist
3. Get approval before proceeding
4. Document reasons for delay

---

## Quick Reference Commands

```bash
# Project directory
cd /home/rebelsts/RAG

# Activate virtual environment
source .venv/bin/activate

# Check system status
./scripts/validate-all-phases.sh

# Start ChromaDB
docker-compose up -d chromadb

# Check logs
docker logs -f chromadb-server

# Emergency stop
docker-compose down

# Get help
cat EMERGENCY_RECOVERY.md
```

---

**Checklist Version**: 1.0
**Last Updated**: 2025-11-13
**Review Before**: Every implementation
**Archive After**: Implementation complete

---

## Sign-Off

**Pre-Flight Checklist Completed By:**

Name: _______________
Date: _______________
Time: _______________

**Implementation Authorized By:**

Name: _______________
Date: _______________
Signature: _______________

---

**Save this checklist for your records after completion**
