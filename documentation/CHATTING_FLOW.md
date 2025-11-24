# JAKE Chatting Flow Diagram

This diagram visualizes the chatting pipeline process defined in PLAN.md.

## Flow 1: Enter Chat Room (Load Character)

This flow occurs **once** when a user enters a chat room with a character.

```mermaid
graph TD
    Start([User Enters Chat Room]) --> LoadChar[Load JAKE Character from Database]
    LoadChar --> LoadSession[Load/Create Conversation Session]
    LoadSession --> LoadHistory[Load Conversation History]
    LoadHistory --> LoadQuests[Load Quest Data]
    LoadQuests --> Ready([Character Ready - Session Active])

    style Start fill:#e1f5ff
    style Ready fill:#e1ffe1
    style LoadChar fill:#fff4e1
    style LoadSession fill:#fff4e1
    style LoadHistory fill:#fff4e1
    style LoadQuests fill:#fff4e1
```

---

## Flow 2: Chatting with Character (Message Loop)

This flow occurs **for each message** within an active chat session.

```mermaid
graph TD
    Start([User Sends Message]) --> Chat[JAKEChatter: Generate Response]
    Chat --> |reply + metadata| UpdateTurn[Increment Turn Count]

    UpdateTurn --> CheckTurn{Check Turn Count}

    CheckTurn --> |turns < 3| PostProcess1
    CheckTurn --> |3 ≤ turns < 10| PostProcess2
    CheckTurn --> |turns ≥ 10| PostProcess3

    subgraph PostProcess1 [Async Post-Processing Workers]
        Summarize1[JAKESummarizer]
    end

    subgraph PostProcess2 [Async Post-Processing Workers]
        Checker1[JAKEChecker]
        Summarize2[JAKESummarizer]
    end

    subgraph PostProcess3 [Async Post-Processing Workers]
        Checker2[JAKEChecker]
        Profiler[JAKEDynamicProfiler]
        Summarize3[JAKESummarizer]
    end

    PostProcess1 --> Save1[Save All Updates]
    PostProcess2 --> Save2[Save All Updates]
    PostProcess3 --> Save3[Save All Updates]

    Save1 --> Return[Return Response to User]
    Save2 --> Return
    Save3 --> Return

    Return --> End([Await Next Message])

    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style Chat fill:#fff4e1
    style CheckTurn fill:#ffe1e1
    style Checker1 fill:#e1ffe1
    style Checker2 fill:#e1ffe1
    style Profiler fill:#f0e1ff
    style Summarize1 fill:#ffe1f0
    style Summarize2 fill:#ffe1f0
    style Summarize3 fill:#ffe1f0
    style PostProcess1 fill:#f5f5f5
    style PostProcess2 fill:#f5f5f5
    style PostProcess3 fill:#f5f5f5
```

---

## Sequence Diagram (Detailed View)

This sequence diagram shows the interaction between components with concurrent post-processing.

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator as JAKE Orchestrator
    participant DB as SQL DB
    participant VectorDB as Vector DB
    participant Chatter as JAKEChatter
    participant Checker as JAKEChecker
    participant Profiler as JAKEDynamicProfiler
    participant Summarizer as JAKESummarizer

    User->>Orchestrator: send_message(text)
    Orchestrator->>DB: load session, history, quests
    DB-->>Orchestrator: context
    Orchestrator->>Chatter: generate_reply(context)
    Chatter-->>Orchestrator: reply + metadata (affection, etc.)

    rect rgb(240, 240, 240)
        Note over Checker,Summarizer: Async Post-Processing Workers (Concurrent)
        par validate_quests
            Orchestrator->>Checker: validate_quests(reply, state)
            Checker-->>Orchestrator: quest updates
        and update_profile
            Orchestrator->>Profiler: update_profile(reply, state)
            Profiler-->>Orchestrator: profile diff
        and extract_atomic_facts
            Orchestrator->>Summarizer: extract_atomic_facts(history + reply)
            Summarizer-->>Orchestrator: atomic facts
        end
    end

    Orchestrator->>DB: save history + quests + profile
    Orchestrator->>VectorDB: upsert memories
    Orchestrator-->>User: final response (dialogue + status)
```

---

## Detailed Flow Description

### Flow 1: Enter Chat Room

#### 1.1 Character Loading (One-time)
- User selects a character and enters the chat room
- System loads JAKE character (created by JAKECreator) from database
- Loads or creates conversation session for this user-character pair
- Retrieves existing conversation history
- Loads quest data associated with this character

#### 1.2 Session State
- Character data is cached in active session
- Subsequent messages don't require character reload
- Session remains active until user exits chat room

---

### Flow 2: Message Loop

#### 2.1 Chat Generation (Always Runs)
- **JAKEChatter** generates rich response:
  - Dialogue (what character says)
  - Action (physical actions/expressions)
  - Situation (scene description)
  - Background (atmosphere)
  - Affection score and change

#### 2.2 Post-Chat Processing (Concurrent Async Workers)

All applicable workers run **concurrently** using async wrappers:

| Turn Count | Active Workers |
|------------|----------------|
| < 3 | JAKESummarizer only |
| 3 - 9 | JAKEChecker + JAKESummarizer |
| ≥ 10 | JAKEChecker + JAKEDynamicProfiler + JAKESummarizer |

**Worker Details:**
- **JAKEChecker**: Validates quest completion status
- **JAKEDynamicProfiler**: Updates character profile with newly discovered traits
- **JAKESummarizer**: Extracts atomic facts for long-term memory

#### 2.3 Database Updates (After Workers Complete)
- Quest statuses updated in SQL DB
- Character dynamic profile updated in SQL DB (if applicable)
- Atomic facts embedded and upserted to Vector DB
- Chat history saved to SQL DB

#### 2.4 Response
- Return complete response to user with:
  - Dialogue and actions
  - Updated affection score
  - Quest completion status
  - Memory extraction count

---

## LangGraph State Machine

The orchestration is managed by a LangGraph state machine in `src/agents/jake_orchestrator.py` that:
- Manages session state and character context
- Routes between nodes based on turn count
- Executes post-processing workers concurrently using `asyncio.gather()`
