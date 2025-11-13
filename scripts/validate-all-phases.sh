#!/bin/bash
# File: /home/rebelsts/RAG/scripts/validate-all-phases.sh
# Purpose: Run all phase validations in sequence
# Usage: ./validate-all-phases.sh

set -uo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "================================================================"
echo "  RAG System - Complete Validation Suite"
echo "================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"  # Go to project root

# Phase 1: Foundation
echo -e "${BLUE}Running Phase 1 Validation...${NC}"
if [ -f "scripts/validate-phase1-foundation.sh" ]; then
    ./scripts/validate-phase1-foundation.sh
    PHASE1_RESULT=$?
else
    echo -e "${RED}Phase 1 validation script not found${NC}"
    PHASE1_RESULT=1
fi

echo ""
echo "Press Enter to continue to Phase 2..."
read

# Phase 2: MCP Integration
echo -e "${BLUE}Running Phase 2 Validation...${NC}"
if [ -f "scripts/validate-phase2-mcp.sh" ]; then
    ./scripts/validate-phase2-mcp.sh
    PHASE2_RESULT=$?
else
    echo -e "${RED}Phase 2 validation script not found${NC}"
    PHASE2_RESULT=1
fi

echo ""
echo "Press Enter to continue to Phase 3..."
read

# Phase 3: Optimization (Quick checks)
echo -e "${BLUE}Running Phase 3 Checks (Optimization)...${NC}"

PHASE3_CHECKS=0
PHASE3_PASSED=0

# Check GPU
((PHASE3_CHECKS++))
if python3 -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} GPU acceleration available"
    ((PHASE3_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} GPU acceleration not available (will use CPU)"
fi

# Check Redis
((PHASE3_CHECKS++))
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✓${NC} Redis caching available"
    ((PHASE3_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Redis not available (caching disabled)"
fi

if [ $PHASE3_PASSED -eq $PHASE3_CHECKS ]; then
    PHASE3_RESULT=0
else
    PHASE3_RESULT=1
fi

echo ""
echo "Press Enter to continue to Phase 5..."
read

# Phase 5: Production (Quick checks)
echo -e "${BLUE}Running Phase 5 Checks (Production Hardening)...${NC}"

PHASE5_CHECKS=0
PHASE5_PASSED=0

# Check backups configured
((PHASE5_CHECKS++))
if crontab -l 2>/dev/null | grep -q "backup-chromadb"; then
    echo -e "${GREEN}✓${NC} Automated backups configured"
    ((PHASE5_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Automated backups not configured"
fi

# Check health monitoring
((PHASE5_CHECKS++))
if crontab -l 2>/dev/null | grep -q "health-check"; then
    echo -e "${GREEN}✓${NC} Health monitoring configured"
    ((PHASE5_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Health monitoring not configured"
fi

# Check authentication
((PHASE5_CHECKS++))
if [ -f "/mnt/nvme-fast/docker-volumes/chromadb/server.htpasswd" ]; then
    echo -e "${GREEN}✓${NC} Authentication credentials configured"
    ((PHASE5_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Authentication not enabled"
fi

if [ $PHASE5_PASSED -eq $PHASE5_CHECKS ]; then
    PHASE5_RESULT=0
else
    PHASE5_RESULT=1
fi

echo ""
echo "================================================================"
echo "  Overall Results"
echo "================================================================"

# Display results
if [ $PHASE1_RESULT -eq 0 ]; then
    echo -e "Phase 1 (Foundation):       ${GREEN}PASS${NC}"
else
    echo -e "Phase 1 (Foundation):       ${RED}FAIL${NC}"
fi

if [ $PHASE2_RESULT -eq 0 ]; then
    echo -e "Phase 2 (MCP Integration):  ${GREEN}PASS${NC}"
else
    echo -e "Phase 2 (MCP Integration):  ${RED}FAIL${NC}"
fi

if [ $PHASE3_RESULT -eq 0 ]; then
    echo -e "Phase 3 (Optimization):     ${GREEN}PASS${NC}"
else
    echo -e "Phase 3 (Optimization):     ${YELLOW}PARTIAL${NC}"
fi

if [ $PHASE5_RESULT -eq 0 ]; then
    echo -e "Phase 5 (Production):       ${GREEN}PASS${NC}"
else
    echo -e "Phase 5 (Production):       ${YELLOW}PARTIAL${NC}"
fi

echo ""

# Overall status
if [ $PHASE1_RESULT -eq 0 ] && [ $PHASE2_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ System is operational and ready for production use${NC}"
    exit 0
else
    echo -e "${RED}✗ Some phases failed - review and fix issues${NC}"
    exit 1
fi
