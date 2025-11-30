# JAKE API Testing Guide

Complete guide for testing all JAKE API endpoints.

## 🧪 Available Test Scripts

### Unified Test Runner (Recommended)
**File**: `run_tests.sh`

One command to run all tests:
- ✅ Runs unit tests first (no server needed)
- ✅ Checks if API server is running
- ✅ Runs API endpoint tests
- ✅ Beautiful summary output
- ✅ Flexible options (unit-only, api-only, custom port)

### API Endpoint Tests
**File**: `tests/test_api_simple.sh`

Shell-based test suite for all 9 API endpoints:
- ✅ Fast execution
- ✅ Minimal dependencies (curl + jq)
- ✅ Tests all endpoints sequentially
- ✅ Validates responses with error checking
- ✅ JSON formatted output
- ✅ Fails fast on errors (exits immediately if API is down)

### Manual Testing
Using curl commands directly for specific tests (see below).

---

## 🚀 Running Tests

### Quick Start (Unified Test Runner)

```bash
# Make sure server is running first
./start_server.sh &
sleep 10

# Run all tests
./run_tests.sh

# Or run only specific tests
./run_tests.sh --unit-only    # No server needed
./run_tests.sh --api-only     # Requires server
./run_tests.sh 8001           # Custom port
```

### Running Individual Test Script

**1. Start the Server**
```bash
# In one terminal (default port 8000)
./start_server.sh

# Or with custom port
./start_server.sh 8001
```

**2. Run the tests**
```bash
# Requires jq for JSON parsing
# Install: brew install jq (Mac) or apt-get install jq (Linux)

./tests/test_api_simple.sh        # Default port 8000
./tests/test_api_simple.sh 8001   # Custom port 8001
```

**Example Output (Success):**
```
Testing JAKE API at: http://localhost:8000

Test 1: Health Check
{
  "status": "healthy"
}
✓ API is healthy

Test 2: Create Character
Created Character ID: 1
Name: Luna

Character Details:
{
  "personality": "Warm, caring, slightly shy...",
  "quirks": "Often hums while working, tucks hair behind ear when nervous...",
  "speaking_style": "Gentle and soft-spoken...",
  "likes": "Books, rainy days, warm tea...",
  "dislikes": "Loud noises, confrontation...",
  "background": "Inherited cafe from grandmother...",
  "goals": "Create a welcoming space..."
}
✓ Character created successfully

...

========================================
✓ All 9 tests completed successfully!
========================================
```

**Example Output (Failure - API not running):**
```
Testing JAKE API at: http://localhost:8000

Test 1: Health Check
❌ FAILED: API is not responding (HTTP 000)
Make sure the server is running:
  ./start_server.sh 8000
```

---

## Manual cURL Commands

Test individual endpoints:

#### 1. Health Check
```bash
curl http://localhost:8000/ping
```

#### 2. Create Character
```bash
curl -X POST "http://localhost:8000/characters" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "Luna",
    "age": "25",
    "occupation": "Cafe owner",
    "additional_info": "Loves books"
  }'
```

#### 3. Get Character
```bash
curl "http://localhost:8000/characters/1"
```

#### 4. Chat (First Message)
```bash
curl -X POST "http://localhost:8000/characters/1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Nice to meet you."
  }'
```

#### 5. Chat (With Session)
```bash
# Save session_id from previous response
curl -X POST "http://localhost:8000/characters/1/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: YOUR_SESSION_ID" \
  -d '{
    "message": "What do you like to do?"
  }'
```

#### 6. Create Quest
```bash
curl -X POST "http://localhost:8000/characters/1/quests" \
  -H "Content-Type: application/json" \
  -d '{
    "quest_type": "regular",
    "title": "First Meeting",
    "description": "Introduce yourself"
  }'
```

#### 7. List Quests
```bash
curl "http://localhost:8000/characters/1/quests"
```

#### 8. Get Conversation History
```bash
curl "http://localhost:8000/conversations/YOUR_SESSION_ID"
```

#### 9. Search Memories
```bash
curl "http://localhost:8000/characters/1/memories?query=books&limit=5"
```

#### 10. List User Characters
```bash
curl "http://localhost:8000/users/user123/characters"
```

---

## 📋 Test Checklist

Use this checklist to manually verify all functionality:

- [ ] Server starts successfully
- [ ] Health check responds
- [ ] Can create character
- [ ] Character generation includes worldview and details
- [ ] Can retrieve character by ID
- [ ] Can send first chat message
- [ ] Session ID is returned
- [ ] Can continue chat with session
- [ ] Affection score changes appropriately
- [ ] Turn count increments
- [ ] Can create regular quest
- [ ] Can create advancement quest
- [ ] Quest list shows all quests
- [ ] Conversation history is saved
- [ ] Messages include rich fields (dialogue, action, etc.)
- [ ] Memories are extracted
- [ ] Memory search returns relevant results
- [ ] Can list user's characters
- [ ] Multiple conversations work independently

---

## 🔍 What Each Test Validates

### Test 1: Health Check
- ✓ Server is running
- ✓ API is accessible
- ✓ Basic connectivity works

### Test 2: Create Character
- ✓ JAKECreator generates worldview
- ✓ JAKECreator generates details
- ✓ Character saved to database
- ✓ All required fields present
- ✓ LLM integration working

### Test 3: Get Character
- ✓ Database retrieval works
- ✓ Character data persists
- ✓ All fields accessible

### Test 4: First Chat
- ✓ JAKEChatter generates response
- ✓ Session created
- ✓ Dialogue generated
- ✓ Actions and context provided
- ✓ Affection tracking works
- ✓ JAKESummarizer extracts memories
- ✓ Messages saved to database

### Test 5: Chat with Session
- ✓ Session continuity works
- ✓ History loading works
- ✓ Context maintained across turns
- ✓ Affection score updates
- ✓ Turn count increments
- ✓ Orchestrator routing works (< 3, < 10, >= 10)

### Test 6: Create Quest
- ✓ Quest creation works
- ✓ Quest saved to database
- ✓ Quest types supported (regular/advancement)

### Test 7: List Quests
- ✓ Quest retrieval works
- ✓ Regular and advancement quests separated
- ✓ Quest status visible

### Test 8: Conversation History
- ✓ Full conversation retrieval
- ✓ All messages saved
- ✓ Rich fields preserved (dialogue, action, etc.)
- ✓ Conversation metadata accurate

### Test 9: Search Memories
- ✓ Vector store working
- ✓ Embeddings generated
- ✓ Semantic search works
- ✓ Relevant results returned

### Test 10: List User Characters
- ✓ User-character relationship works
- ✓ Multiple characters per user supported
- ✓ Character filtering works

---

## 🐛 Troubleshooting

### Server Not Running
```bash
# Error: Connection refused

# Solution:
./start_server.sh
# or
conda activate jake
python -m src.main
```

### Port Already in Use
```bash
# Error: Address already in use

# Solution: Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port:
uvicorn src.main:app --port 8001
```

### OpenAI API Errors
```bash
# Error: Authentication failed

# Solution: Check your .env file
cat .env
# Make sure OPENAI_API_KEY is set correctly
```

### Slow Character Creation
```
# Character creation takes 10-30 seconds (normal)
# It generates worldview + detailed traits using LLM
```

### Test Failures
```bash
# Check logs
# The Python test suite shows detailed error messages

# Check server logs
# Look at the terminal where server is running

# Verify database
sqlite3 jake.db "SELECT * FROM characters;"
```

---

## 📊 Performance Benchmarks

Typical response times:

| Endpoint | Expected Time |
|----------|---------------|
| /ping | < 50ms |
| POST /characters | 10-30s (LLM generation) |
| GET /characters/{id} | < 100ms |
| POST /chat (first) | 3-10s (LLM + memory) |
| POST /chat (continued) | 3-10s |
| POST /quests | < 100ms |
| GET /quests | < 100ms |
| GET /conversations | < 200ms |
| GET /memories | < 500ms (vector search) |

---

## 🔄 Continuous Testing

### During Development

```bash
# Terminal 1: Run server
./start_server.sh

# Terminal 2: Watch for changes and test
watch -n 30 python test_api_endpoints.py
```

### Automated Testing

Add to CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: API Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Conda
        uses: conda-incubator/setup-miniconda@v2
      - name: Install dependencies
        run: conda env create -f environment.yml
      - name: Start server
        run: |
          conda activate jake
          python -m src.main &
          sleep 10
      - name: Run tests
        run: python test_api_endpoints.py
```

---

## 📝 Creating Custom Tests

### Add a New Test Function

```python
def test_my_new_endpoint(self) -> bool:
    """Test: GET /my-endpoint - Description"""
    self.print_test("My New Endpoint (GET /my-endpoint)")

    try:
        response = requests.get(f"{self.base_url}/my-endpoint")

        if response.status_code == 200:
            data = response.json()
            self.print_success("Endpoint works!")
            self.print_data("Result", data)
            self.record_result("My New Endpoint", True)
            return True
        else:
            self.print_error(f"Failed: {response.status_code}")
            self.record_result("My New Endpoint", False)
            return False
    except Exception as e:
        self.print_error(f"Error: {e}")
        self.record_result("My New Endpoint", False, str(e))
        return False
```

### Add to Test Suite

```python
def run_all_tests(self):
    # ... existing tests ...
    self.test_my_new_endpoint()
    # ... rest of tests ...
```

---

## ✅ Test Coverage

Current coverage:

- ✅ Character management (create, get, list)
- ✅ Chat functionality (first message, with session)
- ✅ Quest system (create, list, check)
- ✅ Memory system (extract, search)
- ✅ Conversation history
- ✅ Session management
- ✅ Database operations
- ✅ Vector store operations

---

**For more details, see:**
- [README.md](./README.md) - Setup guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [COMPONENTS.md](./COMPONENTS.md) - Component specifications
