"""
JAKESummarizer: Extracts atomic facts from conversations for memory storage
"""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from src.prompts import PromptManager


class MemoryFacts(BaseModel):
    """Schema for extracted memory facts"""
    facts: List[str] = Field(description="List of atomic facts from the conversation")
    emotions: List[str] = Field(description="Emotional moments or reactions")
    key_events: List[str] = Field(description="Important events or milestones")
    user_info: List[str] = Field(description="Information learned about the user")
    character_revelations: List[str] = Field(description="New things revealed about the character")


class JAKESummarizer:
    """
    Worker that extracts atomic facts from conversations between
    the character and the user for long-term memory storage
    """

    def __init__(self, model_name: str = "gpt-5-nano", temperature: float = 0.0):
        """
        Initialize JAKESummarizer

        Args:
            model_name: OpenAI model to use (using nano for cost efficiency)
            temperature: Temperature (0 for consistent extraction)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.prompt_manager = PromptManager()

    def _extract_facts(self, turn: Dict[str, str]) -> str:
        """Format a single conversation turn"""
        user_msg = turn.get("user", "")
        assistant_msg = turn.get("assistant", "")

        return f"USER: {user_msg}\nCHARACTER: {assistant_msg}"

    def get_memory(
        self,
        history: List[Dict[str, str]],
        character_name: str = "Character"
    ) -> Dict[str, List[str]]:
        """
        Extract atomic facts and memories from conversation history

        Args:
            history: Conversation history (1 turn = user + assistant messages)
            character_name: Name of the character for context

        Returns:
            Dictionary with categorized memory facts
        """
        # Get the last turn (2 messages)
        if len(history) < 2:
            return {
                "facts": [],
                "emotions": [],
                "key_events": [],
                "user_info": [],
                "character_revelations": []
            }

        # Extract last user-assistant pair
        last_turn = {
            "user": history[-2].get("content", "") if len(history) >= 2 else "",
            "assistant": history[-1].get("content", "")
        }

        formatted_turn = self._extract_facts(last_turn)

        memory_prompt = self.prompt_manager.get_memory_extraction_prompt()
        chain = memory_prompt | self.llm | JsonOutputParser()

        memories = chain.invoke({
            "character_name": character_name,
            "conversation_turn": formatted_turn
        })

        return memories

    def should_run(self, history_length: int) -> bool:
        """
        Determine if summarizer should run

        According to PLAN.md:
        - Always run after each turn for memory storage

        Args:
            history_length: Number of messages in history

        Returns:
            True if should run (always, for every turn)
        """
        return history_length >= 2  # At least one complete turn


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    summarizer = JAKESummarizer()

    # Example conversation turn
    history = [
        {
            "role": "user",
            "content": "I had a really tough day at work. My boss was being unreasonable again."
        },
        {
            "role": "assistant",
            "content": "*looks at you with concern* I'm so sorry to hear that. Come, sit down. Let me make you some chamomile tea - it always helps me when I'm stressed. *gently guides you to a cozy corner* You know, this cafe is meant to be a safe space. You can tell me about it if you'd like."
        }
    ]

    memories = summarizer.get_memory(
        history=history,
        character_name="Luna"
    )

    print("=== Extracted Memories ===")
    print(f"\nFacts: {memories.get('facts', [])}")
    print(f"\nEmotions: {memories.get('emotions', [])}")
    print(f"\nKey Events: {memories.get('key_events', [])}")
    print(f"\nUser Info: {memories.get('user_info', [])}")
    print(f"\nCharacter Revelations: {memories.get('character_revelations', [])}")
