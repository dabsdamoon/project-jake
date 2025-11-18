# Prompt Management System

All prompts in the JAKE system are now centrally managed for easy maintenance and version control.

## Structure

```
src/prompts/
├── __init__.py
├── prompt_manager.py          # Central prompt manager
├── creator_prompts.py         # JAKECreator prompts
├── chatter_prompts.py         # JAKEChatter prompts
├── checker_prompts.py         # JAKEChecker prompts
├── profiler_prompts.py        # JAKEDynamicProfiler prompts
└── summarizer_prompts.py      # JAKESummarizer prompts
```

## Usage

### In Agent Classes

```python
from src.prompts import PromptManager

class MyAgent:
    def __init__(self):
        self.llm = ChatOpenAI(...)
        self.prompt_manager = PromptManager()

    def some_method(self):
        # Get prompt from manager
        prompt = self.prompt_manager.get_chat_prompt()

        # Use with LangChain
        chain = prompt | self.llm | parser
        result = chain.invoke(params)
```

### Available Prompts

#### JAKECreator
- `get_worldview_prompt()` - Generate character worldview
- `get_details_prompt()` - Generate character details

#### JAKEChatter
- `get_chat_prompt()` - Generate conversational responses

#### JAKEChecker
- `get_quest_check_prompt()` - Check regular quest completion
- `get_advancement_check_prompt()` - Check advancement quest completion

#### JAKEDynamicProfiler
- `get_dynamic_profile_prompt()` - Generate profile updates

#### JAKESummarizer
- `get_memory_extraction_prompt()` - Extract atomic facts

## Benefits

1. **Centralized Management**: All prompts in one location
2. **Version Control**: Easy to track prompt changes
3. **Reusability**: Prompts can be shared across components
4. **Testing**: Individual prompts can be tested independently
5. **Maintenance**: Update prompts without modifying agent code

## Modifying Prompts

To update a prompt:

1. Navigate to the appropriate prompt file (e.g., `chatter_prompts.py`)
2. Edit the prompt constant (e.g., `CHAT_SYSTEM`)
3. Save the file
4. The change will be automatically picked up by all agents using that prompt

## Example Prompt File

```python
# chatter_prompts.py

CHAT_SYSTEM = """You are roleplaying as the character described below.
Stay in character at all times.

{character_context}

... (rest of prompt)
"""

CHAT_USER = "{query}"
```

## Best Practices

1. **Keep prompts focused**: Each prompt should have a single, clear purpose
2. **Use descriptive variable names**: Make placeholders obvious (e.g., `{character_context}`)
3. **Document expectations**: Add comments explaining what the prompt should return
4. **Test changes**: Verify prompt modifications work as expected
5. **Version important changes**: Use git to track significant prompt updates
