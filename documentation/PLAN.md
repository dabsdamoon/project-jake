# JAKE Chatting Pipeline Plan

## Terminologies
- **JAKE**: 자캐 (자기 캐릭터) in Korean - "self-made character/persona"
- **Turn**: One complete user-assistant exchange (2 messages)
- **Affection Score**: Numeric value (0-100) tracking relationship closeness
- **Quest**: Objective or milestone in character interaction
- **Advancement Quest**: Special quest that unlocks new relationship stages

## Purpose
Combine modular components to create a comprehensive AI chatting system with custom characters (JAKE), featuring:
- Dynamic character generation
- Rich conversational interactions
- Quest-based progression system
- Adaptive character profiles
- Long-term semantic memory

## Architecture Overview

The system uses:
- **LangChain**: LLM integration and chains
- **LangGraph**: State machine orchestration
- **FastAPI**: REST API endpoints
- **SQLAlchemy**: Relational database (characters, conversations, quests)
- **ChromaDB**: Vector database (semantic memory)
- **Centralized Prompt Management**: All prompts managed in `src/prompts/`

## Detailed Process Flow

### Phase 1: Character Creation
1. **User provides basics** → name, age, occupation, additional_info
2. **JAKECreator generates**:
   - Worldview (setting, era, context)
   - Detailed traits (personality, speaking style, likes, dislikes, background, goals)
3. **Save to database** → `Character` table with all generated details

### Phase 2: Conversation Session
4. **Load character** → Retrieve from database by `character_id`
5. **Load/Create session** → Get existing conversation or create new `session_id`
6. **Load context**:
   - Conversation history from `Message` table
   - Active quests from `Quest` table
   - Current affection score and relationship stage
   - Dynamic profile updates (if any)

### Phase 3: Chat Generation
7. **JAKEChatter processes message**:
   - Builds character context from all loaded data
   - Generates response using centralized chat prompt
   - Returns rich output:
     - `dialogue`: Character's spoken words
     - `action`: Physical actions/expressions
     - `situation`: Scene description
     - `background`: Atmosphere/environment
     - `affection_score`: Updated affection (0-100)
     - `affection_change`: Delta from previous (-10 to +10)
     - `internal_thought`: Character's unspoken thoughts

### Phase 4: Post-Chat Processing (Conditional)

**Orchestrated by LangGraph state machine:**

#### Condition A: Turn Count < 3
- ✓ **JAKESummarizer** only
  - Extract atomic facts from conversation
  - Categorize: facts, emotions, key_events, user_info, character_revelations

#### Condition B: 3 ≤ Turn Count < 10
- ✓ **JAKEChecker** - Validate quest completion
  - Regular quests: conversation/action objectives
  - Advancement quests: relationship progression milestones
- ✓ **JAKESummarizer** - Extract memories

#### Condition C: Turn Count ≥ 10
- ✓ **JAKEChecker** - Validate quests
- ✓ **JAKEDynamicProfiler** - Update character profile
  - Identify NEW traits/likes/experiences from conversations
  - Add to dynamic_profile field
- ✓ **JAKESummarizer** - Extract memories

### Phase 5: Database Updates
8. **Save conversation**:
   - Store user message → `Message` table
   - Store assistant response → `Message` table (with rich fields)
   - Update conversation metadata (turn_count, last_interaction)

9. **Update affection & quests**:
   - Update `Conversation.affection_score`
   - Update `Quest.cleared` status (0 or 1)
   - Set `Quest.cleared_at` timestamp if newly cleared

10. **Update dynamic profile** (if applicable):
    - Update `Character.dynamic_profile` with new additions

11. **Store memories**:
    - Save atomic facts → `Memory` table
    - Generate embeddings → Store in ChromaDB
    - Enable semantic search for future context retrieval

### Phase 6: Response
12. **Return to user**:
    - Complete response with dialogue, actions, situation
    - Updated affection score and change
    - Quest completion status
    - Memory extraction count

## LangGraph State Machine

The orchestration is managed by `JAKEOrchestrator` using LangGraph:

```
[Chat Node] → [Decision Node based on turn_count]
    ├─→ [Summarize Node] → END
    ├─→ [Check Quests Node] → [Summarize Node] → END
    └─→ [Check Quests Node] → [Update Profile Node] → [Summarize Node] → END
```

**Benefits:**
- Automatic routing based on conversation stage
- Parallel processing where possible
- Clear state transitions
- Easy to extend with new nodes

## Prompt Management

All prompts centrally managed in `src/prompts/`:
- `creator_prompts.py` - Character generation
- `chatter_prompts.py` - Conversation generation
- `checker_prompts.py` - Quest validation
- `profiler_prompts.py` - Profile updates
- `summarizer_prompts.py` - Memory extraction

Accessed via `PromptManager` class for consistency and maintainability.

## Visualization

See `CHATTING_FLOW.md` for detailed Mermaid diagram of the complete flow.

## Implementation Files

- `src/agents/jake_creator.py` - Character generation
- `src/agents/jake_chatter.py` - Conversation handling
- `src/agents/jake_checker.py` - Quest validation
- `src/agents/jake_dynamic_profiler.py` - Profile updates
- `src/agents/jake_summarizer.py` - Memory extraction
- `src/agents/jake_orchestrator.py` - LangGraph orchestration
- `src/main.py` - FastAPI endpoints
- `src/models/schemas.py` - Database schemas
- `src/utils/vector_store.py` - ChromaDB integration