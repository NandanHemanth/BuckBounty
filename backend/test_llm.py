"""
Test LLM integration (OpenRouter + Gemini fallback)
"""

import asyncio
import os
import sys
import io
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

load_dotenv()

from agents.base_agent import BaseAgent


async def test_llm():
    """Test OpenRouter and Gemini APIs"""
    print("\n" + "="*60)
    print("Testing LLM Integration")
    print("="*60 + "\n")

    # Check API keys
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    print(f"OpenRouter API Key: {'✅ Set' if openrouter_key else '❌ Missing'}")
    print(f"Gemini API Key: {'✅ Set' if gemini_key else '❌ Missing'}")

    if not openrouter_key and not gemini_key:
        print("\n❌ No API keys found! Please set OPENROUTER_API_KEY or GEMINI_API_KEY in .env")
        return

    print("\n" + "-"*60)
    print("Creating test agent...")
    print("-"*60 + "\n")

    # Create a test agent
    agent = BaseAgent(
        agent_name="TestAgent",
        agent_type="Test",
        capabilities=["testing"],
        model="anthropic/claude-3.5-sonnet"
    )

    print("\n" + "-"*60)
    print("Test 1: Simple greeting")
    print("-"*60 + "\n")

    try:
        response = await agent.generate_response(
            prompt="Say hello in one short sentence.",
            context={"test": "greeting"},
            temperature=0.7,
            max_tokens=50
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "-"*60)
    print("Test 2: Financial advice")
    print("-"*60 + "\n")

    try:
        response = await agent.generate_response(
            prompt="Give me one quick tip for saving money. Keep it to one sentence.",
            context={"topic": "finance"},
            temperature=0.7,
            max_tokens=100
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*60)
    print("LLM Testing Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_llm())
