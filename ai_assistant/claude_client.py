"""
Claude API client for the AI Assistant.
"""

import os
import anthropic
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT, build_context_prompt

load_dotenv()


def get_client():
    """Initialize and return the Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file.")
    return anthropic.Anthropic(api_key=api_key)


def ask_assistant(messages, report=None):
    """
    Send a conversation to Claude and return the response.
    
    messages: list of dicts with 'role' and 'content'
    report: current validation report for context (optional)
    """
    client = get_client()

    # Build system prompt with report context if available
    system = SYSTEM_PROMPT
    if report:
        context = build_context_prompt(report)
        system += f"\n\n{context}"

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=system,
        messages=messages,
    )

    return response.content[0].text


def init_chat_history():
    """Return the initial chat history with a welcome message."""
    return [
        {
            "role": "assistant",
            "content": "👋 Hi! I'm your Sovos implementation assistant. I can see your current validation report and help you understand errors, suggest fixes, or answer compliance questions. What would you like to know?"
        }
    ]