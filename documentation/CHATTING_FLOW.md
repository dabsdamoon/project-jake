# JAKE Chatting Flow Diagram

This diagram visualizes the chatting pipeline process defined in PLAN.md.

```mermaid
graph TD
    Start([User Sends Message]) --> LoadChar[Load JAKE Character from Database]
    LoadChar --> LoadSession[Load/Create Conversation Session]
    LoadSession --> LoadHistory[Load Conversation History]
    LoadHistory --> LoadQuests[Load Quest Data]

    LoadQuests --> Chat[JAKEChatter: Generate Response]
    Chat --> |dialogue, action, situation, background, affection| UpdateTurn[Increment Turn Count]

    UpdateTurn --> CheckTurn{Check Turn Count}

    CheckTurn --> |turns < 3| Summarize1[JAKESummarizer Only]
    CheckTurn --> |3 ≤ turns < 10| Branch2[JAKEChecker + JAKESummarizer]
    CheckTurn --> |turns ≥ 10| Branch3[All Three Components]

    Branch2 --> Checker1[JAKEChecker: Validate Quests]
    Branch2 --> Summarize2[JAKESummarizer: Extract Memories]

    Branch3 --> Checker2[JAKEChecker: Validate Quests]
    Branch3 --> Profiler[JAKEDynamicProfiler: Update Profile]
    Branch3 --> Summarize3[JAKESummarizer: Extract Memories]

    Checker1 --> |Updated quest status| SaveQuests1[Update Quest Database]
    Checker2 --> |Updated quest status| SaveQuests2[Update Quest Database]

    Profiler --> |Dynamic profile additions| UpdateChar[Update Character Database]

    Summarize1 --> |Atomic facts| SaveMemory1[Save to Vector DB]
    Summarize2 --> |Atomic facts| SaveMemory2[Save to Vector DB]
    Summarize3 --> |Atomic facts| SaveMemory3[Save to Vector DB]

    SaveQuests1 --> SaveHistory1[Save Chat History]
    SaveQuests2 --> SaveHistory2[Save Chat History]
    UpdateChar --> SaveHistory3[Save Chat History]
    SaveMemory1 --> SaveHistory1
    SaveMemory2 --> SaveHistory2
    SaveMemory3 --> SaveHistory3

    SaveHistory1 --> Return1[Return Response to User]
    SaveHistory2 --> Return2[Return Response to User]
    SaveHistory3 --> Return3[Return Response to User]

    Return1 --> End([End])
    Return2 --> End
    Return3 --> End

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
```

## Detailed Flow Description

### 1. Initialization Phase
- User sends a message
- System loads JAKE character from database
- Loads or creates conversation session
- Retrieves conversation history and quest data

### 2. Chat Generation (Always Runs)
- **JAKEChatter** generates rich response:
  - Dialogue (what character says)
  - Action (physical actions/expressions)
  - Situation (scene description)
  - Background (atmosphere)
  - Affection score and change

### 3. Post-Chat Processing (Conditional)

#### Turn Count < 3
- **JAKESummarizer only**: Extract atomic facts for memory

#### Turn Count 3-9
- **JAKEChecker**: Validate quest completion
- **JAKESummarizer**: Extract atomic facts

#### Turn Count ≥ 10
- **JAKEChecker**: Validate quest completion
- **JAKEDynamicProfiler**: Update character profile with new traits
- **JAKESummarizer**: Extract atomic facts

### 4. Database Updates
- Quest statuses updated
- Character dynamic profile updated (if applicable)
- Memories embedded and saved to vector database
- Chat history saved to SQL database

### 5. Response
- Return complete response to user with:
  - Dialogue and actions
  - Updated affection score
  - Quest completion status
  - Memory extraction count

## LangGraph State Machine

The orchestration is managed by a LangGraph state machine in `src/agents/jake_orchestrator.py` that automatically routes between nodes based on turn count.
