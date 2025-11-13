#!/bin/bash
# File: /home/rebelsts/RAG/scripts/validate-phase2-mcp.sh
# Purpose: Validate Phase 2 (MCP Integration) requirements and deployment
# Usage: ./validate-phase2-mcp.sh

set -uo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
echo "  RAG System - Phase 2 (MCP Integration) Validation"
echo "================================================================"
echo ""

# Check 1: Prerequisites (Phase 1 Complete)
echo "[ Prerequisites ]"

# ChromaDB must be running
if curl -sf http://localhost:8001/api/v2/heartbeat >/dev/null 2>&1; then
    pass "ChromaDB server is healthy"
else
    fail "ChromaDB server not accessible"
    info "  Run Phase 1 validation first"
    exit 1
fi

# Database must have data
COLLECTION_EXISTS=$(curl -sf http://localhost:8001/api/v1/collections 2>/dev/null | grep -c "coding_knowledge" || echo "0")
if [ "$COLLECTION_EXISTS" -gt 0 ]; then
    pass "Knowledge base collection exists"
else
    fail "Knowledge base not ingested"
    info "  Run: ./venv/bin/python ingest.py"
    exit 1
fi

echo ""

# Check 2: MCP Server Files
echo "[ MCP Server Files ]"

# Check directory
if [ -d "mcp_server" ]; then
    pass "MCP server directory exists"

    # Check main server file
    if [ -f "mcp_server/rag_server.py" ]; then
        pass "rag_server.py exists"

        # Validate Python syntax
        if python3 -m py_compile mcp_server/rag_server.py 2>/dev/null; then
            pass "rag_server.py syntax valid"
        else
            fail "rag_server.py has syntax errors"
            info "  Check: python3 -m py_compile mcp_server/rag_server.py"
        fi

        # Check for required imports
        if grep -q "from fastmcp import FastMCP" mcp_server/rag_server.py; then
            pass "FastMCP import present"
        else
            fail "FastMCP import missing"
        fi

        if grep -q "@mcp.tool" mcp_server/rag_server.py; then
            pass "MCP tools defined"
        else
            fail "No MCP tools found in rag_server.py"
        fi
    else
        fail "rag_server.py not found"
        info "  Create from IMPLEMENTATION_WORKFLOW.md Phase 2"
    fi

    # Check requirements.txt
    if [ -f "mcp_server/requirements.txt" ]; then
        pass "requirements.txt exists"
    else
        warn "requirements.txt missing"
    fi

    # Check Dockerfile
    if [ -f "mcp_server/Dockerfile" ]; then
        pass "Dockerfile exists"
    else
        warn "Dockerfile missing (optional)"
    fi
else
    fail "MCP server directory not found"
    info "  Create: mkdir -p mcp_server"
fi

echo ""

# Check 3: MCP Dependencies
echo "[ MCP Dependencies ]"

REQUIRED_MCP_PACKAGES=("fastmcp" "chromadb" "sentence-transformers")
for pkg in "${REQUIRED_MCP_PACKAGES[@]}"; do
    if ./.venv/bin/pip show "$pkg" &>/dev/null; then
        pass "Package installed: $pkg"
    else
        fail "Package missing: $pkg"
        info "  Install: ./venv/bin/pip install $pkg"
    fi
done

echo ""

# Check 4: MCP Server Functionality
echo "[ MCP Server Functionality ]"

# Test MCP server can start
info "Testing MCP server startup..."
if timeout 10 ./.venv/bin/python mcp_server/rag_server.py &>/tmp/mcp_test.log &
 MCP_PID=$!
then
    sleep 3

    # Check if process is still running
    if ps -p $MCP_PID >/dev/null 2>&1; then
        pass "MCP server starts successfully"
        kill $MCP_PID 2>/dev/null || true
        wait $MCP_PID 2>/dev/null || true
    else
        fail "MCP server crashed on startup"
        info "  Check logs: cat /tmp/mcp_test.log"
        cat /tmp/mcp_test.log
    fi
else
    fail "MCP server failed to start"
    info "  Check: python3 mcp_server/rag_server.py"
fi

# Test ChromaDB connection from MCP server context
info "Testing ChromaDB connection from MCP context..."
TEST_RESULT=$(python3 <<'EOF'
import sys
import os
sys.path.insert(0, '/home/rebelsts/RAG/mcp_server')
os.chdir('/home/rebelsts/RAG')

try:
    import chromadb

    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8001"))

    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_collection("coding_knowledge")
    count = collection.count()
    print(f"SUCCESS:{count}")
except Exception as e:
    print(f"FAILED:{e}")
EOF
)

if echo "$TEST_RESULT" | grep -q "SUCCESS"; then
    DOC_COUNT=$(echo "$TEST_RESULT" | cut -d: -f2)
    pass "MCP can connect to ChromaDB ($DOC_COUNT documents)"
else
    fail "MCP cannot connect to ChromaDB"
    ERROR=$(echo "$TEST_RESULT" | cut -d: -f2-)
    info "  Error: $ERROR"
fi

echo ""

# Check 5: Docker MCP Server
echo "[ Docker MCP Server ]"

# Check docker-compose-full.yml
if [ -f "docker-compose-full.yml" ]; then
    pass "docker-compose-full.yml exists"

    # Validate syntax
    if docker-compose -f docker-compose-full.yml config &>/dev/null; then
        pass "docker-compose-full.yml syntax valid"
    else
        fail "docker-compose-full.yml has syntax errors"
    fi

    # Check if MCP server is defined
    if grep -q "mcp-server:" docker-compose-full.yml; then
        pass "MCP server service defined"
    else
        fail "MCP server service not defined in docker-compose-full.yml"
    fi
else
    warn "docker-compose-full.yml not found"
    info "  Using docker-compose.yml instead (ChromaDB only)"
fi

# Check if MCP container exists
if docker ps -a | grep -q "rag-mcp-server"; then
    pass "MCP server container exists"

    # Check if running
    if docker ps | grep -q "rag-mcp-server"; then
        pass "MCP server container running"

        # Check logs for errors
        if docker logs rag-mcp-server 2>&1 | tail -20 | grep -qi "error"; then
            warn "MCP server logs contain errors"
            info "  Check: docker logs rag-mcp-server --tail 50"
        else
            pass "MCP server logs clean"
        fi

        # Test connection from MCP container to ChromaDB
        if docker exec rag-mcp-server curl -sf http://chromadb:8000/api/v2/heartbeat >/dev/null 2>&1; then
            pass "MCP container can reach ChromaDB"
        else
            fail "MCP container cannot reach ChromaDB"
            info "  Check Docker network: docker network inspect rag-network"
        fi
    else
        warn "MCP server container not running"
        info "  Start: docker-compose -f docker-compose-full.yml up -d mcp-server"
    fi
else
    warn "MCP server container not deployed"
    info "  Deploy: docker-compose -f docker-compose-full.yml up -d"
fi

echo ""

# Check 6: Claude Code Configuration
echo "[ Claude Code Configuration ]"

# Check config directory
if [ -d "$HOME/.config/claude-code" ]; then
    pass "Claude Code config directory exists"

    # Check mcp_servers.json
    if [ -f "$HOME/.config/claude-code/mcp_servers.json" ]; then
        pass "mcp_servers.json exists"

        # Validate JSON syntax
        if python3 -m json.tool "$HOME/.config/claude-code/mcp_servers.json" >/dev/null 2>&1; then
            pass "mcp_servers.json syntax valid"

            # Check for rag-knowledge-base server
            if grep -q "rag-knowledge-base" "$HOME/.config/claude-code/mcp_servers.json"; then
                pass "rag-knowledge-base server configured"
            else
                warn "rag-knowledge-base server not found in config"
                info "  Add MCP server configuration"
            fi
        else
            fail "mcp_servers.json has JSON syntax errors"
            info "  Validate: python3 -m json.tool ~/.config/claude-code/mcp_servers.json"
        fi
    else
        warn "mcp_servers.json not found"
        info "  Create: mkdir -p ~/.config/claude-code && touch ~/.config/claude-code/mcp_servers.json"
    fi
else
    warn "Claude Code config directory not found"
    info "  Claude Code may not be installed or configured"
fi

echo ""

# Check 7: MCP Server Registration
echo "[ MCP Server Registration ]"

# Try to list MCP servers (requires claude CLI)
if command -v claude &>/dev/null; then
    pass "claude CLI installed"

    # List MCP servers
    info "Checking MCP server registration..."
    if timeout 10 claude mcp list 2>&1 | grep -q "rag-knowledge-base"; then
        pass "rag-knowledge-base MCP server registered"
    else
        warn "rag-knowledge-base MCP server not registered"
        info "  Check: claude mcp list"
        info "  Verify mcp_servers.json configuration"
    fi
else
    warn "claude CLI not installed"
    info "  Cannot verify MCP registration"
    info "  Install Claude Code to test"
fi

echo ""

# Check 8: Network Configuration
echo "[ Network Configuration ]"

# Check Docker network exists
if docker network inspect rag-network >/dev/null 2>&1; then
    pass "rag-network exists"

    # Check containers are connected
    NETWORK_INFO=$(docker network inspect rag-network)

    if echo "$NETWORK_INFO" | grep -q "chromadb-server"; then
        pass "ChromaDB connected to rag-network"
    else
        warn "ChromaDB not connected to rag-network"
    fi

    if echo "$NETWORK_INFO" | grep -q "rag-mcp-server"; then
        pass "MCP server connected to rag-network"
    else
        warn "MCP server not connected to rag-network"
        info "  Fix: docker network connect rag-network rag-mcp-server"
    fi
else
    warn "rag-network not found"
    info "  Docker will create it automatically on first compose up"
fi

echo ""

# Check 9: Environment Variables
echo "[ Environment Variables ]"

# Check if MCP container has correct env vars
if docker ps | grep -q "rag-mcp-server"; then
    CHROMA_HOST=$(docker exec rag-mcp-server env 2>/dev/null | grep CHROMA_HOST | cut -d= -f2 || echo "NOT_SET")
    CHROMA_PORT=$(docker exec rag-mcp-server env 2>/dev/null | grep CHROMA_PORT | cut -d= -f2 || echo "NOT_SET")

    if [ "$CHROMA_HOST" = "chromadb" ]; then
        pass "CHROMA_HOST set correctly: $CHROMA_HOST"
    else
        fail "CHROMA_HOST incorrect: $CHROMA_HOST (should be 'chromadb')"
        info "  Update docker-compose-full.yml environment section"
    fi

    if [ "$CHROMA_PORT" = "8000" ]; then
        pass "CHROMA_PORT set correctly: $CHROMA_PORT"
    else
        warn "CHROMA_PORT is: $CHROMA_PORT (expected 8000 for internal)"
    fi
else
    info "MCP container not running - skipping env check"
fi

echo ""

# Check 10: Integration Test
echo "[ Integration Test ]"

if command -v claude &>/dev/null && docker ps | grep -q "rag-mcp-server"; then
    info "Attempting integration test via Claude Code..."

    # Create test script
    cat > /tmp/mcp_integration_test.sh <<'EOF'
#!/bin/bash
timeout 30 claude <<'CLAUDE_EOF'
Use the rag-knowledge-base MCP server to list all technologies. Respond with just the count.
CLAUDE_EOF
EOF

    chmod +x /tmp/mcp_integration_test.sh

    if /tmp/mcp_integration_test.sh 2>&1 | grep -qi "technolog\|react\|python"; then
        pass "Integration test successful"
        info "  MCP server is responding to Claude Code queries"
    else
        warn "Integration test inconclusive"
        info "  Manual test: Open claude and run: Use rag-knowledge-base to query something"
    fi

    rm -f /tmp/mcp_integration_test.sh
else
    info "Integration test skipped (requires claude CLI and running MCP server)"
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

    if [ $SUCCESS_RATE -ge 85 ]; then
        echo -e "${GREEN}✓ Phase 2 ready - MCP integration successful${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Test MCP server: claude mcp list"
        echo "  2. Query knowledge base: Use rag-knowledge-base to query 'What is React?'"
        echo "  3. Proceed to Phase 3 (Optimization)"
        exit 0
    elif [ $SUCCESS_RATE -ge 65 ]; then
        echo -e "${YELLOW}⚠ Phase 2 has warnings - review and fix before proceeding${NC}"
        echo ""
        echo "Common fixes:"
        echo "  - Ensure docker-compose-full.yml is configured correctly"
        echo "  - Verify network connectivity between containers"
        echo "  - Check mcp_servers.json syntax"
        exit 1
    else
        echo -e "${RED}✗ Phase 2 validation failed - fix critical issues${NC}"
        echo ""
        echo "Critical checks failed. Review:"
        echo "  - ChromaDB must be running and accessible"
        echo "  - MCP server must start without errors"
        echo "  - Docker network must connect containers"
        exit 1
    fi
else
    echo "No checks were performed"
    exit 1
fi
