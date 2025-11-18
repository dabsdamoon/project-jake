"""
JAKE API - FastAPI main application
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import json
from datetime import datetime

from src.agents.jake_orchestrator import JAKEOrchestrator
from src.database.connection import get_db_session, init_db
from src.models.schemas import Character, Conversation, Message, Quest, Memory
from src.utils.vector_store import VectorMemoryStore

# Initialize FastAPI app
app = FastAPI(
    title="JAKE API",
    description="API for creating and chatting with custom AI characters (JAKE)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator and vector store
orchestrator = JAKEOrchestrator()
vector_store = VectorMemoryStore()


# Pydantic models for API
class CharacterCreate(BaseModel):
    """Request model for creating a character"""
    user_id: str
    name: str
    age: str
    occupation: str
    additional_info: Optional[str] = ""


class ChatRequest(BaseModel):
    """Request model for chat"""
    message: str
    session_id: Optional[str] = None


class QuestCreate(BaseModel):
    """Request model for creating a quest"""
    quest_type: str  # 'regular' or 'advancement'
    title: str
    description: str
    required_affection: int = 0


# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


# Health check
@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {"status": "healthy", "service": "JAKE API"}


# Character endpoints
@app.post("/characters")
async def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db_session)
):
    """
    Create a new JAKE character

    Process:
    1. Use JAKECreator to generate character details
    2. Save to database
    3. Return character info
    """
    # Create character using orchestrator
    character_basics = {
        "name": character_data.name,
        "age": character_data.age,
        "occupation": character_data.occupation,
        "additional_info": character_data.additional_info
    }

    character_profile = orchestrator.create_character(character_basics)

    # Save to database
    db_character = Character(
        user_id=character_data.user_id,
        name=character_data.name,
        age=character_data.age,
        occupation=character_data.occupation,
        additional_info=character_data.additional_info,
        worldview=character_profile["worldview"],
        details=character_profile["details"],
        dynamic_profile=""
    )

    db.add(db_character)
    db.commit()
    db.refresh(db_character)

    return {
        "character_id": db_character.id,
        "name": db_character.name,
        "worldview": db_character.worldview,
        "details": db_character.details,
        "created_at": db_character.created_at
    }


@app.get("/characters/{character_id}")
async def get_character(
    character_id: int,
    db: Session = Depends(get_db_session)
):
    """Get character by ID"""
    character = db.query(Character).filter(Character.id == character_id).first()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return {
        "character_id": character.id,
        "name": character.name,
        "age": character.age,
        "occupation": character.occupation,
        "worldview": character.worldview,
        "details": character.details,
        "dynamic_profile": character.dynamic_profile,
        "created_at": character.created_at
    }


@app.get("/users/{user_id}/characters")
async def list_user_characters(
    user_id: str,
    db: Session = Depends(get_db_session)
):
    """List all characters for a user"""
    characters = db.query(Character).filter(Character.user_id == user_id).all()

    return {
        "user_id": user_id,
        "characters": [
            {
                "character_id": char.id,
                "name": char.name,
                "age": char.age,
                "occupation": char.occupation,
                "created_at": char.created_at
            }
            for char in characters
        ]
    }


# Chat endpoints
@app.post("/characters/{character_id}/chat")
async def chat_with_character(
    character_id: int,
    chat_request: ChatRequest,
    db: Session = Depends(get_db_session)
):
    """
    Chat with a character

    Process:
    1. Load character from database
    2. Load or create conversation session
    3. Get conversation history
    4. Process message through orchestrator
    5. Save message and updates to database
    6. Store memories in vector database
    7. Return response
    """
    # Load character
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Load or create conversation
    session_id = chat_request.session_id
    conversation = None

    if session_id:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()

    if not conversation:
        # Create new conversation
        import uuid
        session_id = str(uuid.uuid4())
        conversation = Conversation(
            character_id=character_id,
            session_id=session_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Load history
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.timestamp).all()

    history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    # Load quests
    quests = db.query(Quest).filter(Quest.character_id == character_id).all()
    regular_quests = {
        "quests": [
            {
                "id": f"quest_{q.id}",
                "title": q.title,
                "description": q.description,
                "cleared": q.cleared
            }
            for q in quests if q.quest_type == "regular"
        ]
    }
    advancement_quests = {
        "quests": [
            {
                "id": f"adv_{q.id}",
                "title": q.title,
                "description": q.description,
                "required_affection": q.required_affection,
                "cleared": q.cleared
            }
            for q in quests if q.quest_type == "advancement"
        ]
    }

    # Build character dict
    character_dict = {
        "basics": {
            "name": character.name,
            "age": character.age,
            "occupation": character.occupation
        },
        "worldview": character.worldview,
        "details": character.details,
        "dynamic_profile": character.dynamic_profile
    }

    # Process message through orchestrator
    result = orchestrator.process_message(
        user_message=chat_request.message,
        character=character_dict,
        history=history,
        regular_quests=regular_quests,
        advancement_quests=advancement_quests,
        current_affection=conversation.affection_score,
        relationship_stage=conversation.relationship_stage
    )

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_request.message
    )
    db.add(user_msg)

    # Save assistant message
    response = result["response"]
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response["dialogue"],
        dialogue=response["dialogue"],
        action=response.get("action", ""),
        situation=response.get("situation", ""),
        background=response.get("background", ""),
        internal_thought=response.get("internal_thought", ""),
        affection_change=response.get("affection_change", 0)
    )
    db.add(assistant_msg)

    # Update conversation state
    conversation.affection_score = result["updated_affection"]
    conversation.turn_count += 1
    conversation.last_interaction = datetime.utcnow()

    # Update character dynamic profile if changed
    if result.get("updated_dynamic_profile"):
        character.dynamic_profile = result["updated_dynamic_profile"]

    # Update quests if checked
    if result.get("updated_quests"):
        updated_regular = result["updated_quests"].get("regular_quests", {}).get("quests", [])
        updated_advancement = result["updated_quests"].get("advancement_quests", {}).get("quests", [])

        for updated_quest in updated_regular + updated_advancement:
            quest_id_str = updated_quest.get("id", "")
            if quest_id_str.startswith("quest_"):
                quest_id = int(quest_id_str.replace("quest_", ""))
            elif quest_id_str.startswith("adv_"):
                quest_id = int(quest_id_str.replace("adv_", ""))
            else:
                continue

            quest = db.query(Quest).filter(Quest.id == quest_id).first()
            if quest:
                quest.cleared = updated_quest.get("cleared", 0)
                if quest.cleared == 1 and not quest.cleared_at:
                    quest.cleared_at = datetime.utcnow()

    # Save memories to database and vector store
    memories = result.get("memories", {})
    for category, facts in memories.items():
        for fact in facts:
            memory = Memory(
                character_id=character_id,
                conversation_id=conversation.id,
                category=category,
                content=fact
            )
            db.add(memory)
            db.flush()  # Get the ID

            # Add to vector store
            vector_store.add_memory(
                character_id=character_id,
                memory_id=memory.id,
                content=fact,
                metadata={
                    "category": category,
                    "timestamp": str(memory.timestamp),
                    "conversation_id": conversation.id
                }
            )

    db.commit()

    return {
        "session_id": session_id,
        "dialogue": response["dialogue"],
        "action": response.get("action", ""),
        "situation": response.get("situation", ""),
        "background": response.get("background", ""),
        "internal_thought": response.get("internal_thought", ""),
        "affection_score": result["updated_affection"],
        "affection_change": response.get("affection_change", 0),
        "relationship_stage": conversation.relationship_stage,
        "turn_count": conversation.turn_count,
        "memories_extracted": sum(len(facts) for facts in memories.values())
    }


# Quest endpoints
@app.post("/characters/{character_id}/quests")
async def create_quest(
    character_id: int,
    quest_data: QuestCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new quest for a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    quest = Quest(
        character_id=character_id,
        quest_type=quest_data.quest_type,
        title=quest_data.title,
        description=quest_data.description,
        required_affection=quest_data.required_affection
    )

    db.add(quest)
    db.commit()
    db.refresh(quest)

    return {
        "quest_id": quest.id,
        "title": quest.title,
        "quest_type": quest.quest_type,
        "cleared": quest.cleared
    }


@app.get("/characters/{character_id}/quests")
async def list_quests(
    character_id: int,
    db: Session = Depends(get_db_session)
):
    """List all quests for a character"""
    quests = db.query(Quest).filter(Quest.character_id == character_id).all()

    return {
        "character_id": character_id,
        "regular_quests": [
            {
                "quest_id": q.id,
                "title": q.title,
                "description": q.description,
                "cleared": q.cleared,
                "cleared_at": q.cleared_at
            }
            for q in quests if q.quest_type == "regular"
        ],
        "advancement_quests": [
            {
                "quest_id": q.id,
                "title": q.title,
                "description": q.description,
                "required_affection": q.required_affection,
                "cleared": q.cleared,
                "cleared_at": q.cleared_at
            }
            for q in quests if q.quest_type == "advancement"
        ]
    }


# Memory endpoints
@app.get("/characters/{character_id}/memories")
async def search_memories(
    character_id: int,
    query: str,
    limit: int = 5,
    db: Session = Depends(get_db_session)
):
    """Search character memories semantically"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    memories = vector_store.search_memories(
        character_id=character_id,
        query=query,
        n_results=limit
    )

    return {
        "character_id": character_id,
        "query": query,
        "memories": memories
    }


# Conversation history
@app.get("/conversations/{session_id}")
async def get_conversation_history(
    session_id: str,
    db: Session = Depends(get_db_session)
):
    """Get conversation history for a session"""
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.timestamp).all()

    return {
        "session_id": session_id,
        "character_id": conversation.character_id,
        "affection_score": conversation.affection_score,
        "relationship_stage": conversation.relationship_stage,
        "turn_count": conversation.turn_count,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "dialogue": msg.dialogue,
                "action": msg.action,
                "situation": msg.situation,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]
    }


# Run server
if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host=host, port=port)
