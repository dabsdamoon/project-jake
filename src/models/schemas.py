"""
Database schemas for JAKE system
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Character(Base):
    """Character table - stores JAKE character data"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Owner of this character
    name = Column(String, nullable=False)
    age = Column(String)
    occupation = Column(String)
    additional_info = Column(Text)

    # Generated details
    worldview = Column(Text)
    details = Column(JSON)  # Stores personality, likes, dislikes, etc.
    dynamic_profile = Column(Text, default="")

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="character")
    quests = relationship("Quest", back_populates="character")


class Conversation(Base):
    """Conversation table - stores chat sessions"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    session_id = Column(String, unique=True, index=True)

    # Conversation state
    affection_score = Column(Integer, default=50)
    relationship_stage = Column(String, default="stranger")
    turn_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    character = relationship("Character", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """Message table - stores individual messages"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)

    # For assistant messages, store rich output
    dialogue = Column(Text)
    action = Column(Text)
    situation = Column(Text)
    background = Column(Text)
    internal_thought = Column(Text)
    affection_change = Column(Integer, default=0)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Quest(Base):
    """Quest table - stores quest data"""
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))

    quest_type = Column(String)  # 'regular' or 'advancement'
    title = Column(String)
    description = Column(Text)
    required_affection = Column(Integer, default=0)
    cleared = Column(Integer, default=0)  # 0 = not cleared, 1 = cleared

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    cleared_at = Column(DateTime, nullable=True)

    # Relationships
    character = relationship("Character", back_populates="quests")


class Memory(Base):
    """Memory table - stores extracted facts from conversations"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    category = Column(String)  # 'fact', 'emotion', 'key_event', 'user_info', 'character_revelation'
    content = Column(Text)
    embedding = Column(JSON)  # Will store vector embedding for semantic search

    timestamp = Column(DateTime, default=datetime.utcnow)
