"""
JAKEDynamicProfiler: Updates character details based on conversation progress
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from src.prompts import PromptManager


class JAKEDynamicProfiler:
    """
    Worker that generates updated character details using information
    accumulated as conversations progress.

    Example:
    - Original likes: flowers, chocolate, bookstores
    - During conversation: goes to amusement park
    - Updated likes: flowers, chocolate, bookstores, amusement parks
    """

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.3):
        """
        Initialize JAKEDynamicProfiler

        Args:
            model_name: OpenAI model to use
            temperature: Temperature (moderate for consistent but adaptive updates)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.prompt_manager = PromptManager()

    def _format_history(self, history: List[Dict[str, str]], num_turns: int = 3) -> str:
        """Format recent conversation history"""
        formatted = []
        recent_history = history[-(num_turns * 2):]  # Last N turns (2 messages per turn)

        for turn in recent_history:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            formatted.append(f"{role.upper()}: {content}")

        return "\n".join(formatted)

    def _dynamic_profile(
        self,
        history: List[Dict[str, str]],
        character_details: Dict[str, str],
        quest_context: Dict[str, Any] = None
    ) -> str:
        """
        Generate dynamic profile additions based on conversation history

        Args:
            history: Conversation history (recent turns)
            character_details: Original character details
            quest_context: Optional quest information for context

        Returns:
            dynamic_profile: String with new information to add to character profile
        """
        formatted_history = self._format_history(history, num_turns=3)

        quest_info = ""
        if quest_context:
            quest_info = f"\n\nRecent Quest Activity:\n{quest_context}"

        profile_prompt = self.prompt_manager.get_dynamic_profile_prompt()

        # Format original profile
        original_profile_text = "\n".join([
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in character_details.items()
        ])

        chain = profile_prompt | self.llm | StrOutputParser()

        dynamic_profile = chain.invoke({
            "original_profile": original_profile_text,
            "history": formatted_history,
            "quest_info": quest_info
        })

        # Return empty string if no updates
        if "no significant updates" in dynamic_profile.lower():
            return ""

        return dynamic_profile.strip()

    def update_profile(
        self,
        character: Dict[str, Any],
        history: List[Dict[str, str]],
        quest_context: Dict[str, Any] = None
    ) -> str:
        """
        Simplified interface to update character profile

        Args:
            character: Complete character dictionary
            history: Conversation history
            quest_context: Optional quest information

        Returns:
            Updated dynamic profile string
        """
        character_details = character.get("details", {})
        existing_dynamic = character.get("dynamic_profile", "")

        new_additions = self._dynamic_profile(
            history,
            character_details,
            quest_context
        )

        if not new_additions:
            return existing_dynamic

        # Combine existing and new
        if existing_dynamic:
            updated_profile = f"{existing_dynamic}\n\n=== Recent Updates ===\n{new_additions}"
        else:
            updated_profile = new_additions

        return updated_profile

    def should_update(self, history_length: int) -> bool:
        """
        Determine if profile should be updated based on conversation length

        According to PLAN.md:
        - Don't run if history < 3 turns
        - Run if history >= 10 turns

        Args:
            history_length: Number of conversation turns (messages / 2)

        Returns:
            True if profile should be updated
        """
        return history_length >= 10


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    profiler = JAKEDynamicProfiler()

    # Example character
    character = {
        "details": {
            "personality": "Warm, caring, slightly shy",
            "likes": "Books, rainy days, warm tea",
            "dislikes": "Loud noises, confrontation"
        },
        "dynamic_profile": ""
    }

    # Example conversation showing new interests
    history = [
        {"role": "user", "content": "Have you ever been to an amusement park?"},
        {"role": "assistant", "content": "Actually, I haven't! I've always been a bit nervous about rides."},
        {"role": "user", "content": "What if we went together? I'd hold your hand on the scary rides."},
        {"role": "assistant", "content": "*blushes* That... that actually sounds really nice. Maybe I'd like it with you there."},
        {"role": "user", "content": "Great! Let's plan it for this weekend."},
        {"role": "assistant", "content": "I'm excited! I've heard the ferris wheel has an amazing view."}
    ]

    updated_profile = profiler.update_profile(
        character=character,
        history=history
    )

    print("=== Dynamic Profile Update ===")
    print(updated_profile)
