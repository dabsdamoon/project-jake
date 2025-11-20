# Getting Started with JAKE API

## Quick Overview

The JAKE system is **already fully connected** through FastAPI. Here's how all components work together:

```
User Request → FastAPI Endpoint → JAKEOrchestrator → LangGraph State Machine
                                         ↓
                    ┌────────────────────┴────────────────────┐
                    ▼                    ▼                     ▼
              JAKECreator          JAKEChatter         JAKEChecker
                                        ↓                      ↓
                              JAKEDynamicProfiler    JAKESummarizer
                                        ↓
                              Database + Vector Store
                                        ↓
                                  JSON Response
```

---

## 🚀 Step-by-Step: Running the API

### 1. Install Dependencies

```bash
# Make sure you're in the project directory
cd /Users/dabsdamoon/projects/project-jake

# Install all required packages
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Using your favorite editor:
nano .env
# or
vim .env
# or
code .env
```

Add this to `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=sqlite:///./jake.db
CHROMA_PERSIST_DIR=./chroma_db
HOST=0.0.0.0
PORT=8000
```

### 3. Run the Server

```bash
# Option A: Using startup script (Recommended)
./start_server.sh          # Default port 8000
./start_server.sh 8001     # Custom port 8001

# Option B: Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001  # Custom port
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Access the API

Open your browser and go to:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/ping

---

## 📡 Using the API

### Example 1: Create a Character

```bash
curl -X POST "http://localhost:8000/characters" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "Luna",
    "age": "25",
    "occupation": "Cafe owner",
    "additional_info": "Loves books, coffee, and rainy days"
  }'
```

**Response:**
```json
{
  "character_id": 1,
  "name": "Luna",
  "worldview": "Luna lives in a quaint neighborhood...",
  "details": {
    "personality": "Warm, caring, slightly shy...",
    "speaking_style": "Gentle and soft-spoken...",
    "likes": "Books, rainy days, warm tea...",
    ...
  },
  "created_at": "2025-11-18T14:30:00"
}
```

### Example 2: Chat with Character

```bash
curl -X POST "http://localhost:8000/characters/1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! This cafe looks really cozy."
  }'
```

**Response:**
```json
{
  "session_id": "abc-123-def-456",
  "dialogue": "Oh, thank you! *smiles warmly* I try to make everyone feel at home here.",
  "action": "*wipes hands on apron and gestures to a corner table*",
  "situation": "The cafe is quiet in the afternoon, soft jazz playing in the background",
  "background": "Warm lighting filters through large windows, casting gentle shadows",
  "internal_thought": "It's nice when customers appreciate the atmosphere I've created...",
  "affection_score": 52,
  "affection_change": 2,
  "relationship_stage": "stranger",
  "turn_count": 1,
  "memories_extracted": 3
}
```

### Example 3: Continue Conversation (with Session)

```bash
curl -X POST "http://localhost:8000/characters/1/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: abc-123-def-456" \
  -d '{
    "message": "What kind of books do you like?"
  }'
```

The system automatically:
1. ✅ Loads conversation history
2. ✅ Maintains affection score
3. ✅ Tracks turn count
4. ✅ Routes through appropriate agents (per PLAN.md)
5. ✅ Saves everything to database

### Example 4: Create a Quest

```bash
curl -X POST "http://localhost:8000/characters/1/quests" \
  -H "Content-Type: application/json" \
  -d '{
    "quest_type": "regular",
    "title": "Getting to Know Each Other",
    "description": "Ask about Luna'\''s favorite book",
    "required_affection": 0
  }'
```

### Example 5: Search Memories

```bash
curl -X GET "http://localhost:8000/characters/1/memories?query=favorite%20book&limit=5"
```

---

## 🔧 How the Connection Works (Code Level)

### The Flow in `src/main.py`

```python
# 1. Initialize orchestrator (connects all agents)
orchestrator = JAKEOrchestrator()
vector_store = VectorMemoryStore()

# 2. Chat endpoint receives request
@app.post("/characters/{character_id}/chat")
async def chat_with_character(character_id: int, chat_request: ChatRequest, db: Session):

    # 3. Load character from database
    character = db.query(Character).filter(Character.id == character_id).first()

    # 4. Load/create conversation session
    conversation = load_or_create_session(chat_request.session_id)

    # 5. Load context (history, quests, affection)
    history = get_message_history(conversation.id)
    quests = get_character_quests(character_id)

    # 6. Build character dictionary
    character_dict = {
        "basics": {...},
        "worldview": character.worldview,
        "details": character.details,
        "dynamic_profile": character.dynamic_profile
    }

    # 7. Process through orchestrator (THE MAGIC HAPPENS HERE)
    result = orchestrator.process_message(
        user_message=chat_request.message,
        character=character_dict,
        history=history,
        regular_quests=regular_quests,
        advancement_quests=advancement_quests,
        current_affection=conversation.affection_score,
        relationship_stage=conversation.relationship_stage
    )

    # 8. Orchestrator internally:
    #    - Runs JAKEChatter
    #    - Routes to JAKEChecker/JAKEDynamicProfiler/JAKESummarizer based on turn count
    #    - Returns complete result

    # 9. Save everything to database
    save_messages(conversation.id, chat_request.message, result["response"])
    update_affection(conversation, result["updated_affection"])
    update_quests(result.get("updated_quests"))
    update_character_profile(character, result.get("updated_dynamic_profile"))

    # 10. Store memories in vector database
    for category, facts in result["memories"].items():
        for fact in facts:
            save_to_vector_db(character_id, fact, category)

    # 11. Return response to user
    return {
        "session_id": conversation.session_id,
        "dialogue": result["response"]["dialogue"],
        "action": result["response"]["action"],
        ...
    }
```

### The Orchestrator (LangGraph State Machine)

```python
# In src/agents/jake_orchestrator.py

class JAKEOrchestrator:
    def __init__(self):
        # Initialize all agents
        self.creator = JAKECreator()
        self.chatter = JAKEChatter()
        self.checker = JAKEChecker()
        self.profiler = JAKEDynamicProfiler()
        self.summarizer = JAKESummarizer()

        # Build LangGraph state machine
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ConversationState)

        # Add nodes
        workflow.add_node("chat", self._chat_node)
        workflow.add_node("check_quests", self._check_quests_node)
        workflow.add_node("update_profile", self._update_profile_node)
        workflow.add_node("summarize", self._summarize_node)

        # Set entry point
        workflow.set_entry_point("chat")

        # Add conditional routing (THIS IS WHERE PLAN.MD LOGIC HAPPENS)
        workflow.add_conditional_edges(
            "chat",
            self._route_after_chat,
            {
                "summarize_only": "summarize",           # turns < 3
                "check_and_summarize": "check_quests",   # 3 ≤ turns < 10
                "full_process": "check_quests"            # turns ≥ 10
            }
        )

        return workflow.compile()

    def process_message(self, user_message, character, history, ...):
        # Run through state machine
        result = self.graph.invoke({
            "user_message": user_message,
            "character": character,
            "history": history,
            ...
        })
        return result
```

---

## 🧪 Testing the Full Pipeline

### Option 1: Use the Test Script

```bash
python test_jake.py
```

This tests:
- ✅ Character creation
- ✅ Conversation flow
- ✅ Quest checking
- ✅ Memory extraction
- ✅ Full orchestrator

### Option 2: Manual Testing with cURL

Create a simple test script:

```bash
#!/bin/bash
# test_api.sh

API="http://localhost:8000"

echo "1. Creating character..."
CHARACTER=$(curl -s -X POST "$API/characters" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "name": "Alice",
    "age": "28",
    "occupation": "Librarian",
    "additional_info": "Loves mystery novels"
  }')

CHAR_ID=$(echo $CHARACTER | jq -r '.character_id')
echo "Character ID: $CHAR_ID"

echo -e "\n2. First chat..."
CHAT1=$(curl -s -X POST "$API/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi! I love libraries too!"
  }')

SESSION=$(echo $CHAT1 | jq -r '.session_id')
echo "Session ID: $SESSION"
echo "Response: $(echo $CHAT1 | jq -r '.dialogue')"
echo "Affection: $(echo $CHAT1 | jq -r '.affection_score')"

echo -e "\n3. Second chat (with session)..."
CHAT2=$(curl -s -X POST "$API/characters/$CHAR_ID/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: $SESSION" \
  -d '{
    "message": "What is your favorite genre?"
  }')

echo "Response: $(echo $CHAT2 | jq -r '.dialogue')"
echo "Affection: $(echo $CHAT2 | jq -r '.affection_score')"

echo -e "\n4. View history..."
curl -s "$API/conversations/$SESSION" | jq
```

### Option 3: Python Client

```python
# test_client.py
import requests

BASE_URL = "http://localhost:8000"

# 1. Create character
response = requests.post(f"{BASE_URL}/characters", json={
    "user_id": "user123",
    "name": "Luna",
    "age": "25",
    "occupation": "Cafe owner",
    "additional_info": "Loves books and coffee"
})
character = response.json()
char_id = character["character_id"]
print(f"Created character: {character['name']} (ID: {char_id})")

# 2. Start conversation
response = requests.post(f"{BASE_URL}/characters/{char_id}/chat", json={
    "message": "Hello! This place looks cozy."
})
chat1 = response.json()
session_id = chat1["session_id"]
print(f"\nLuna: {chat1['dialogue']}")
print(f"Action: {chat1['action']}")
print(f"Affection: {chat1['affection_score']}")

# 3. Continue conversation
response = requests.post(
    f"{BASE_URL}/characters/{char_id}/chat",
    json={"message": "Do you have any book recommendations?"},
    headers={"X-Session-Id": session_id}
)
chat2 = response.json()
print(f"\nLuna: {chat2['dialogue']}")
print(f"Affection: {chat2['affection_score']} ({chat2['affection_change']:+d})")

# 4. Create quest
response = requests.post(f"{BASE_URL}/characters/{char_id}/quests", json={
    "quest_type": "regular",
    "title": "Book Discussion",
    "description": "Ask about Luna's favorite book genre"
})
quest = response.json()
print(f"\nQuest created: {quest['title']}")

# 5. Multiple turns to trigger quest checking (turn 3+)
for i in range(3, 6):
    response = requests.post(
        f"{BASE_URL}/characters/{char_id}/chat",
        json={"message": f"Message {i}"},
        headers={"X-Session-Id": session_id}
    )
    chat = response.json()
    print(f"\nTurn {chat['turn_count']}: Affection {chat['affection_score']}")

# 6. Check quest status
response = requests.get(f"{BASE_URL}/characters/{char_id}/quests")
quests = response.json()
print(f"\nQuests: {quests}")
```

---

## 🎛️ Advanced: Customizing the API

### Adding a New Endpoint

Edit `src/main.py`:

```python
@app.get("/characters/{character_id}/stats")
async def get_character_stats(character_id: int, db: Session = Depends(get_db_session)):
    """Get character statistics"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    conversations = db.query(Conversation).filter(
        Conversation.character_id == character_id
    ).all()

    total_messages = sum(conv.turn_count * 2 for conv in conversations)
    avg_affection = sum(conv.affection_score for conv in conversations) / len(conversations) if conversations else 0

    return {
        "character_id": character_id,
        "name": character.name,
        "total_conversations": len(conversations),
        "total_messages": total_messages,
        "average_affection": avg_affection
    }
```

### Modifying Agent Behavior

Edit prompts in `src/prompts/`:

```python
# src/prompts/chatter_prompts.py

CHAT_SYSTEM = """You are roleplaying as the character described below.

{character_context}

CUSTOM INSTRUCTION: Always end responses with a question to keep the conversation flowing.

...rest of prompt...
"""
```

The changes take effect immediately (no code restart needed if using `--reload`).

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn src.main:app --port 8001
```

### Database Issues
```bash
# Reset database
rm jake.db
python -m src.main  # Will recreate on startup
```

### Import Errors
```bash
# Make sure you're running from project root
cd /Users/dabsdamoon/projects/project-jake

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📚 Next Steps

1. **Read the Docs**: Visit http://localhost:8000/docs
2. **Try Examples**: Run `test_jake.py` or use the cURL examples above
3. **Customize Prompts**: Edit files in `src/prompts/`
4. **Add Quests**: Create quests through the API
5. **Monitor**: Check database with `sqlite3 jake.db`

The system is ready to use! 🚀
