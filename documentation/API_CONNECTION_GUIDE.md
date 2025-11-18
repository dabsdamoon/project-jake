# How FastAPI Connects All JAKE Components

## 🔗 Connection Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER REQUEST                            │
│          (HTTP: POST /characters/1/chat)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                        │
│                    (src/main.py)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  @app.post("/characters/{character_id}/chat")        │   │
│  │  async def chat_with_character(...):                 │   │
│  │      1. Load character from DB                       │   │
│  │      2. Load conversation session                    │   │
│  │      3. Load history & quests                        │   │
│  │      4. Call orchestrator.process_message()    ◄─────┼───┼─┐
│  │      5. Save results to DB                           │   │ │
│  │      6. Return JSON response                         │   │ │
│  └──────────────────────────────────────────────────────┘   │ │
└─────────────────────────────────────────────────────────────┘ │
                                                                 │
┌────────────────────────────────────────────────────────────────┘
│
│  ┌─────────────────────────────────────────────────────────┐
└─▶│              JAKEOrchestrator                            │
   │         (src/agents/jake_orchestrator.py)                │
   │  ┌───────────────────────────────────────────────────┐  │
   │  │          LangGraph State Machine                  │  │
   │  │                                                   │  │
   │  │  Entry: chat_node()                              │  │
   │  │    ↓                                              │  │
   │  │  [Calls JAKEChatter]                             │  │
   │  │    ↓                                              │  │
   │  │  Decision: route_after_chat()                    │  │
   │  │    ├─ turns < 3  → summarize_node()             │  │
   │  │    ├─ turns < 10 → check_quests → summarize     │  │
   │  │    └─ turns ≥ 10 → check → profile → summarize  │  │
   │  └───────────────────────────────────────────────────┘  │
   └────────────┬────────────┬────────────┬───────────────────┘
                │            │            │
      ┌─────────┴────┐  ┌────┴─────┐  ┌──┴──────────┐
      ▼              ▼              ▼                 ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐
│  JAKE    │  │  JAKE    │  │  JAKE    │  │     JAKE       │
│ Creator  │  │ Chatter  │  │ Checker  │  │ Summarizer     │
└──────────┘  └────┬─────┘  └──────────┘  └────────────────┘
                   │              │               │
              ┌────┴──────────┐   │               │
              ▼               │   │               │
        ┌──────────┐          │   │               │
        │  JAKE    │          │   │               │
        │ Dynamic  │          │   │               │
        │ Profiler │          │   │               │
        └────┬─────┘          │   │               │
             │                │   │               │
             └────────┬───────┴───┴───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │    PromptManager             │
        │  (Centralized Prompts)       │
        │                              │
        │  • creator_prompts.py        │
        │  • chatter_prompts.py        │
        │  • checker_prompts.py        │
        │  • profiler_prompts.py       │
        │  • summarizer_prompts.py     │
        └──────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │       OpenAI GPT-4o          │
        │    (LLM Processing)          │
        └──────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────────┐
        │          Response Aggregation            │
        │  • Dialogue, action, situation           │
        │  • Affection score                       │
        │  • Quest status                          │
        │  • Memories                              │
        └──────────────┬──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │         Data Persistence Layer           │
        │                                          │
        │  ┌────────────────┐  ┌────────────────┐ │
        │  │   SQL Database │  │  Vector Store  │ │
        │  │  (SQLAlchemy)  │  │   (ChromaDB)   │ │
        │  │                │  │                │ │
        │  │  • Character   │  │  • Embeddings  │ │
        │  │  • Conversation│  │  • Semantic    │ │
        │  │  • Message     │  │    Search      │ │
        │  │  • Quest       │  │                │ │
        │  │  • Memory      │  │                │ │
        │  └────────────────┘  └────────────────┘ │
        └──────────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │       JSON Response           │
        │  {                            │
        │    "dialogue": "...",         │
        │    "action": "...",           │
        │    "affection_score": 55,     │
        │    ...                        │
        │  }                            │
        └──────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │         USER RECEIVES         │
        │      Complete Response        │
        └──────────────────────────────┘
```

---

## 🔑 Key Connection Points

### 1. FastAPI Initialization (`src/main.py`)

```python
# Lines 16-18
app = FastAPI(
    title="JAKE API",
    description="API for creating and chatting with custom AI characters",
)

# Lines 35-36
orchestrator = JAKEOrchestrator()  # ← Connects all agents!
vector_store = VectorMemoryStore()  # ← Vector DB connection
```

### 2. The Main Chat Endpoint (Line 144)

This is where **everything connects**:

```python
@app.post("/characters/{character_id}/chat")
async def chat_with_character(
    character_id: int,
    chat_request: ChatRequest,
    db: Session = Depends(get_db_session)  # ← DB connection
):
```

**What happens inside**:

```python
# Step 1: Load character (Lines 156-159)
character = db.query(Character).filter(Character.id == character_id).first()

# Step 2: Load/create session (Lines 161-180)
if session_id:
    conversation = db.query(Conversation).filter(...).first()
else:
    conversation = Conversation(...)  # Create new

# Step 3: Load history (Lines 182-187)
messages = db.query(Message).filter(...).all()
history = [{"role": msg.role, "content": msg.content} for msg in messages]

# Step 4: Load quests (Lines 189-211)
quests = db.query(Quest).filter(...).all()
regular_quests = {...}
advancement_quests = {...}

# Step 5: Build character dict (Lines 213-221)
character_dict = {
    "basics": {...},
    "worldview": character.worldview,
    "details": character.details,
    "dynamic_profile": character.dynamic_profile
}

# Step 6: ⭐ THE MAGIC ⭐ - Call orchestrator (Lines 223-231)
result = orchestrator.process_message(
    user_message=chat_request.message,
    character=character_dict,
    history=history,
    regular_quests=regular_quests,
    advancement_quests=advancement_quests,
    current_affection=conversation.affection_score,
    relationship_stage=conversation.relationship_stage
)

# Step 7: Save to database (Lines 233-271)
# - Save user message
# - Save assistant response
# - Update affection
# - Update quests
# - Update character profile
# - Store memories in vector DB

# Step 8: Return response (Lines 273-285)
return {
    "session_id": session_id,
    "dialogue": response["dialogue"],
    ...
}
```

### 3. Orchestrator Connection (`src/agents/jake_orchestrator.py`)

```python
class JAKEOrchestrator:
    def __init__(self):
        # ⭐ This connects all 5 agents ⭐
        self.creator = JAKECreator()        # Line 38
        self.chatter = JAKEChatter()        # Line 39
        self.checker = JAKEChecker()        # Line 40
        self.profiler = JAKEDynamicProfiler()  # Line 41
        self.summarizer = JAKESummarizer()  # Line 42

        # Build LangGraph state machine
        self.graph = self._build_graph()    # Line 45

    def process_message(self, ...):
        # Run through state machine
        result = self.graph.invoke(initial_state)  # Line 200
        return result
```

### 4. Agent → PromptManager Connection

**Every agent** uses the PromptManager:

```python
# In each agent's __init__:
self.prompt_manager = PromptManager()

# Then in methods:
prompt = self.prompt_manager.get_chat_prompt()  # ← Centralized!
chain = prompt | self.llm | parser
result = chain.invoke(...)
```

### 5. Database Connection (`src/database/connection.py`)

```python
# Lines 13-16
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Line 21
def init_db():
    Base.metadata.create_all(bind=engine)

# Lines 31-38
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI uses this via dependency injection:
```python
def my_endpoint(db: Session = Depends(get_db_session)):
    # db is automatically provided!
```

---

## 🎯 Request → Response Flow

### Example: User sends "Hello!"

```
1. HTTP POST /characters/1/chat {"message": "Hello!"}
   ↓
2. FastAPI endpoint receives request
   ↓
3. Load character #1 from database
   ↓
4. Load conversation session (or create new)
   ↓
5. Load conversation history
   ↓
6. Load character's quests
   ↓
7. Call orchestrator.process_message(
       user_message="Hello!",
       character={...},
       history=[...],
       ...
   )
   ↓
8. Orchestrator invokes LangGraph state machine:
   │
   ├─> chat_node():
   │   └─> JAKEChatter.chat()
   │       └─> PromptManager.get_chat_prompt()
   │           └─> OpenAI GPT-4o
   │               └─> Returns: {dialogue, action, affection, ...}
   │
   ├─> route_after_chat() [decides based on turn_count]
   │   └─> If turns < 3: go to summarize_node
   │   └─> If turns < 10: go to check_quests → summarize
   │   └─> If turns ≥ 10: go to check_quests → profile → summarize
   │
   ├─> check_quests_node() [if applicable]:
   │   └─> JAKEChecker.check_quests()
   │       └─> Returns: {updated_quests}
   │
   ├─> update_profile_node() [if applicable]:
   │   └─> JAKEDynamicProfiler.update_profile()
   │       └─> Returns: {updated_dynamic_profile}
   │
   └─> summarize_node():
       └─> JAKESummarizer.get_memory()
           └─> Returns: {facts, emotions, key_events, ...}
   ↓
9. Orchestrator returns complete result:
   {
       "response": {...},
       "updated_affection": 52,
       "updated_quests": {...},
       "updated_dynamic_profile": "...",
       "memories": {...}
   }
   ↓
10. FastAPI endpoint saves everything:
    ├─> Save user message to Message table
    ├─> Save assistant response to Message table
    ├─> Update Conversation.affection_score
    ├─> Update Quest.cleared status
    ├─> Update Character.dynamic_profile
    └─> For each memory fact:
        ├─> Save to Memory table
        └─> Generate embedding & save to ChromaDB
    ↓
11. FastAPI returns JSON response:
    {
        "session_id": "abc-123",
        "dialogue": "Hello! *smiles warmly* Welcome!",
        "action": "*waves hand*",
        "affection_score": 52,
        ...
    }
    ↓
12. User receives response
```

---

## 🛠️ How to Extend the System

### Add a New Agent

1. **Create agent file**: `src/agents/jake_newagent.py`
```python
from src.prompts import PromptManager

class JAKENewAgent:
    def __init__(self):
        self.llm = ChatOpenAI(...)
        self.prompt_manager = PromptManager()

    def process(self, input_data):
        prompt = self.prompt_manager.get_new_prompt()
        result = (prompt | self.llm | parser).invoke(input_data)
        return result
```

2. **Add prompt**: `src/prompts/newagent_prompts.py`
```python
NEW_PROMPT_SYSTEM = """Your prompt here"""
```

3. **Update PromptManager**: `src/prompts/prompt_manager.py`
```python
@staticmethod
def get_new_prompt():
    from .newagent_prompts import NEW_PROMPT_SYSTEM
    return ChatPromptTemplate.from_messages([...])
```

4. **Add to Orchestrator**: `src/agents/jake_orchestrator.py`
```python
def __init__(self):
    ...
    self.new_agent = JAKENewAgent()

def _build_graph(self):
    ...
    workflow.add_node("new_node", self._new_node)

def _new_node(self, state):
    result = self.new_agent.process(state["data"])
    state["new_result"] = result
    return state
```

5. **Use in FastAPI**: `src/main.py`
```python
# It's automatically available through the orchestrator!
```

### Add a New Endpoint

In `src/main.py`:
```python
@app.get("/characters/{character_id}/relationship-status")
async def get_relationship_status(
    character_id: int,
    db: Session = Depends(get_db_session)
):
    conversations = db.query(Conversation).filter(...).all()

    return {
        "character_id": character_id,
        "total_conversations": len(conversations),
        "average_affection": ...,
        "relationship_stage": ...,
        "milestones_reached": ...
    }
```

---

## 📊 Monitoring Connections

### Check if all components are connected:

```python
# test_connections.py
from src.agents.jake_orchestrator import JAKEOrchestrator
from src.database.connection import get_db, init_db
from src.utils.vector_store import VectorMemoryStore

print("Testing connections...")

# 1. Test orchestrator
orchestrator = JAKEOrchestrator()
print(f"✓ Orchestrator loaded")
print(f"  - Creator: {orchestrator.creator}")
print(f"  - Chatter: {orchestrator.chatter}")
print(f"  - Checker: {orchestrator.checker}")
print(f"  - Profiler: {orchestrator.profiler}")
print(f"  - Summarizer: {orchestrator.summarizer}")

# 2. Test database
init_db()
print("✓ Database initialized")

# 3. Test vector store
vector_store = VectorMemoryStore()
print("✓ Vector store connected")

print("\n✅ All components connected successfully!")
```

Run it:
```bash
python test_connections.py
```

---

## 🎉 Summary

The connection is **already complete** in your implementation:

1. **FastAPI** (`src/main.py`) exposes HTTP endpoints
2. **Orchestrator** (`jake_orchestrator.py`) coordinates all agents via LangGraph
3. **5 Agents** each handle specific tasks and use **PromptManager**
4. **Database** stores persistent data (SQLAlchemy)
5. **Vector Store** enables semantic memory search (ChromaDB)

Everything is connected through **dependency injection** and **orchestration patterns**.

Just run:
```bash
./start_server.sh
```

And you're ready to go! 🚀
