"""
Test script for JAKE system
Run this to test the basic functionality
"""
import asyncio
from dotenv import load_dotenv

load_dotenv()


async def test_character_creation():
    """Test creating a character"""
    print("\n=== Testing Character Creation ===")

    from src.agents.jake_creator import JAKECreator

    creator = JAKECreator()

    character_basics = {
        "name": "Luna",
        "age": "25",
        "occupation": "Cafe owner",
        "additional_info": "Loves books, coffee, and cozy rainy days"
    }

    print(f"Creating character: {character_basics['name']}...")
    character = creator.create_character(character_basics)

    print(f"\n✓ Character created successfully!")
    print(f"Name: {character['basics']['name']}")
    print(f"\nWorldview (excerpt):\n{character['worldview'][:200]}...")
    print(f"\nPersonality: {character['details'].get('personality', 'N/A')[:100]}...")

    return character


async def test_conversation(character):
    """Test a conversation"""
    print("\n\n=== Testing Conversation ===")

    from src.agents.jake_chatter import JAKEChatter

    chatter = JAKEChatter()

    messages = [
        "Hello! This cafe looks really cozy.",
        "What's your favorite book?",
        "That sounds interesting! Would you recommend it?"
    ]

    history = []
    current_affection = 50

    for i, msg in enumerate(messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"You: {msg}")

        response = chatter.chat(
            query=msg,
            character=character,
            history=history,
            current_affection=current_affection
        )

        print(f"\nLuna: {response['dialogue']}")
        print(f"Action: {response['action']}")
        print(f"Affection: {response['affection_score']} ({response['affection_change']:+d})")

        # Update history
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": response['dialogue']})
        current_affection = response['affection_score']

    print("\n✓ Conversation test completed!")
    return history


async def test_quest_checking(history):
    """Test quest checking"""
    print("\n\n=== Testing Quest Checker ===")

    from src.agents.jake_checker import JAKEChecker

    checker = JAKEChecker()

    # Define some test quests
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
                "title": "Show Interest",
                "description": "Ask for a book recommendation",
                "cleared": 0
            }
        ]
    }

    advancement_quests = {
        "quests": [
            {
                "id": "adv_001",
                "title": "First Connection",
                "description": "Have a meaningful conversation about shared interests",
                "required_affection": 55,
                "cleared": 0
            }
        ]
    }

    result = checker.check_quests(
        history=history,
        regular_quests=regular_quests,
        advancement_quests=advancement_quests,
        current_affection=60,
        relationship_stage="acquaintance"
    )

    print("\nRegular Quests:")
    for quest in result['regular_quests']['quests']:
        status = "✓ Cleared" if quest['cleared'] == 1 else "○ Not cleared"
        print(f"  {status} - {quest['title']}")

    print("\nAdvancement Quests:")
    for quest in result['advancement_quests']['quests']:
        status = "✓ Cleared" if quest['cleared'] == 1 else "○ Not cleared"
        print(f"  {status} - {quest['title']}")

    print("\n✓ Quest checking completed!")


async def test_memory_extraction(history, character):
    """Test memory extraction"""
    print("\n\n=== Testing Memory Extraction ===")

    from src.agents.jake_summarizer import JAKESummarizer

    summarizer = JAKESummarizer()

    memories = summarizer.get_memory(
        history=history,
        character_name=character['basics']['name']
    )

    print("\nExtracted Memories:")
    for category, facts in memories.items():
        if facts:
            print(f"\n  {category.replace('_', ' ').title()}:")
            for fact in facts:
                print(f"    - {fact}")

    total_facts = sum(len(facts) for facts in memories.values())
    print(f"\n✓ Extracted {total_facts} memory facts!")


async def test_orchestrator():
    """Test the full orchestrator"""
    print("\n\n=== Testing LangGraph Orchestrator ===")

    from src.agents.jake_orchestrator import JAKEOrchestrator

    orchestrator = JAKEOrchestrator()

    # Create character
    print("\n1. Creating character...")
    character = orchestrator.create_character({
        "name": "Elena",
        "age": "28",
        "occupation": "Librarian",
        "additional_info": "Passionate about literature and history"
    })
    print(f"   ✓ Created: {character['basics']['name']}")

    # Process messages
    history = []

    messages = [
        "Hi! I'm looking for a good mystery novel.",
        "What got you interested in working at a library?"
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n2.{i}. Processing message...")
        result = orchestrator.process_message(
            user_message=msg,
            character=character,
            history=history,
            current_affection=50
        )

        print(f"   You: {msg}")
        print(f"   Elena: {result['response']['dialogue'][:100]}...")
        print(f"   Affection: {result['updated_affection']}")
        print(f"   Memories extracted: {sum(len(v) for v in result['memories'].values())}")

        # Update history
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": result['response']['dialogue']})

    print("\n✓ Orchestrator test completed!")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("JAKE System Test Suite")
    print("=" * 60)

    try:
        # Test 1: Character Creation
        character = await test_character_creation()

        # Test 2: Conversation
        history = await test_conversation(character)

        # Test 3: Quest Checking
        await test_quest_checking(history)

        # Test 4: Memory Extraction
        await test_memory_extraction(history, character)

        # Test 5: Full Orchestrator
        await test_orchestrator()

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
