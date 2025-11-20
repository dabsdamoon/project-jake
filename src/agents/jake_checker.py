"""
JAKEChecker: Agent that checks quest completion status from conversation history
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from src.prompts import PromptManager


class JAKEChecker:
    """
    Agent that analyzes conversation history and determines whether
    quests have been cleared
    """

    def __init__(self, model_name: str = "gpt-5-nano", temperature: float = 0.0):
        """
        Initialize JAKEChecker

        Args:
            model_name: OpenAI model to use
            temperature: Temperature (should be low for consistency)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.prompt_manager = PromptManager()

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history into readable text"""
        formatted = []
        for i, turn in enumerate(history[-6:], 1):  # Last 3 turns (6 messages)
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        return "\n".join(formatted)

    def _check_quest(
        self,
        history: List[Dict[str, str]],
        dict_quest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check whether each quest has been cleared

        Args:
            history: 3 turns of conversation history (last 6 messages)
            dict_quest: Quest list in nested dictionary (JSON) format

        Returns:
            dict_quest: Same structure with quest clear status filled in as binary values
        """
        formatted_history = self._format_history(history)

        quest_prompt = self.prompt_manager.get_quest_check_prompt()
        chain = quest_prompt | self.llm | JsonOutputParser()

        updated_quests = chain.invoke({
            "history": formatted_history,
            "quest_json": dict_quest
        })

        return updated_quests

    def _check_advancement_quest(
        self,
        history: List[Dict[str, str]],
        dict_quest: Dict[str, Any],
        current_affection: int = 50,
        relationship_stage: str = "stranger"
    ) -> Dict[str, Any]:
        """
        Check advancement quests with relationship progression logic

        Args:
            history: 3 turns of conversation history
            dict_quest: Quest list in nested dictionary format
            current_affection: Current affection score
            relationship_stage: Current relationship stage

        Returns:
            dict_quest: Same structure with advancement quest status updated
        """
        formatted_history = self._format_history(history)

        advancement_prompt = self.prompt_manager.get_advancement_check_prompt()
        chain = advancement_prompt | self.llm | JsonOutputParser()

        updated_quests = chain.invoke({
            "history": formatted_history,
            "quest_json": dict_quest,
            "affection": current_affection,
            "stage": relationship_stage
        })

        return updated_quests

    def check_quests(
        self,
        history: List[Dict[str, str]],
        regular_quests: Dict[str, Any],
        advancement_quests: Dict[str, Any],
        current_affection: int = 50,
        relationship_stage: str = "stranger"
    ) -> Dict[str, Any]:
        """
        Check both regular and advancement quests

        Args:
            history: Conversation history
            regular_quests: Regular quest dictionary
            advancement_quests: Advancement quest dictionary
            current_affection: Current affection score
            relationship_stage: Current relationship stage

        Returns:
            Dictionary with updated regular_quests and advancement_quests
        """
        updated_regular = self._check_quest(history, regular_quests)
        updated_advancement = self._check_advancement_quest(
            history,
            advancement_quests,
            current_affection,
            relationship_stage
        )

        return {
            "regular_quests": updated_regular,
            "advancement_quests": updated_advancement
        }


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    checker = JAKEChecker()

    # Example conversation history
    history = [
        {"role": "user", "content": "What's your favorite book?"},
        {"role": "assistant", "content": "I love 'The Night Circus'! It's so magical and atmospheric."},
        {"role": "user", "content": "That's one of my favorites too! What do you like about it?"},
        {"role": "assistant", "content": "The way it blends romance with mystery... it reminds me of my cafe somehow."},
        {"role": "user", "content": "Would you like to visit a library together sometime?"},
        {"role": "assistant", "content": "I'd love that! There's a wonderful old library downtown."}
    ]

    # Example quest structure
    regular_quests = {
        "quests": [
            {
                "id": "quest_001",
                "title": "Getting to Know Each Other",
                "description": "Ask about Luna's favorite book",
                "cleared": 0
            },
            {
                "id": "quest_002",
                "title": "Shared Interests",
                "description": "Find a common interest",
                "cleared": 0
            }
        ]
    }

    advancement_quests = {
        "quests": [
            {
                "id": "adv_001",
                "title": "First Outing",
                "description": "Suggest going somewhere together",
                "required_affection": 60,
                "cleared": 0
            }
        ]
    }

    result = checker.check_quests(
        history=history,
        regular_quests=regular_quests,
        advancement_quests=advancement_quests,
        current_affection=65,
        relationship_stage="friend"
    )

    print("=== Quest Check Results ===")
    print("Regular Quests:", result["regular_quests"])
    print("\nAdvancement Quests:", result["advancement_quests"])
