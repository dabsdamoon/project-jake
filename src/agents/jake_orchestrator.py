"""
JAKE Orchestrator: LangGraph-based agent that coordinates all JAKE components
"""
from typing import Dict, Any, List, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

from src.agents.jake_creator import JAKECreator
from src.agents.jake_chatter import JAKEChatter
from src.agents.jake_checker import JAKEChecker
from src.agents.jake_dynamic_profiler import JAKEDynamicProfiler
from src.agents.jake_summarizer import JAKESummarizer


class ConversationState(TypedDict):
    """State for the conversation graph"""
    # Input
    user_message: str
    character: Dict[str, Any]
    history: List[Dict[str, str]]
    regular_quests: Dict[str, Any]
    advancement_quests: Dict[str, Any]
    current_affection: int
    relationship_stage: str
    turn_count: int

    # Output
    response: Dict[str, Any]
    updated_quests: Dict[str, Any]
    updated_dynamic_profile: str
    memories: Dict[str, List[str]]
    updated_affection: int


class JAKEOrchestrator:
    """
    LangGraph-based orchestrator that coordinates all JAKE components
    following the process defined in PLAN.md
    """

    def __init__(self):
        """Initialize all JAKE components"""
        self.creator = JAKECreator()
        self.chatter = JAKEChatter()
        self.checker = JAKEChecker()
        self.profiler = JAKEDynamicProfiler()
        self.summarizer = JAKESummarizer()

        # Build the conversation graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph conversation flow

        Process (from PLAN.md):
        1. Chat with JAKEChatter
        2. After chat, decide what to run based on turn count:
           - If turns < 3: run JAKESummarizer only
           - If turns < 10: run JAKEChecker and JAKESummarizer
           - If turns >= 10: run all (JAKEChecker, JAKEDynamicProfiler, JAKESummarizer)
        """
        # Create graph
        workflow = StateGraph(ConversationState)

        # Add nodes
        workflow.add_node("chat", self._chat_node)
        workflow.add_node("check_quests", self._check_quests_node)
        workflow.add_node("update_profile", self._update_profile_node)
        workflow.add_node("summarize", self._summarize_node)

        # Define the flow
        workflow.set_entry_point("chat")

        # After chat, route based on turn count
        workflow.add_conditional_edges(
            "chat",
            self._route_after_chat,
            {
                "summarize_only": "summarize",
                "check_and_summarize": "check_quests",
                "full_process": "check_quests"
            }
        )

        # Quest checking routes
        workflow.add_conditional_edges(
            "check_quests",
            self._route_after_quest_check,
            {
                "update_profile": "update_profile",
                "summarize": "summarize"
            }
        )

        # After profile update, go to summarize
        workflow.add_edge("update_profile", "summarize")

        # After summarize, end
        workflow.add_edge("summarize", END)

        return workflow.compile()

    def _chat_node(self, state: ConversationState) -> ConversationState:
        """Node: Generate chat response"""
        response = self.chatter.chat(
            query=state["user_message"],
            character=state["character"],
            history=state["history"],
            current_affection=state["current_affection"]
        )

        # Update affection
        new_affection = min(100, max(0, response.get("affection_score", state["current_affection"])))

        state["response"] = response
        state["updated_affection"] = new_affection
        return state

    def _check_quests_node(self, state: ConversationState) -> ConversationState:
        """Node: Check quest completion"""
        # Build updated history including the new exchange
        updated_history = state["history"] + [
            {"role": "user", "content": state["user_message"]},
            {"role": "assistant", "content": state["response"]["dialogue"]}
        ]

        quest_results = self.checker.check_quests(
            history=updated_history,
            regular_quests=state["regular_quests"],
            advancement_quests=state["advancement_quests"],
            current_affection=state["updated_affection"],
            relationship_stage=state["relationship_stage"]
        )

        state["updated_quests"] = quest_results
        return state

    def _update_profile_node(self, state: ConversationState) -> ConversationState:
        """Node: Update dynamic profile"""
        # Build updated history
        updated_history = state["history"] + [
            {"role": "user", "content": state["user_message"]},
            {"role": "assistant", "content": state["response"]["dialogue"]}
        ]

        quest_context = state.get("updated_quests")

        updated_profile = self.profiler.update_profile(
            character=state["character"],
            history=updated_history,
            quest_context=quest_context
        )

        state["updated_dynamic_profile"] = updated_profile
        return state

    def _summarize_node(self, state: ConversationState) -> ConversationState:
        """Node: Extract and summarize memories"""
        # Build updated history
        updated_history = state["history"] + [
            {"role": "user", "content": state["user_message"]},
            {"role": "assistant", "content": state["response"]["dialogue"]}
        ]

        memories = self.summarizer.get_memory(
            history=updated_history,
            character_name=state["character"]["basics"]["name"]
        )

        state["memories"] = memories
        return state

    def _route_after_chat(self, state: ConversationState) -> Literal["summarize_only", "check_and_summarize", "full_process"]:
        """
        Route based on turn count (from PLAN.md):
        - turns < 3: summarize only
        - turns < 10: check quests + summarize
        - turns >= 10: full process (check + profile + summarize)
        """
        turn_count = state["turn_count"]

        if turn_count < 3:
            return "summarize_only"
        elif turn_count < 10:
            return "check_and_summarize"
        else:
            return "full_process"

    def _route_after_quest_check(self, state: ConversationState) -> Literal["update_profile", "summarize"]:
        """Route after quest check based on turn count"""
        turn_count = state["turn_count"]

        if turn_count >= 10:
            return "update_profile"
        else:
            return "summarize"

    def process_message(
        self,
        user_message: str,
        character: Dict[str, Any],
        history: List[Dict[str, str]],
        regular_quests: Dict[str, Any] = None,
        advancement_quests: Dict[str, Any] = None,
        current_affection: int = 50,
        relationship_stage: str = "stranger"
    ) -> Dict[str, Any]:
        """
        Process a user message through the complete JAKE pipeline

        Args:
            user_message: User's input
            character: Complete character profile
            history: Conversation history
            regular_quests: Regular quest dictionary
            advancement_quests: Advancement quest dictionary
            current_affection: Current affection score
            relationship_stage: Current relationship stage

        Returns:
            Complete result with response, updated quests, profile, and memories
        """
        # Calculate turn count
        turn_count = len(history) // 2

        # Prepare initial state
        initial_state: ConversationState = {
            "user_message": user_message,
            "character": character,
            "history": history,
            "regular_quests": regular_quests or {"quests": []},
            "advancement_quests": advancement_quests or {"quests": []},
            "current_affection": current_affection,
            "relationship_stage": relationship_stage,
            "turn_count": turn_count,
            "response": {},
            "updated_quests": {},
            "updated_dynamic_profile": "",
            "memories": {},
            "updated_affection": current_affection
        }

        # Run the graph
        result = self.graph.invoke(initial_state)

        return {
            "response": result["response"],
            "updated_affection": result["updated_affection"],
            "updated_quests": result.get("updated_quests"),
            "updated_dynamic_profile": result.get("updated_dynamic_profile"),
            "memories": result.get("memories", {})
        }

    def create_character(self, character_basics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new character using JAKECreator

        Args:
            character_basics: Basic character information

        Returns:
            Complete character profile
        """
        return self.creator.create_character(character_basics)


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    orchestrator = JAKEOrchestrator()

    # Create a character
    print("=== Creating Character ===")
    character = orchestrator.create_character({
        "name": "Luna",
        "age": "25",
        "occupation": "Cafe owner",
        "additional_info": "Loves books and cozy atmospheres"
    })
    print(f"Created: {character['basics']['name']}")

    # Simulate a conversation
    print("\n=== Starting Conversation ===")
    history = []

    # Turn 1
    result1 = orchestrator.process_message(
        user_message="Hello! This cafe looks really cozy.",
        character=character,
        history=history,
        current_affection=50
    )

    print(f"\nLuna: {result1['response']['dialogue']}")
    print(f"Action: {result1['response']['action']}")
    print(f"Affection: {result1['updated_affection']}")
    print(f"Memories extracted: {len(sum(result1['memories'].values(), []))} facts")
