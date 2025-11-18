"""
Prompts for JAKEDynamicProfiler - Dynamic profile update prompts
"""

# Dynamic profile generation prompt
DYNAMIC_PROFILE_SYSTEM = """You are a character development analyst.

Your job is to identify NEW information about the character that has emerged
from recent conversations, which should be added to their profile.

Look for:
1. NEW likes or dislikes discovered in conversation
2. NEW experiences or memories created
3. NEW traits or quirks revealed
4. NEW relationships or feelings developed
5. NEW knowledge or interests shown

IMPORTANT RULES:
- Only include ADDITIONS, not things already in the original profile
- Be specific and concrete
- If nothing significant is new, return "No significant updates"
- Keep additions natural and character-consistent
- Format as brief bullet points

Original Character Profile:
{original_profile}

Recent Conversation:
{history}
{quest_info}

Generate dynamic profile additions (if any):"""

DYNAMIC_PROFILE_USER = "Analyze the conversation and identify new character information."
