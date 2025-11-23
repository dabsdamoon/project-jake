#!/bin/bash
# JAKE Test Suite Runner
# Runs API endpoint tests to verify the JAKE system
#
# This script:
# 1. Starts the API server automatically
# 2. Runs API endpoint tests (all 9 endpoints)
# 3. Shuts down the API server when finished

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set PYTHONPATH to project root so 'src' module can be found
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# JSON parsing helper using Python (instead of jq)
json_get() {
    python -c "import sys, json; data=json.load(sys.stdin); print(data.get('$1', '') if isinstance(data.get('$1'), str) else json.dumps(data.get('$1', '')))" 2>/dev/null
}

json_pretty() {
    python -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))" 2>/dev/null
}

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
SERVER_PID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            API_URL="http://localhost:$PORT"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [PORT]"
            echo ""
            echo "Options:"
            echo "  --port PORT    Specify API server port (default: 8000)"
            echo "  -h, --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0             Run tests on port 8000"
            echo "  $0 8001        Run tests on port 8001"
            echo "  $0 --port 8001 Run tests on port 8001"
            exit 0
            ;;
        *)
            PORT="$1"
            API_URL="http://localhost:$PORT"
            shift
            ;;
    esac
done

# Cleanup function to stop the server
cleanup() {
    local exit_code=$?
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        echo ""
        echo -e "${BLUE}Shutting down API server (PID: $SERVER_PID)...${NC}"
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
        echo -e "${GREEN}Server stopped${NC}"
    fi
    exit $exit_code
}

# Handle Ctrl+C (SIGINT) gracefully
handle_interrupt() {
    echo ""
    echo -e "${YELLOW}Interrupted by user (Ctrl+C)${NC}"
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        echo -e "${BLUE}Shutting down API server (PID: $SERVER_PID)...${NC}"
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
        echo -e "${GREEN}Server stopped${NC}"
    fi
    exit 130
}

# Set traps for cleanup
trap handle_interrupt INT
trap cleanup EXIT TERM

# Print header
echo ""
echo -e "${BOLD}${CYAN}================================================================${NC}"
echo -e "${BOLD}${CYAN}                    JAKE TEST SUITE${NC}"
echo -e "${BOLD}${CYAN}================================================================${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  API URL: ${YELLOW}$API_URL${NC}"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${MAGENTA}  $1${NC}"
    echo -e "${BOLD}${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to wait for server to be ready
wait_for_server() {
    local max_attempts=30
    local attempt=1

    echo -e "${BLUE}Waiting for server to be ready...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$API_URL/ping" 2>/dev/null | grep -q "200"; then
            echo -e "${GREEN}✓ Server is ready${NC}"
            return 0
        fi
        echo -e "  Attempt $attempt/$max_attempts..."
        sleep 1
        attempt=$((attempt + 1))
    done

    echo -e "${RED}✗ Server failed to start within $max_attempts seconds${NC}"
    return 1
}

# ============================================================================
# STEP 1: START API SERVER
# ============================================================================
print_section "Step 1: Starting API Server"

echo -e "${BLUE}Starting API server on port $PORT...${NC}"

# Start server in background (PORT is passed via environment variable)
PORT="$PORT" python -m src.main > /tmp/jake_server.log 2>&1 &
SERVER_PID=$!

echo -e "  Server PID: ${YELLOW}$SERVER_PID${NC}"

# Wait for server to be ready
if ! wait_for_server; then
    echo -e "${RED}Failed to start server. Check logs:${NC}"
    cat /tmp/jake_server.log
    exit 1
fi

# ============================================================================
# STEP 2: API ENDPOINT TESTS
# ============================================================================
print_section "Step 2: API Endpoint Tests"

echo -e "${BLUE}Running API endpoint tests...${NC}"
echo ""

API_TESTS_PASSED=0
API_TESTS_TOTAL=9

# Test 1: Health Check
echo -e "${BLUE}Test 1/9: Health Check${NC}"
HTTP_CODE=$(curl -s -o /tmp/health_response.json -w "%{http_code}" "$API_URL/ping")

if [ "$HTTP_CODE" = "200" ]; then
    STATUS=$(cat /tmp/health_response.json | json_get status)
    if [ "$STATUS" = "healthy" ]; then
        cat /tmp/health_response.json | json_pretty
        echo -e "${GREEN}✓ Health check passed${NC}"
        API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ Health check failed: unhealthy status${NC}"
    fi
else
    echo -e "${RED}✗ Health check failed: HTTP $HTTP_CODE${NC}"
fi
echo ""

# Test 2: Create Character
echo -e "${BLUE}Test 2/9: Create Character${NC}"
CHARACTER=$(curl -s -X POST "$API_URL/characters" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "name": "Luna",
    "age": "25",
    "occupation": "Cafe owner",
    "additional_info": "Loves books and coffee"
  }')

CHAR_ID=$(echo $CHARACTER | json_get character_id)

if [ -n "$CHAR_ID" ] && [ "$CHAR_ID" != "null" ] && [ "$CHAR_ID" != "" ]; then
    echo "Created Character ID: $CHAR_ID"
    echo "Name: $(echo $CHARACTER | json_get name)"
    echo $CHARACTER | json_get details
    echo -e "${GREEN}✓ Character created successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to create character${NC}"
    echo "Response: $CHARACTER"
fi
echo ""

# Test 3: Get Character
echo -e "${BLUE}Test 3/9: Get Character${NC}"
GET_CHAR=$(curl -s "$API_URL/characters/$CHAR_ID")
GET_CHAR_ID=$(echo $GET_CHAR | json_get character_id)

if [ -n "$GET_CHAR_ID" ] && [ "$GET_CHAR_ID" != "null" ] && [ "$GET_CHAR_ID" != "" ]; then
    echo $GET_CHAR | python -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ['character_id','name','age','occupation']}, indent=2))"
    echo -e "${GREEN}✓ Character retrieved successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to retrieve character${NC}"
    echo "Response: $GET_CHAR"
fi
echo ""

# Test 4: First Chat
echo -e "${BLUE}Test 4/9: First Chat Message${NC}"
CHAT1=$(curl -s -X POST "$API_URL/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! This cafe looks really cozy."
  }')

SESSION=$(echo $CHAT1 | json_get session_id)

if [ -n "$SESSION" ] && [ "$SESSION" != "null" ] && [ "$SESSION" != "" ]; then
    echo "Session ID: $SESSION"
    echo $CHAT1 | python -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ['dialogue','affection_score','turn_count']}, indent=2))"
    echo -e "${GREEN}✓ Chat initiated successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to create chat session${NC}"
    echo "Response: $CHAT1"
fi
echo ""

# Test 5: Continue Chat
echo -e "${BLUE}Test 5/9: Continue Chat (with session)${NC}"
CHAT2=$(curl -s -X POST "$API_URL/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: $SESSION" \
  -d '{
    "message": "What kind of books do you like?"
  }')

DIALOGUE2=$(echo $CHAT2 | json_get dialogue)

if [ -n "$DIALOGUE2" ] && [ "$DIALOGUE2" != "null" ] && [ "$DIALOGUE2" != "" ]; then
    echo $CHAT2 | python -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({k:d.get(k) for k in ['dialogue','affection_score','affection_change','turn_count']}, indent=2))"
    echo -e "${GREEN}✓ Chat continued successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to continue chat${NC}"
    echo "Response: $CHAT2"
fi
echo ""

# Test 6: Create Quest
echo -e "${BLUE}Test 6/9: Create Quest${NC}"
QUEST=$(curl -s -X POST "$API_URL/characters/$CHAR_ID/quests" \
  -H "Content-Type: application/json" \
  -d '{
    "quest_type": "regular",
    "title": "Book Discussion",
    "description": "Ask about favorite books"
  }')

QUEST_ID=$(echo $QUEST | json_get quest_id)

if [ -n "$QUEST_ID" ] && [ "$QUEST_ID" != "null" ] && [ "$QUEST_ID" != "" ]; then
    echo $QUEST | json_pretty
    echo -e "${GREEN}✓ Quest created successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to create quest${NC}"
    echo "Response: $QUEST"
fi
echo ""

# Test 7: List Quests
echo -e "${BLUE}Test 7/9: List Quests${NC}"
QUESTS=$(curl -s "$API_URL/characters/$CHAR_ID/quests")
QUESTS_LIST=$(echo $QUESTS | json_get regular_quests)

if [ -n "$QUESTS_LIST" ] && [ "$QUESTS_LIST" != "[]" ] && [ "$QUESTS_LIST" != "" ]; then
    echo $QUESTS | json_get regular_quests
    echo -e "${GREEN}✓ Quests retrieved successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to retrieve quests${NC}"
    echo "Response: $QUESTS"
fi
echo ""

# Test 8: Conversation History
echo -e "${BLUE}Test 8/9: Conversation History${NC}"
HISTORY=$(curl -s "$API_URL/conversations/$SESSION")
HISTORY_SESSION=$(echo $HISTORY | json_get session_id)

if [ -n "$HISTORY_SESSION" ] && [ "$HISTORY_SESSION" != "null" ] && [ "$HISTORY_SESSION" != "" ]; then
    echo $HISTORY | python -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({'session_id':d.get('session_id'),'affection_score':d.get('affection_score'),'turn_count':d.get('turn_count'),'message_count':len(d.get('messages',[]))}, indent=2))"
    echo -e "${GREEN}✓ Conversation history retrieved successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to retrieve conversation history${NC}"
    echo "Response: $HISTORY"
fi
echo ""

# Test 9: List User Characters
echo -e "${BLUE}Test 9/9: List User Characters${NC}"
USER_CHARS=$(curl -s "$API_URL/users/test_user/characters")
CHARS_LIST=$(echo $USER_CHARS | json_get characters)

if [ -n "$CHARS_LIST" ] && [ "$CHARS_LIST" != "[]" ] && [ "$CHARS_LIST" != "" ]; then
    echo $USER_CHARS | json_get characters
    echo -e "${GREEN}✓ User characters retrieved successfully${NC}"
    API_TESTS_PASSED=$((API_TESTS_PASSED + 1))
else
    echo -e "${RED}✗ Failed to retrieve user characters${NC}"
    echo "Response: $USER_CHARS"
fi
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_section "Test Summary"

echo -e "${BOLD}Results:${NC}"
echo -e "  Total Tests: ${CYAN}$API_TESTS_TOTAL${NC}"
echo -e "  Passed: ${GREEN}$API_TESTS_PASSED${NC}"
echo -e "  Failed: ${RED}$((API_TESTS_TOTAL - API_TESTS_PASSED))${NC}"

if [ $API_TESTS_PASSED -eq $API_TESTS_TOTAL ]; then
    echo ""
    echo -e "${BOLD}${GREEN}================================================================${NC}"
    echo -e "${BOLD}${GREEN}  ALL TESTS PASSED! JAKE is working perfectly!${NC}"
    echo -e "${BOLD}${GREEN}================================================================${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${BOLD}${RED}================================================================${NC}"
    echo -e "${BOLD}${RED}  SOME TESTS FAILED - Please review the errors above${NC}"
    echo -e "${BOLD}${RED}================================================================${NC}"
    echo ""
    exit 1
fi
