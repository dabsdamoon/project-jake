"""
JAKEChatter: Agent for running character chats with dialogue, actions, and affection scoring
"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
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

    def __init__(self, model_name: str = "gpt-5-nano", temperature: float = 0.8):
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
        template = self.prompt_manager.get_character_context_template()
        context = template.format(
            name=character_basics.get('name', 'Unknown'),
            age=character_basics.get('age', 'Unknown'),
            occupation=character_basics.get('occupation', 'Unknown'),
            personality=character_details.get('personality', 'Not specified'),
            quirks=character_details.get('quirks', 'Not specified'),
            speaking_style=character_details.get('speaking_style', 'Not specified'),
            likes=character_details.get('likes', 'Not specified'),
            dislikes=character_details.get('dislikes', 'Not specified'),
            background=character_details.get('background', 'Not specified'),
            goals=character_details.get('goals', 'Not specified')
        )

        if dynamic_profile:
            dynamic_suffix = self.prompt_manager.get_character_context_dynamic_suffix()
            context += dynamic_suffix.format(dynamic_profile=dynamic_profile)

        return context

    def _chat(
        self,
        query: str,
        character_basics: Dict[str, Any],
        character_details: Dict[str, str],
        history: Optional[List[Dict[str, str]]] = None,
        dynamic_profile: str = "",
        current_affection: int = 50
    ) -> ChatResponse:
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
            ChatResponse object with validated dialogue, action, situation, background,
            affection_score, affection_change, and internal_thought
        """
        character_context = self._build_character_context(
            character_basics,
            character_details,
            dynamic_profile
        )

        chat_prompt = self.prompt_manager.get_chat_prompt()

        # Prepare history in the correct format (LangChain message objects)
        formatted_history = []
        if history:
            for turn in history:
                role = turn.get("role")
                content = turn.get("content")
                if role and content:
                    if role == "user":
                        formatted_history.append(HumanMessage(content=content))
                    elif role == "assistant":
                        formatted_history.append(AIMessage(content=content))

        chain = chat_prompt | self.llm.with_structured_output(ChatResponse)

        response = chain.invoke({
            "character_context": character_context,
            "current_affection": current_affection,
            "history": formatted_history,  # List of LangChain message objects
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
        response = self._chat(
            query=query,
            character_basics=character.get("basics", {}),
            character_details=character.get("details", {}),
            history=history,
            dynamic_profile=character.get("dynamic_profile", ""),
            current_affection=current_affection
        )
        return response.model_dump()  # Convert Pydantic model to dict


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
            "quirks": "Often hums while working, has a habit of tucking hair behind ear when nervous",
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
