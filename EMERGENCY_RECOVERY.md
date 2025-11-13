# Emergency Recovery Playbook

**Version**: 1.0
**Purpose**: Quick reference guide for emergency situations
**Last Updated**: 2025-11-13

---

## Quick Navigation

- [Emergency #1: ChromaDB Won't Start](#emergency-1-chromadb-wont-start)
- [Emergency #2: MCP Server Not Responding](#emergency-2-mcp-server-not-responding)
- [Emergency #3: Database Corruption](#emergency-3-database-corruption)
- [Emergency #4: Out of Disk Space](#emergency-4-out-of-disk-space)
- [Emergency #5: Authentication Lockout](#emergency-5-authentication-lockout)
- [Emergency #6: Complete System Reset](#emergency-6-complete-system-reset)
- [Diagnostic Commands](#diagnostic-commands)

---

## Emergency #1: ChromaDB Won't Start

**Symptoms:**
- Container fails to start
- Health check continuously failing
- Port binding errors

**Quick Fix (5 minutes):**

```bash
# Step 1: Check what's wrong
docker logs chromadb-server --tail 50

# Step 2: Stop and remove container
docker stop chromadb-server
docker rm chromadb-server

# Step 3: Check port availability
sudo lsof -i :8001
# If port in use, kill process or change port in docker-compose.yml

# Step 4: Restart
docker-compose up -d chromadb

# Step 5: Monitor startup
docker logs -f chromadb-server

# Step 6: Verify health
curl http://localhost:8001/api/v2/heartbeat
```

**If Still Failing:**

```bash
# Check disk space
df -h /mnt/nvme-fast

# Check permissions
ls -la /mnt/nvme-fast/docker-volumes/chromadb

# Fix permissions
sudo chown -R $USER:$USER /mnt/nvme-fast/docker-volumes/chromadb

# Nuclear option: Reset container
docker-compose down
docker volume prune -f
docker-compose up -d
```

**Escalation:**
- Check RISK_MITIGATION_GUIDE.md Issue #4, #5, #6
- Restore from backup (see Emergency #3)

---

## Emergency #2: MCP Server Not Responding

**Symptoms:**
- Claude Code cannot connect to MCP server
- `claude mcp list` shows server as disconnected
- MCP queries timeout

**Quick Fix (10 minutes):**

```bash
# Step 1: Check MCP container status
docker ps | grep mcp-server

# Step 2: Check logs for errors
docker logs rag-mcp-server --tail 50

# Step 3: Verify ChromaDB is accessible from MCP container
docker exec rag-mcp-server curl http://chromadb:8000/api/v2/heartbeat

# Step 4: Restart MCP server
docker restart rag-mcp-server

# Step 5: Wait and verify
sleep 10
docker logs rag-mcp-server --tail 20

# Step 6: Test registration
claude mcp list
```

**If Connection Still Fails:**

```bash
# Check network connectivity
docker network inspect rag-network

# Reconnect containers to network
docker network connect rag-network chromadb-server
docker network connect rag-network rag-mcp-server

# Verify environment variables
docker exec rag-mcp-server env | grep CHROMA

# Rebuild MCP server
docker-compose -f docker-compose-full.yml build mcp-server
docker-compose -f docker-compose-full.yml up -d mcp-server
```

**Fallback: Run MCP Server Directly (Not Containerized):**

```bash
# Stop Docker MCP server
docker stop rag-mcp-server

# Run locally
cd /home/rebelsts/RAG
export CHROMA_HOST=localhost
export CHROMA_PORT=8001
./.venv/bin/python mcp_server/rag_server.py
```

**Escalation:**
- Check RISK_MITIGATION_GUIDE.md Issue #1, #2, #3
- Review mcp_servers.json configuration
- Test with `validate-phase2-mcp.sh`

---

## Emergency #3: Database Corruption

**Symptoms:**
- Queries return errors
- Collection not found
- Data inconsistencies
- ChromaDB crashes during queries

**Quick Fix (20 minutes):**

**Option A: Restore from Latest Backup**

```bash
# Step 1: Stop ChromaDB
docker stop chromadb-server

# Step 2: Find latest backup
ls -lt /mnt/nvme-fast/backups/chromadb/ | head -5
LATEST_BACKUP=$(ls -t /mnt/nvme-fast/backups/chromadb/chromadb_*.tar.gz | head -1)

# Step 3: Backup current (corrupted) database
sudo mv /mnt/nvme-fast/docker-volumes/chromadb /mnt/nvme-fast/docker-volumes/chromadb.corrupted.$(date +%Y%m%d)

# Step 4: Restore from backup
sudo mkdir -p /mnt/nvme-fast/docker-volumes/chromadb
sudo tar -xzf "$LATEST_BACKUP" -C /mnt/nvme-fast/docker-volumes/

# Step 5: Fix permissions
sudo chown -R $USER:$USER /mnt/nvme-fast/docker-volumes/chromadb

# Step 6: Restart ChromaDB
docker start chromadb-server

# Step 7: Verify
sleep 10
curl http://localhost:8001/api/v2/heartbeat
```

**Option B: Rebuild Database from Source**

```bash
# Step 1: Stop and remove ChromaDB
docker stop chromadb-server
docker rm chromadb-server

# Step 2: Clear database directory
sudo rm -rf /mnt/nvme-fast/docker-volumes/chromadb/*

# Step 3: Restart ChromaDB (will create fresh database)
docker-compose up -d chromadb

# Step 4: Wait for healthy
sleep 15
curl http://localhost:8001/api/v2/heartbeat

# Step 5: Re-ingest data (THIS WILL TAKE 30-60 MINUTES)
cd /home/rebelsts/RAG
./.venv/bin/python ingest.py 2>&1 | tee logs/emergency_reingest_$(date +%Y%m%d).log

# Step 6: Verify document count
python3 <<'EOF'
import chromadb
client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_collection("coding_knowledge")
print(f"Documents restored: {collection.count()}")
EOF
```

**Prevention:**
- Set up automated daily backups (see IMPLEMENTATION_WORKFLOW.md Phase 5)
- Test backup restoration monthly

---

## Emergency #4: Out of Disk Space

**Symptoms:**
- Ingestion fails with "No space left on device"
- Docker containers won't start
- Backup jobs failing

**Quick Fix (10 minutes):**

```bash
# Step 1: Check disk usage
df -h
du -sh /mnt/nvme-fast/* | sort -h

# Step 2: Find large files
sudo du -h /mnt/nvme-fast | sort -h | tail -20

# Step 3: Clean Docker
docker system prune -a -f
docker volume prune -f

# Step 4: Clean old backups (keep last 7 days)
find /mnt/nvme-fast/backups/chromadb -name "chromadb_*.tar.gz" -mtime +7 -delete

# Step 5: Clean logs
sudo find /var/log -name "*.log" -mtime +30 -delete
sudo journalctl --vacuum-time=30d

# Step 6: Clean temp files
rm -rf /tmp/*
rm -rf ~/.cache/*

# Step 7: Verify space recovered
df -h /mnt/nvme-fast
```

**If Still Low on Space:**

```bash
# Identify largest directories
sudo du -h --max-depth=2 /mnt/nvme-fast | sort -h | tail -20

# Consider:
# 1. Moving backups to external storage
# 2. Reducing data sources in targets.json
# 3. Adding another drive
# 4. Compressing old data
```

**Prevention:**
- Set up disk space monitoring
- Configure automatic cleanup
- Alert at 80% capacity

---

## Emergency #5: Authentication Lockout

**Symptoms:**
- Cannot access ChromaDB (401 Unauthorized)
- Lost admin password
- htpasswd file corrupted

**Quick Fix (5 minutes):**

**Option A: Disable Authentication Temporarily**

```bash
# Step 1: Stop ChromaDB
docker stop chromadb-server

# Step 2: Edit docker-compose.yml - comment out auth env vars
sed -i 's/CHROMA_SERVER_AUTH/#CHROMA_SERVER_AUTH/g' docker-compose.yml

# Step 3: Restart
docker start chromadb-server

# Step 4: Access without auth
curl http://localhost:8001/api/v2/heartbeat

# Step 5: Reset password
./scripts/setup-auth.sh

# Step 6: Re-enable auth (uncomment in docker-compose.yml)
sed -i 's/#CHROMA_SERVER_AUTH/CHROMA_SERVER_AUTH/g' docker-compose.yml

# Step 7: Restart
docker restart chromadb-server
```

**Option B: Reset Password**

```bash
# Step 1: Generate new password
NEW_PASSWORD="your-new-secure-password"
htpasswd -nbB admin "$NEW_PASSWORD" > /mnt/nvme-fast/docker-volumes/chromadb/server.htpasswd

# Step 2: Restart ChromaDB
docker restart chromadb-server

# Step 3: Update all client configurations with new password
# Edit: ingest.py, mcp_server/rag_server.py, coding_knowledge_tool.py
```

**Prevention:**
- Store password in secure password manager
- Document password recovery procedure
- Set up emergency admin account

---

## Emergency #6: Complete System Reset

**Use Case:** Nuclear option when nothing else works

**⚠️ WARNING: THIS WILL DELETE ALL DATA**

**Reset Procedure (30 minutes):**

```bash
# Step 1: Create emergency backup
mkdir -p /tmp/emergency_backup
cp -r data /tmp/emergency_backup/
cp targets.json /tmp/emergency_backup/

# Step 2: Stop all services
docker-compose -f docker-compose-full.yml down

# Step 3: Remove all Docker resources
docker system prune -a -f --volumes

# Step 4: Clear database
sudo rm -rf /mnt/nvme-fast/docker-volumes/chromadb/*

# Step 5: Reset configuration
mv docker-compose.yml docker-compose.yml.old
mv docker-compose-full.yml docker-compose-full.yml.old

# Step 6: Restore from IMPLEMENTATION_WORKFLOW.md
# Create fresh docker-compose.yml from Phase 1

# Step 7: Start ChromaDB
docker-compose up -d chromadb

# Step 8: Wait for health
sleep 15
curl http://localhost:8001/api/v2/heartbeat

# Step 9: Re-ingest data
./.venv/bin/python ingest.py 2>&1 | tee logs/full_reset_ingest.log

# Step 10: Rebuild MCP server
docker-compose -f docker-compose-full.yml build mcp-server
docker-compose -f docker-compose-full.yml up -d mcp-server

# Step 11: Validate
./scripts/validate-all-phases.sh
```

**Post-Reset Checklist:**
- [ ] ChromaDB health check passing
- [ ] Database has expected document count
- [ ] MCP server responding
- [ ] Claude Code can query MCP server
- [ ] Authentication configured
- [ ] Backups re-enabled
- [ ] Monitoring re-enabled

---

## Diagnostic Commands

### Quick Health Check

```bash
# One-liner health check
echo "ChromaDB: $(curl -sf http://localhost:8001/api/v2/heartbeat && echo 'OK' || echo 'FAIL')"
echo "MCP Server: $(docker ps | grep -q rag-mcp-server && echo 'Running' || echo 'Down')"
echo "Redis: $(redis-cli ping 2>/dev/null || echo 'Not running')"
```

### View All Logs

```bash
# Docker logs
docker-compose logs -f --tail=100

# System logs
sudo journalctl -xe -n 100

# Backup logs
tail -50 /var/log/chromadb-backup.log

# Health check logs
tail -50 /var/log/rag-health.log
```

### Check Resource Usage

```bash
# Docker stats
docker stats --no-stream

# Disk usage
df -h

# Memory usage
free -h

# CPU usage
top -bn1 | head -20
```

### Test Connectivity

```bash
# ChromaDB
curl -v http://localhost:8001/api/v2/heartbeat

# MCP to ChromaDB
docker exec rag-mcp-server curl http://chromadb:8000/api/v2/heartbeat

# Redis
redis-cli ping

# Network
docker network inspect rag-network
```

### Check Configuration

```bash
# Docker Compose
docker-compose config

# Environment variables
docker exec rag-mcp-server env

# MCP configuration
cat ~/.config/claude-code/mcp_servers.json | python3 -m json.tool

# Cron jobs
crontab -l
```

---

## Emergency Contacts

**System Owner:** [Your Name]
**Email:** [Your Email]
**Phone:** [Your Phone]

**Escalation Path:**
1. Check this playbook
2. Check RISK_MITIGATION_GUIDE.md
3. Run validation scripts
4. Review logs
5. Contact system owner

**External Resources:**
- ChromaDB Discord: https://discord.gg/MMeYNTmh3x
- FastMCP GitHub Issues: https://github.com/jlowin/fastmcp/issues
- Claude API Support: support@anthropic.com

---

## Recovery Time Objectives (RTO)

| Emergency | Target RTO | Actual Time | Data Loss |
|-----------|-----------|-------------|-----------|
| ChromaDB won't start | 5 minutes | Varies | None |
| MCP server issues | 10 minutes | Varies | None |
| Database corruption | 20 minutes (with backup) | 20-30 min | Minimal |
| Out of disk space | 10 minutes | Varies | None |
| Auth lockout | 5 minutes | Varies | None |
| Complete reset | 30 minutes | 30-60 min | Rebuild from source |

---

**Last Updated**: 2025-11-13
**Review Schedule**: Monthly
**Next Review**: 2025-12-13
