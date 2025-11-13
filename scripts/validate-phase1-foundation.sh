#!/bin/bash
# File: /home/rebelsts/RAG/scripts/validate-phase1-foundation.sh
# Purpose: Validate Phase 1 (Foundation) requirements and deployment
# Usage: ./validate-phase1-foundation.sh

set -uo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((CHECKS_WARNING++))
}

info() {
    echo -e "  $1"
}

echo "================================================================"
echo "  RAG System - Phase 1 (Foundation) Validation"
echo "================================================================"
echo ""

# Check 1: System Requirements
echo "[ System Requirements ]"

# Check Python version
if python3 --version | grep -qE "Python 3\.(8|9|10|11|12)"; then
    pass "Python 3.8+ installed: $(python3 --version)"
else
    fail "Python version not compatible: $(python3 --version)"
fi

# Check disk space
NVME_AVAIL=$(df -BG /mnt/nvme-fast 2>/dev/null | tail -1 | awk '{print $4}' | sed 's/G//' || echo "0")
if [ "$NVME_AVAIL" -gt 50 ]; then
    pass "NVMe storage available: ${NVME_AVAIL}GB"
else
    fail "Insufficient NVMe storage: ${NVME_AVAIL}GB (need 50GB+)"
fi

# Check RAM
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -ge 64 ]; then
    pass "RAM available: ${TOTAL_RAM}GB"
else
    warn "Low RAM: ${TOTAL_RAM}GB (recommended 64GB+)"
fi

echo ""

# Check 2: Dependencies
echo "[ Dependencies ]"

# Check virtual environment
if [ -d ".venv" ]; then
    pass "Virtual environment exists"

    # Check Python packages
    REQUIRED_PACKAGES=("chromadb" "langchain" "sentence-transformers" "beautifulsoup4" "requests" "gitpython")
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if ./.venv/bin/pip show "$pkg" &>/dev/null; then
            pass "Package installed: $pkg"
        else
            fail "Package missing: $pkg"
        fi
    done
else
    fail "Virtual environment not found"
fi

echo ""

# Check 3: Docker
echo "[ Docker Environment ]"

# Check Docker is installed
if command -v docker &>/dev/null; then
    pass "Docker installed: $(docker --version | cut -d' ' -f3 | tr -d ',')"
else
    fail "Docker not installed"
fi

# Check Docker is running
if docker ps &>/dev/null; then
    pass "Docker daemon running"
else
    fail "Docker daemon not running"
fi

# Check docker-compose
if command -v docker-compose &>/dev/null; then
    pass "docker-compose installed"
else
    warn "docker-compose not found (may use 'docker compose' instead)"
fi

echo ""

# Check 4: Port Availability
echo "[ Port Availability ]"

# Check port 8001 (ChromaDB)
if ! sudo lsof -i :8001 &>/dev/null && ! sudo ss -tlnp | grep -q ":8001 "; then
    pass "Port 8001 available"
else
    warn "Port 8001 in use: $(sudo lsof -ti :8001 | xargs -r ps -p | tail -1)"
    info "  Mitigation: Use different port or stop conflicting service"
fi

# Check port 6379 (Redis)
if ! sudo lsof -i :6379 &>/dev/null && ! sudo ss -tlnp | grep -q ":6379 "; then
    pass "Port 6379 available"
else
    info "Port 6379 in use (expected if Redis running)"
fi

echo ""

# Check 5: Storage Permissions
echo "[ Storage Permissions ]"

# Check NVMe mount exists
if [ -d "/mnt/nvme-fast" ]; then
    pass "NVMe mount point exists"

    # Check write permissions
    if touch /mnt/nvme-fast/test_write 2>/dev/null && rm /mnt/nvme-fast/test_write 2>/dev/null; then
        pass "Write permissions to /mnt/nvme-fast"
    else
        fail "No write permissions to /mnt/nvme-fast"
        info "  Mitigation: sudo chown -R $USER:$USER /mnt/nvme-fast"
    fi

    # Check docker volume directory
    if [ -d "/mnt/nvme-fast/docker-volumes" ]; then
        pass "Docker volumes directory exists"
    else
        warn "Docker volumes directory missing"
        info "  Creating: mkdir -p /mnt/nvme-fast/docker-volumes/chromadb"
    fi
else
    fail "NVMe mount point not found"
    info "  Mitigation: Mount NVMe drive or use alternative path"
fi

echo ""

# Check 6: Configuration Files
echo "[ Configuration Files ]"

# Check docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"

    # Validate YAML syntax
    if docker-compose config &>/dev/null 2>&1; then
        pass "docker-compose.yml syntax valid"
    else
        fail "docker-compose.yml has syntax errors"
        info "  Run: docker-compose config"
    fi
else
    fail "docker-compose.yml not found"
    info "  Mitigation: Create from IMPLEMENTATION_WORKFLOW.md Phase 1"
fi

# Check targets.json
if [ -f "targets.json" ]; then
    pass "targets.json exists"

    # Validate JSON syntax
    if python3 -m json.tool targets.json >/dev/null 2>&1; then
        pass "targets.json syntax valid"

        # Count targets
        TARGET_COUNT=$(python3 -c "import json; print(len(json.load(open('targets.json'))))")
        info "  Targets configured: $TARGET_COUNT"
    else
        fail "targets.json has syntax errors"
    fi
else
    fail "targets.json not found"
fi

echo ""

# Check 7: Data Acquisition Status
echo "[ Data Acquisition ]"

# Check data directory
if [ -d "data" ]; then
    pass "Data directory exists"

    # Count repos
    if [ -d "data/repos" ]; then
        REPO_COUNT=$(find data/repos -maxdepth 1 -type d 2>/dev/null | wc -l)
        ((REPO_COUNT--)) # Subtract the data/repos directory itself
        if [ $REPO_COUNT -gt 0 ]; then
            pass "Git repositories acquired: $REPO_COUNT"
        else
            warn "No git repositories found"
        fi
    fi

    # Count scraped sites
    if [ -d "data/scraped" ]; then
        SCRAPED_COUNT=$(find data/scraped -maxdepth 1 -type d 2>/dev/null | wc -l)
        ((SCRAPED_COUNT--))
        if [ $SCRAPED_COUNT -gt 0 ]; then
            pass "Documentation sites scraped: $SCRAPED_COUNT"
        else
            warn "No scraped documentation found"
        fi
    fi

    # Count total files
    FILE_COUNT=$(find data -type f \( -name "*.md" -o -name "*.py" -o -name "*.js" -o -name "*.ts" \) 2>/dev/null | wc -l)
    if [ $FILE_COUNT -gt 100 ]; then
        pass "Total source files: $FILE_COUNT"
    else
        warn "Low file count: $FILE_COUNT (expected 1000+)"
        info "  Mitigation: Run ./venv/bin/python acquisition_agent.py"
    fi
else
    warn "Data directory not found - acquisition not run"
    info "  Next step: Run acquisition_agent.py"
fi

echo ""

# Check 8: ChromaDB Deployment
echo "[ ChromaDB Deployment ]"

# Check if container exists
if docker ps -a | grep -q "chromadb-server"; then
    pass "ChromaDB container exists"

    # Check if running
    if docker ps | grep -q "chromadb-server"; then
        pass "ChromaDB container running"

        # Check health
        if curl -sf http://localhost:8001/api/v2/heartbeat >/dev/null 2>&1; then
            pass "ChromaDB health check passing"

            # Check collection exists
            COLLECTION_CHECK=$(docker exec chromadb-server curl -sf http://localhost:8000/api/v1/collections 2>/dev/null || echo "")
            if echo "$COLLECTION_CHECK" | grep -q "coding_knowledge"; then
                pass "Collection 'coding_knowledge' exists"

                # Try to get count (may fail if not ingested yet)
                info "  Ready for queries"
            else
                warn "Collection not created yet - ingestion needed"
                info "  Next step: Run ./venv/bin/python ingest.py"
            fi
        else
            fail "ChromaDB health check failed"
            info "  Check logs: docker logs chromadb-server"
        fi
    else
        warn "ChromaDB container not running"
        info "  Start: docker-compose up -d chromadb"
    fi
else
    warn "ChromaDB container not deployed"
    info "  Deploy: docker-compose up -d"
fi

echo ""

# Summary
echo "================================================================"
echo "  Validation Summary"
echo "================================================================"
echo -e "${GREEN}Passed:${NC}   $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARNING"
echo -e "${RED}Failed:${NC}   $CHECKS_FAILED"
echo ""

# Calculate success rate
TOTAL_CHECKS=$((CHECKS_PASSED + CHECKS_FAILED))
if [ $TOTAL_CHECKS -gt 0 ]; then
    SUCCESS_RATE=$(awk "BEGIN {printf \"%.0f\", ($CHECKS_PASSED/$TOTAL_CHECKS)*100}")
    echo "Success Rate: ${SUCCESS_RATE}%"

    if [ $SUCCESS_RATE -ge 90 ]; then
        echo -e "${GREEN}✓ Phase 1 ready to proceed${NC}"
        exit 0
    elif [ $SUCCESS_RATE -ge 70 ]; then
        echo -e "${YELLOW}⚠ Phase 1 has warnings - review and fix${NC}"
        exit 1
    else
        echo -e "${RED}✗ Phase 1 validation failed - fix critical issues${NC}"
        exit 1
    fi
else
    echo "No checks were performed"
    exit 1
fi
