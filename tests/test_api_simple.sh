#!/bin/bash
# Simple shell script to test JAKE API endpoints using curl

# Exit on any error
set -e

# Default port or use first argument
PORT="${1:-8000}"
API="http://localhost:$PORT"
echo "Testing JAKE API at: $API"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check (CRITICAL - must pass)
echo -e "${BLUE}Test 1: Health Check${NC}"

# Check if API is responding
HTTP_CODE=$(curl -s -o /tmp/health_response.json -w "%{http_code}" "$API/ping")

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}❌ FAILED: API is not responding (HTTP $HTTP_CODE)${NC}"
    echo -e "${YELLOW}Make sure the server is running:${NC}"
    echo -e "  ./start_server.sh $PORT"
    echo ""
    exit 1
fi

# Check health status
cat /tmp/health_response.json | jq '.'
STATUS=$(cat /tmp/health_response.json | jq -r '.status // empty')

if [ "$STATUS" != "healthy" ]; then
    echo -e "${RED}❌ FAILED: API returned unhealthy status${NC}"
    exit 1
fi

echo -e "${GREEN}✓ API is healthy${NC}"
echo ""

# Test 2: Create Character
echo -e "${BLUE}Test 2: Create Character${NC}"
CHARACTER=$(curl -s -X POST "$API/characters" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "name": "Luna",
    "age": "25",
    "occupation": "Cafe owner",
    "additional_info": "Loves books and coffee"
  }')

CHAR_ID=$(echo $CHARACTER | jq -r '.character_id // empty')

if [ -z "$CHAR_ID" ] || [ "$CHAR_ID" = "null" ]; then
    echo -e "${RED}❌ FAILED: Could not create character${NC}"
    echo "Response: $CHARACTER"
    exit 1
fi

echo "Created Character ID: $CHAR_ID"
echo "Name: $(echo $CHARACTER | jq -r '.name')"
echo ""
echo "Character Details:"
echo $CHARACTER | jq '.details'
echo -e "${GREEN}✓ Character created successfully${NC}"
echo ""

# Test 3: Get Character
echo -e "${BLUE}Test 3: Get Character${NC}"
GET_CHAR=$(curl -s "$API/characters/$CHAR_ID")
GET_CHAR_ID=$(echo $GET_CHAR | jq -r '.character_id // empty')

if [ -z "$GET_CHAR_ID" ] || [ "$GET_CHAR_ID" = "null" ]; then
    echo -e "${RED}❌ FAILED: Could not retrieve character${NC}"
    echo "Response: $GET_CHAR"
    exit 1
fi

echo $GET_CHAR | jq '{character_id, name, age, occupation}'
echo -e "${GREEN}✓ Character retrieved successfully${NC}"
echo ""

# Test 4: First Chat
echo -e "${BLUE}Test 4: First Chat Message${NC}"
CHAT1=$(curl -s -X POST "$API/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! This cafe looks really cozy."
  }')

SESSION=$(echo $CHAT1 | jq -r '.session_id // empty')

if [ -z "$SESSION" ] || [ "$SESSION" = "null" ]; then
    echo -e "${RED}❌ FAILED: Could not create chat session${NC}"
    echo "Response: $CHAT1"
    exit 1
fi

echo "Session ID: $SESSION"
echo $CHAT1 | jq '{dialogue, affection_score, turn_count}'
echo -e "${GREEN}✓ Chat initiated successfully${NC}"
echo ""

# Test 5: Continue Chat
echo -e "${BLUE}Test 5: Continue Chat (with session)${NC}"
CHAT2=$(curl -s -X POST "$API/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: $SESSION" \
  -d '{
    "message": "What kind of books do you like?"
  }')

DIALOGUE2=$(echo $CHAT2 | jq -r '.dialogue // empty')

if [ -z "$DIALOGUE2" ] || [ "$DIALOGUE2" = "null" ]; then
    echo -e "${RED}❌ FAILED: Could not continue chat${NC}"
    echo "Response: $CHAT2"
    exit 1
fi

echo $CHAT2 | jq '{dialogue, affection_score, affection_change, turn_count}'
echo -e "${GREEN}✓ Chat continued successfully${NC}"
echo ""

# Test 6: Create Quest
echo -e "${BLUE}Test 6: Create Quest${NC}"
QUEST=$(curl -s -X POST "$API/characters/$CHAR_ID/quests" \
  -H "Content-Type: application/json" \
  -d '{
    "quest_type": "regular",
    "title": "Book Discussion",
    "description": "Ask about favorite books"
  }')

QUEST_ID=$(echo $QUEST | jq -r '.quest_id // empty')

if [ -z "$QUEST_ID" ] || [ "$QUEST_ID" = "null" ]; then
    echo -e "${RED}❌ FAILED: Could not create quest${NC}"
    echo "Response: $QUEST"
    exit 1
fi

echo $QUEST | jq '.'
echo -e "${GREEN}✓ Quest created successfully${NC}"
echo ""

# Test 7: List Quests
echo -e "${BLUE}Test 7: List Quests${NC}"
QUESTS=$(curl -s "$API/characters/$CHAR_ID/quests")
echo $QUESTS | jq '.regular_quests'
echo -e "${GREEN}✓ Quests retrieved successfully${NC}"
echo ""

# Test 8: Conversation History
echo -e "${BLUE}Test 8: Conversation History${NC}"
HISTORY=$(curl -s "$API/conversations/$SESSION")
HISTORY_SESSION=$(echo $HISTORY | jq -r '.session_id // empty')

if [ -z "$HISTORY_SESSION" ] || [ "$HISTORY_SESSION" = "null" ]; then
    echo -e "${RED}❌ FAILED: Could not retrieve conversation history${NC}"
    echo "Response: $HISTORY"
    exit 1
fi

echo $HISTORY | jq '{session_id, affection_score, turn_count, message_count: (.messages | length)}'
echo -e "${GREEN}✓ Conversation history retrieved successfully${NC}"
echo ""

# Test 9: List User Characters
echo -e "${BLUE}Test 9: List User Characters${NC}"
USER_CHARS=$(curl -s "$API/users/test_user/characters")
echo $USER_CHARS | jq '.characters'
echo -e "${GREEN}✓ User characters retrieved successfully${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All 9 tests completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
