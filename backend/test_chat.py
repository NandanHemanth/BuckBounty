"""
Simple test script to verify chat functionality
Tests the agent chat endpoint with OpenRouter/Gemini
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from agents.mcp_server import mcp_server
from agents.mark_agent import MarkAgent
from agents.bounty_hunter_1 import BountyHunter1
from agents.bounty_hunter_2 import BountyHunter2
from dotenv import load_dotenv

load_dotenv()


async def test_chat():
    """Test the chat interface"""
    print("\n" + "="*60)
    print("🧪 TESTING CHAT INTERFACE")
    print("="*60 + "\n")

    # Initialize agents
    print("Initializing agents...")
    bh1 = BountyHunter1()
    bh2 = BountyHunter2()
    mark = MarkAgent(bh1, bh2)

    # Register with MCP
    mcp_server.register_agent("mark", mark)
    mcp_server.register_agent("bounty_hunter_1", bh1)
    mcp_server.register_agent("bounty_hunter_2", bh2)
    await mcp_server.start()

    print("\n✅ All agents initialized!\n")

    # Test messages
    test_messages = [
        "Hello! How can you help me?",
        "Find me some coupons for food delivery",
        "What's happening in the finance market?",
        "Should I spend $100 on groceries this week?"
    ]

    user_id = "test_user_123"

    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─'*60}")
        print(f"Test {i}/{len(test_messages)}")
        print(f"{'─'*60}")
        print(f"👤 User: {message}")
        print(f"\n⏳ Processing...\n")

        try:
            # Route through MCP server
            result = await mcp_server.route_request(
                user_id=user_id,
                message=message,
                conversation_history=[]
            )

            if result['success']:
                print(f"🤖 {result['agent'].upper()}: {result['response'][:200]}...")
                if len(result['response']) > 200:
                    print(f"   ... (truncated, full response is {len(result['response'])} chars)")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()

        # Small delay between tests
        await asyncio.sleep(1)

    print("\n" + "="*60)
    print("✅ CHAT TESTING COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n🔧 Setting up test environment...")
    asyncio.run(test_chat())
