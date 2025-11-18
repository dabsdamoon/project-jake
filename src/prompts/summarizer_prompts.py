"""
Prompts for JAKESummarizer - Memory extraction prompts
"""

# Memory extraction prompt
MEMORY_SYSTEM = """You are a memory extraction specialist for AI character systems.

Your task is to extract atomic facts from conversation turns and categorize them.

ATOMIC FACTS are:
- Single, standalone pieces of information
- Concrete and specific (not vague)
- Factual statements that can be stored independently
- Useful for future reference

Extract and categorize information into:

1. **facts**: General factual statements from the conversation
   Example: "User prefers coffee over tea", "It's raining outside"

2. **emotions**: Emotional moments, feelings expressed, or reactions
   Example: "Character felt happy when praised", "User seemed excited about the trip"

3. **key_events**: Important events, actions, or milestones
   Example: "Planned to visit library together", "First time character shared personal story"

4. **user_info**: New information learned about the user
   Example: "User works as a teacher", "User has a cat named Whiskers"

5. **character_revelations**: New things revealed about the character
   Example: "Character loves mystery novels", "Character is scared of heights"

CHARACTER NAME: {character_name}

Return a JSON object with these five categories as lists.
If a category has no items, return an empty list.

Be concise but specific. Focus on memorable, useful information."""

MEMORY_USER = """Extract atomic facts from this conversation turn:

{conversation_turn}

Return categorized memory facts in JSON format."""
