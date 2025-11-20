#!/bin/bash
# JAKE Test Suite Runner
# Runs all tests to verify the JAKE system
#
# This script runs:
# 1. Unit tests (individual component testing)
# 2. API server health check
# 3. API endpoint tests (all 9 endpoints)

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default values
PORT="${1:-8000}"
API_URL="http://localhost:$PORT"
RUN_UNIT_TESTS=true
RUN_API_TESTS=true
SKIP_SERVER_CHECK=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            API_URL="http://localhost:$PORT"
            shift 2
            ;;
        --unit-only)
            RUN_UNIT_TESTS=true
            RUN_API_TESTS=false
            SKIP_SERVER_CHECK=true
            shift
            ;;
        --api-only)
            RUN_UNIT_TESTS=false
            RUN_API_TESTS=true
            shift
            ;;
        --skip-server-check)
            SKIP_SERVER_CHECK=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [PORT]"
            echo ""
            echo "Options:"
            echo "  --port PORT          Specify API server port (default: 8000)"
            echo "  --unit-only          Run only unit tests (no API server needed)"
            echo "  --api-only           Run only API tests (requires running server)"
            echo "  --skip-server-check  Skip checking if server is running"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                   Run all tests on port 8000"
            echo "  $0 8001              Run all tests on port 8001"
            echo "  $0 --unit-only       Run only unit tests"
            echo "  $0 --api-only        Run only API tests"
            exit 0
            ;;
        *)
            PORT="$1"
            API_URL="http://localhost:$PORT"
            shift
            ;;
    esac
done

# Print header
echo ""
echo -e "${BOLD}${CYAN}================================================================${NC}"
echo -e "${BOLD}${CYAN}                    JAKE TEST SUITE${NC}"
echo -e "${BOLD}${CYAN}================================================================${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  API URL: ${YELLOW}$API_URL${NC}"
echo -e "  Unit Tests: ${YELLOW}$([ "$RUN_UNIT_TESTS" = true ] && echo "enabled" || echo "disabled")${NC}"
echo -e "  API Tests: ${YELLOW}$([ "$RUN_API_TESTS" = true ] && echo "enabled" || echo "disabled")${NC}"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${MAGENTA}  $1${NC}"
    echo -e "${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to record test result
record_result() {
    if [ $1 -eq 0 ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✓ $2 passed${NC}"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}✗ $2 failed${NC}"
        if [ "${3:-}" != "continue" ]; then
            exit 1
        fi
    fi
}

# ============================================================================
# STEP 1: UNIT TESTS (No API server required)
# ============================================================================
if [ "$RUN_UNIT_TESTS" = true ]; then
    print_section "Step 1: Unit Tests (Testing Individual Components)"

    echo -e "${BLUE}Running unit tests with tests/test_jake.py...${NC}"
    echo ""

    if python tests/test_jake.py; then
        record_result 0 "Unit tests"
    else
        record_result 1 "Unit tests"
    fi
fi

# ============================================================================
# STEP 2: CHECK API SERVER (if running API tests)
# ============================================================================
if [ "$RUN_API_TESTS" = true ] && [ "$SKIP_SERVER_CHECK" = false ]; then
    print_section "Step 2: API Server Health Check"

    echo -e "${BLUE}Checking if API server is running at $API_URL...${NC}"

    # Try to ping the server
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/ping" || echo "000")

    if [ "$HTTP_CODE" != "200" ]; then
        echo -e "${RED}✗ API server is not responding (HTTP $HTTP_CODE)${NC}"
        echo ""
        echo -e "${YELLOW}Please start the server first:${NC}"
        echo -e "  ./start_server.sh $PORT"
        echo ""
        echo -e "${YELLOW}Or run unit tests only:${NC}"
        echo -e "  ./run_tests.sh --unit-only"
        echo ""
        exit 1
    fi

    echo -e "${GREEN}✓ API server is running and healthy${NC}"
fi

# ============================================================================
# STEP 3: API ENDPOINT TESTS
# ============================================================================
if [ "$RUN_API_TESTS" = true ]; then
    print_section "Step 3: API Endpoint Tests"

    echo -e "${BLUE}Running API endpoint tests with tests/test_api_simple.sh...${NC}"
    echo ""

    if ./tests/test_api_simple.sh $PORT; then
        record_result 0 "API endpoint tests"
    else
        record_result 1 "API endpoint tests"
    fi
fi

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_section "Test Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "${BOLD}Results:${NC}"
echo -e "  Total Tests: ${CYAN}$TOTAL_TESTS${NC}"
echo -e "  Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "  Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${BOLD}${GREEN}================================================================${NC}"
    echo -e "${BOLD}${GREEN}  🎉 ALL TESTS PASSED! JAKE is working perfectly!${NC}"
    echo -e "${BOLD}${GREEN}================================================================${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${BOLD}${RED}================================================================${NC}"
    echo -e "${BOLD}${RED}  ✗ SOME TESTS FAILED - Please review the errors above${NC}"
    echo -e "${BOLD}${RED}================================================================${NC}"
    echo ""
    exit 1
fi
