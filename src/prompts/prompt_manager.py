"""
Centralized prompt management for JAKE system

This module provides a unified interface for accessing all prompts used
throughout the JAKE system. Prompts are organized by component.
"""
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class PromptManager:
    """
    Central manager for all JAKE prompts

    Usage:
        from src.prompts import PromptManager

        pm = PromptManager()
        prompt = pm.get_chat_prompt()
        chain = prompt | llm | parser
    """

    def __init__(self):
        """Initialize prompt manager"""
        pass

    # ============================================
    # JAKECreator Prompts
    # ============================================

    @staticmethod
    def get_worldview_prompt() -> ChatPromptTemplate:
        """Get prompt for worldview generation"""
        from .creator_prompts import WORLDVIEW_SYSTEM, WORLDVIEW_USER
        return ChatPromptTemplate.from_messages([
            ("system", WORLDVIEW_SYSTEM),
            ("user", WORLDVIEW_USER)
        ])

    @staticmethod
    def get_details_prompt() -> ChatPromptTemplate:
        """Get prompt for character details generation"""
        from .creator_prompts import DETAILS_SYSTEM, DETAILS_USER
        return ChatPromptTemplate.from_messages([
            ("system", DETAILS_SYSTEM),
            ("user", DETAILS_USER)
        ])

    # ============================================
    # JAKEChatter Prompts
    # ============================================

    @staticmethod
    def get_chat_prompt() -> ChatPromptTemplate:
        """Get prompt for chat generation"""
        from .chatter_prompts import CHAT_SYSTEM, CHAT_USER
        return ChatPromptTemplate.from_messages([
            ("system", CHAT_SYSTEM),
            MessagesPlaceholder(variable_name="history", optional=True),
            ("user", CHAT_USER)
        ])

    # ============================================
    # JAKEChecker Prompts
    # ============================================

    @staticmethod
    def get_quest_check_prompt() -> ChatPromptTemplate:
        """Get prompt for quest checking"""
        from .checker_prompts import QUEST_CHECK_SYSTEM, QUEST_CHECK_USER
        return ChatPromptTemplate.from_messages([
            ("system", QUEST_CHECK_SYSTEM),
            ("user", QUEST_CHECK_USER)
        ])

    @staticmethod
    def get_advancement_check_prompt() -> ChatPromptTemplate:
        """Get prompt for advancement quest checking"""
        from .checker_prompts import ADVANCEMENT_CHECK_SYSTEM, ADVANCEMENT_CHECK_USER
        return ChatPromptTemplate.from_messages([
            ("system", ADVANCEMENT_CHECK_SYSTEM),
            ("user", ADVANCEMENT_CHECK_USER)
        ])

    # ============================================
    # JAKEDynamicProfiler Prompts
    # ============================================

    @staticmethod
    def get_dynamic_profile_prompt() -> ChatPromptTemplate:
        """Get prompt for dynamic profile generation"""
        from .profiler_prompts import DYNAMIC_PROFILE_SYSTEM, DYNAMIC_PROFILE_USER
        return ChatPromptTemplate.from_messages([
            ("system", DYNAMIC_PROFILE_SYSTEM),
            ("user", DYNAMIC_PROFILE_USER)
        ])

    # ============================================
    # JAKESummarizer Prompts
    # ============================================

    @staticmethod
    def get_memory_extraction_prompt() -> ChatPromptTemplate:
        """Get prompt for memory extraction"""
        from .summarizer_prompts import MEMORY_SYSTEM, MEMORY_USER
        return ChatPromptTemplate.from_messages([
            ("system", MEMORY_SYSTEM),
            ("user", MEMORY_USER)
        ])
