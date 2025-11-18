# JAKE Documentation Index

Welcome to the JAKE (자캐) project documentation!

## 📚 Documentation Overview

### Getting Started
1. **[GETTING_STARTED.md](./GETTING_STARTED.md)** - Complete guide to running the JAKE API
   - Installation steps
   - API examples
   - Testing the system
   - Troubleshooting

2. **[CONDA_SETUP.md](./CONDA_SETUP.md)** - Conda environment setup
   - Creating conda environment
   - Environment management
   - Best practices
   - Troubleshooting

### Architecture & Design
3. **[PLAN.md](./PLAN.md)** - Detailed process flow and pipeline
   - System architecture
   - 6-phase conversation flow
   - LangGraph state machine
   - Database operations

4. **[COMPONENTS.md](./COMPONENTS.md)** - Complete component specifications
   - All 10 system components
   - Method signatures and schemas
   - Database models
   - API endpoints

5. **[CHATTING_FLOW.md](./CHATTING_FLOW.md)** - Visual flow diagram
   - Mermaid diagram of conversation pipeline
   - Step-by-step flow description
   - Conditional routing logic

### Implementation Details
6. **[API_CONNECTION_GUIDE.md](./API_CONNECTION_GUIDE.md)** - How components connect
   - Detailed connection architecture
   - Request-response flow
   - Code-level explanations
   - Extension guide

7. **[PROMPT_MANAGEMENT.md](./PROMPT_MANAGEMENT.md)** - Prompt system guide
   - Centralized prompt structure
   - How to modify prompts
   - Best practices

---

## 🎯 Quick Navigation by Task

### I want to...

#### ...get started quickly
→ Read **[GETTING_STARTED.md](./GETTING_STARTED.md)**

#### ...set up conda environment
→ Read **[CONDA_SETUP.md](./CONDA_SETUP.md)**

#### ...understand the system architecture
→ Read **[PLAN.md](./PLAN.md)** and **[COMPONENTS.md](./COMPONENTS.md)**

#### ...see how data flows through the system
→ Read **[CHATTING_FLOW.md](./CHATTING_FLOW.md)** and **[API_CONNECTION_GUIDE.md](./API_CONNECTION_GUIDE.md)**

#### ...modify prompts
→ Read **[PROMPT_MANAGEMENT.md](./PROMPT_MANAGEMENT.md)**

#### ...understand a specific component
→ Read **[COMPONENTS.md](./COMPONENTS.md)** (sections 1-10)

#### ...add new features
→ Read **[API_CONNECTION_GUIDE.md](./API_CONNECTION_GUIDE.md)** (extension guide)

---

## 📖 Recommended Reading Order

### For New Users:
1. [GETTING_STARTED.md](./GETTING_STARTED.md) - Run the system
2. [CHATTING_FLOW.md](./CHATTING_FLOW.md) - Understand the flow
3. [COMPONENTS.md](./COMPONENTS.md) - Learn about components

### For Developers:
1. [PLAN.md](./PLAN.md) - Understand architecture
2. [COMPONENTS.md](./COMPONENTS.md) - Study all components
3. [API_CONNECTION_GUIDE.md](./API_CONNECTION_GUIDE.md) - See how it connects
4. [PROMPT_MANAGEMENT.md](./PROMPT_MANAGEMENT.md) - Learn prompt system

### For Contributors:
1. [CONDA_SETUP.md](./CONDA_SETUP.md) - Set up environment
2. [API_CONNECTION_GUIDE.md](./API_CONNECTION_GUIDE.md) - Understand architecture
3. [PROMPT_MANAGEMENT.md](./PROMPT_MANAGEMENT.md) - Modify prompts
4. [COMPONENTS.md](./COMPONENTS.md) - Reference specifications

---

## 📊 Document Statistics

| Document | Purpose | Lines | Key Topics |
|----------|---------|-------|------------|
| GETTING_STARTED.md | Tutorial | ~400 | Setup, examples, testing |
| CONDA_SETUP.md | Environment | ~200 | Conda, dependencies |
| PLAN.md | Architecture | ~150 | Flow, phases, orchestration |
| COMPONENTS.md | Specifications | ~650 | All 10 components, schemas |
| CHATTING_FLOW.md | Visual | ~100 | Mermaid diagram, flow |
| API_CONNECTION_GUIDE.md | Implementation | ~600 | Connections, code details |
| PROMPT_MANAGEMENT.md | System Guide | ~100 | Prompts, editing |

**Total**: ~2,200 lines of documentation

---

## 🔗 External Resources

- **GitHub Repository**: [Link to repo]
- **OpenAI API Docs**: https://platform.openai.com/docs
- **LangChain Docs**: https://python.langchain.com/docs
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **ChromaDB Docs**: https://docs.trychroma.com/

---

## 🤝 Contributing to Documentation

To improve this documentation:

1. Edit the relevant markdown file
2. Follow the existing structure and formatting
3. Add examples where helpful
4. Keep it concise but comprehensive
5. Update this INDEX.md if adding new documents

---

## 📝 Documentation Structure

```
documentation/
├── INDEX.md                      # This file
├── GETTING_STARTED.md            # Getting started guide
├── CONDA_SETUP.md                # Conda setup
├── PLAN.md                       # Architecture and flow
├── COMPONENTS.md                 # Component specifications
├── CHATTING_FLOW.md              # Visual flow diagram
├── API_CONNECTION_GUIDE.md       # Connection details
└── PROMPT_MANAGEMENT.md          # Prompt system
```

---

**Last Updated**: November 19, 2025
