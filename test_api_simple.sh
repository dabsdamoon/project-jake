#!/bin/bash
# Simple shell script to test JAKE API endpoints using curl

# Default port or use first argument
PORT="${1:-8000}"
API="http://localhost:$PORT"
echo "Testing JAKE API at: $API"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
curl -s "$API/ping" | jq '.'
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

CHAR_ID=$(echo $CHARACTER | jq -r '.character_id')
echo "Created Character ID: $CHAR_ID"
echo $CHARACTER | jq '{character_id, name, personality: .details.personality}'
echo ""

# Test 3: Get Character
echo -e "${BLUE}Test 3: Get Character${NC}"
curl -s "$API/characters/$CHAR_ID" | jq '{character_id, name, age, occupation}'
echo ""

# Test 4: First Chat
echo -e "${BLUE}Test 4: First Chat Message${NC}"
CHAT1=$(curl -s -X POST "$API/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! This cafe looks really cozy."
  }')

SESSION=$(echo $CHAT1 | jq -r '.session_id')
echo "Session ID: $SESSION"
echo $CHAT1 | jq '{dialogue, affection_score, turn_count}'
echo ""

# Test 5: Continue Chat
echo -e "${BLUE}Test 5: Continue Chat (with session)${NC}"
CHAT2=$(curl -s -X POST "$API/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: $SESSION" \
  -d '{
    "message": "What kind of books do you like?"
  }')

echo $CHAT2 | jq '{dialogue, affection_score, affection_change, turn_count}'
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

echo $QUEST | jq '.'
echo ""

# Test 7: List Quests
echo -e "${BLUE}Test 7: List Quests${NC}"
curl -s "$API/characters/$CHAR_ID/quests" | jq '.regular_quests'
echo ""

# Test 8: Conversation History
echo -e "${BLUE}Test 8: Conversation History${NC}"
curl -s "$API/conversations/$SESSION" | jq '{session_id, affection_score, turn_count, message_count: (.messages | length)}'
echo ""

# Test 9: List User Characters
echo -e "${BLUE}Test 9: List User Characters${NC}"
curl -s "$API/users/test_user/characters" | jq '.characters'
echo ""

echo -e "${GREEN}✓ All tests completed!${NC}"
