# JAKE Documentation

Welcome to the JAKE (자캐 - 자기 캐릭터) project documentation!

## Quick Start

### 1. Prerequisites

Make sure you have Conda installed:
- **Miniconda** (recommended): https://docs.conda.io/en/latest/miniconda.html
- **Anaconda**: https://www.anaconda.com/download

```bash
conda --version
```

### 2. Setup Environment

```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate jake
```

### 3. Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit and add your OpenAI API key
nano .env
```

Add to `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=sqlite:///./jake.db
CHROMA_PERSIST_DIR=./chroma_db
HOST=0.0.0.0
PORT=8000
```

### 4. Run the Server

```bash
# Option A: Using startup script (Recommended)
./start_server.sh

# Option B: Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API:
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/ping

---

## Using the API

### Create a Character

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

### Chat with Character

```bash
curl -X POST "http://localhost:8000/characters/1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! This cafe looks really cozy."
  }'
```

### Continue Conversation (with Session)

```bash
curl -X POST "http://localhost:8000/characters/1/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: YOUR_SESSION_ID" \
  -d '{
    "message": "What kind of books do you like?"
  }'
```

### Create a Quest

```bash
curl -X POST "http://localhost:8000/characters/1/quests" \
  -H "Content-Type: application/json" \
  -d '{
    "quest_type": "regular",
    "title": "Getting to Know Each Other",
    "description": "Ask about Luna'\''s favorite book"
  }'
```

### Search Memories

```bash
curl -X GET "http://localhost:8000/characters/1/memories?query=favorite%20book&limit=5"
```

---

## Conda Environment Management

### Update Environment

```bash
conda activate jake
conda env update -f environment.yml --prune
```

### Add New Package

```bash
conda activate jake
pip install your-new-package
pip freeze > requirements.txt
```

### Remove/Recreate Environment

```bash
conda deactivate
conda env remove -n jake
conda env create -f environment.yml
```

---

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9
# Or use different port
uvicorn src.main:app --port 8001
```

### Database Issues
```bash
rm jake.db
python -m src.main  # Will recreate on startup
```

### OpenAI API Errors
```bash
# Check if .env is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'Found' if os.getenv('OPENAI_API_KEY') else 'Missing')"
```

### Conda Environment Not Activating
```bash
conda init bash  # or zsh
source ~/.bashrc
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, flow diagrams, component connections |
| [COMPONENTS.md](./COMPONENTS.md) | All 10 component specifications and prompt management |
| [TESTING.md](./TESTING.md) | API testing guide with examples |

---

## External Resources

- **OpenAI API Docs**: https://platform.openai.com/docs
- **LangChain Docs**: https://python.langchain.com/docs
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **ChromaDB Docs**: https://docs.trychroma.com/
- **Conda User Guide**: https://docs.conda.io/projects/conda/en/latest/user-guide/
