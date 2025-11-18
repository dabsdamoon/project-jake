"""
JAKEChatter: Agent for running character chats with dialogue, actions, and affection scoring
"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from src.prompts import PromptManager


class ChatResponse(BaseModel):
    """Schema for chat response"""
    dialogue: str = Field(description="Character's spoken dialogue")
    action: str = Field(description="Character's physical actions or expressions")
    situation: str = Field(description="Current situation description")
    background: str = Field(description="Background/scene description")
    affection_score: int = Field(description="Current affection level (0-100)")
    affection_change: int = Field(description="Change in affection from last turn (-10 to +10)")
    internal_thought: str = Field(description="Character's internal thoughts (not spoken)")


class JAKEChatter:
    """
    Agent for running character chats with rich outputs including dialogue,
    actions, situation descriptions, and affection tracking
    """

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.8):
        """
        Initialize JAKEChatter

        Args:
            model_name: OpenAI model to use
            temperature: Temperature for generation (higher = more varied responses)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.prompt_manager = PromptManager()

    def _build_character_context(
        self,
        character_basics: Dict[str, Any],
        character_details: Dict[str, str],
        dynamic_profile: str = ""
    ) -> str:
        """Build comprehensive character context for the prompt"""
        context = f"""
CHARACTER PROFILE:
Name: {character_basics.get('name', 'Unknown')}
Age: {character_basics.get('age', 'Unknown')}
Occupation: {character_basics.get('occupation', 'Unknown')}

PERSONALITY & TRAITS:
{character_details.get('personality', 'Not specified')}

DISTINCTIVE CHARACTERISTICS:
{character_details.get('character', 'Not specified')}

SPEAKING STYLE:
{character_details.get('speaking_style', 'Not specified')}

LIKES: {character_details.get('likes', 'Not specified')}
DISLIKES: {character_details.get('dislikes', 'Not specified')}

BACKGROUND:
{character_details.get('background', 'Not specified')}

GOALS & MOTIVATIONS:
{character_details.get('goals', 'Not specified')}
"""
        if dynamic_profile:
            context += f"\n\nDYNAMIC UPDATES (from recent interactions):\n{dynamic_profile}"

        return context

    def _chat(
        self,
        query: str,
        character_basics: Dict[str, Any],
        character_details: Dict[str, str],
        history: Optional[List[Dict[str, str]]] = None,
        dynamic_profile: str = "",
        current_affection: int = 50
    ) -> Dict[str, Any]:
        """
        Generate chat response with all required outputs

        Args:
            query: User input text
            character_basics: Basic character fields
            character_details: Character details from JAKECreator
            history: Conversation history
            dynamic_profile: Dynamic profile updates
            current_affection: Current affection score

        Returns:
            Dictionary with dialogue, action, situation, background, affection_score
        """
        character_context = self._build_character_context(
            character_basics,
            character_details,
            dynamic_profile
        )

        chat_prompt = self.prompt_manager.get_chat_prompt()

        # Prepare history in the correct format
        formatted_history = []
        if history:
            for turn in history:
                role = turn.get("role")
                content = turn.get("content")
                if role and content:
                    formatted_history.append((role, content))

        chain = chat_prompt | self.llm | JsonOutputParser()

        response = chain.invoke({
            "character_context": character_context,
            "current_affection": current_affection,
            "history": formatted_history if formatted_history else None,
            "query": query
        })

        return response

    def chat(
        self,
        query: str,
        character: Dict[str, Any],
        history: Optional[List[Dict[str, str]]] = None,
        current_affection: int = 50
    ) -> Dict[str, Any]:
        """
        Simplified chat interface

        Args:
            query: User input
            character: Complete character profile
            history: Conversation history
            current_affection: Current affection score

        Returns:
            Chat response dictionary
        """
        return self._chat(
            query=query,
            character_basics=character.get("basics", {}),
            character_details=character.get("details", {}),
            history=history,
            dynamic_profile=character.get("dynamic_profile", ""),
            current_affection=current_affection
        )


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    chatter = JAKEChatter()

    # Example character
    character = {
        "basics": {
            "name": "Luna",
            "age": "25",
            "occupation": "Cafe owner"
        },
        "details": {
            "personality": "Warm, caring, slightly shy but friendly once comfortable",
            "character": "Often hums while working, has a habit of tucking hair behind ear when nervous",
            "speaking_style": "Gentle and soft-spoken, uses polite language, occasionally hesitant",
            "likes": "Books, rainy days, warm tea, cozy atmospheres",
            "dislikes": "Loud noises, confrontation, rushed situations",
            "background": "Inherited the cafe from grandmother, finds comfort in serving others",
            "goals": "Create a space where people feel at home and welcome"
        },
        "dynamic_profile": ""
    }

    # First interaction
    response = chatter.chat(
        query="Hello! This cafe looks really cozy.",
        character=character,
        current_affection=50
    )

    print("=== Chat Response ===")
    print(f"Dialogue: {response['dialogue']}")
    print(f"Action: {response['action']}")
    print(f"Situation: {response['situation']}")
    print(f"Affection: {response['affection_score']} ({response['affection_change']:+d})")
    print(f"Internal Thought: {response['internal_thought']}")
