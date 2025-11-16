"""
MARK Agent - Main Personal Finance Agent
Orchestrates all other agents and provides comprehensive financial guidance
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .base_agent import BaseAgent


class MarkAgent(BaseAgent):
    """
    MARK - Main Personal Finance Agent
    Coordinates all other agents and provides unified financial assistance
    """

    def __init__(self, bounty_hunter_1=None, bounty_hunter_2=None):
        super().__init__(
            agent_name="MARK",
            agent_type="Main Personal Finance Agent",
            capabilities=[
                "financial_advice",
                "budget_analysis",
                "spending_insights",
                "agent_orchestration",
                "conversation_management",
                "multi_modal_processing"
            ]
        )

        # Reference to other agents
        self.bounty_hunter_1 = bounty_hunter_1
        self.bounty_hunter_2 = bounty_hunter_2

        # Conversation history per user
        self.conversations: Dict[str, List[Dict]] = {}

        self.personality = {
            "traits": ["friendly", "analytical", "proactive", "educational"],
            "communication_style": "conversational_expert",
            "humor_level": 0.3,
            "formality": 0.5
        }

        print("👔 MARK Agent initialized - Ready to assist!")

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request - main orchestration logic
        """
        user_id = request.get("user_id")
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])

        # Store conversation
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        self.conversations[user_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Analyze intent
        intent = await self._analyze_intent(message)

        # Route to appropriate handler
        if intent == "coupon_search":
            response = await self._handle_coupon_request(user_id, message)
        elif intent == "finance_news":
            response = await self._handle_news_request(user_id, message)
        elif intent == "budget_advice":
            response = await self._handle_budget_advice(user_id, message)
        elif intent == "transaction_analysis":
            response = await self._handle_transaction_analysis(user_id, message)
        elif intent == "general_greeting":
            response = await self._handle_greeting(user_id)
        else:
            response = await self._handle_general_query(user_id, message, conversation_history)

        # Store assistant response
        self.conversations[user_id].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "response": response,
            "intent": intent,
            "data": {}
        }

    async def _analyze_intent(self, message: str) -> str:
        """Analyze user message to determine intent"""
        message_lower = message.lower()

        # Coupon/deal related
        if any(word in message_lower for word in ["coupon", "deal", "discount", "promo", "code", "save money"]):
            return "coupon_search"

        # Finance news related
        if any(word in message_lower for word in ["news", "market", "stock", "economy", "trend", "finance"]):
            return "finance_news"

        # Budget advice
        if any(word in message_lower for word in ["budget", "spending", "afford", "save", "savings"]):
            return "budget_advice"

        # Transaction analysis
        if any(word in message_lower for word in ["transaction", "purchase", "spent", "category", "analyze"]):
            return "transaction_analysis"

        # Greeting
        if any(word in message_lower for word in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon"]):
            return "general_greeting"

        return "general"

    async def _handle_coupon_request(self, user_id: str, message: str) -> str:
        """Handle coupon-related requests via BountyHunter1"""
        if not self.bounty_hunter_1:
            return "My coupon hunter is currently offline. Let me help you with something else!"

        try:
            result = await self.bounty_hunter_1.process_request({
                "user_id": user_id,
                "message": message
            })

            return result.get("response", "I couldn't find any coupons right now.")

        except Exception as e:
            print(f"❌ Error calling BountyHunter1: {e}")
            return "I'm having trouble accessing the coupon database right now. Please try again later!"

    async def _handle_news_request(self, user_id: str, message: str) -> str:
        """Handle finance news requests via BountyHunter2"""
        if not self.bounty_hunter_2:
            return "My finance news tracker is currently offline. Let me help you with something else!"

        try:
            result = await self.bounty_hunter_2.process_request({
                "user_id": user_id,
                "message": message
            })

            return result.get("response", "I couldn't find relevant news right now.")

        except Exception as e:
            print(f"❌ Error calling BountyHunter2: {e}")
            return "I'm having trouble accessing finance news right now. Please try again later!"

    async def _handle_budget_advice(self, user_id: str, message: str) -> str:
        """Provide budget advice based on user's transaction history"""
        # Get user's spending data
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            from vector_db import VectorDB

            vector_db = VectorDB()

            # Get recent budget
            current_month = datetime.now().strftime("%Y-%m")
            budget_data = vector_db.get_budget(current_month)

            # Get spending stats
            stats = vector_db.get_category_stats()

            # Build context
            context = {
                "budget": budget_data.get("amount", 0) if budget_data else 0,
                "categories": len(stats),
                "user_message": message
            }

            prompt = f"""The user asked: "{message}"

Budget information:
- Monthly budget: ${context['budget']}
- Number of spending categories: {context['categories']}

Provide personalized budget advice that:
1. Addresses their specific question
2. Offers actionable tips
3. Suggests areas where they could save money
4. Is encouraging and supportive

Be conversational and friendly (like a helpful financial advisor friend)."""

            response = await self.generate_response(prompt, context, temperature=0.7, max_tokens=500)

            return response

        except Exception as e:
            print(f"❌ Error in budget advice: {e}")
            return "I'd love to help with budgeting! Let me analyze your spending patterns and get back to you with personalized advice."

    async def _handle_transaction_analysis(self, user_id: str, message: str) -> str:
        """Analyze user's transaction patterns"""
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            from vector_db import VectorDB

            vector_db = VectorDB()

            # Get category stats
            stats = vector_db.get_category_stats()

            # Build summary
            summary = "\n".join([
                f"- {stat['category']}: {stat['count']} transactions, ${stat['total_amount']:.2f} total"
                for stat in stats[:10]
            ])

            context = {
                "user_message": message,
                "transaction_summary": summary
            }

            prompt = f"""The user asked: "{message}"

Their recent transaction breakdown:
{summary}

Provide insights that:
1. Highlight spending patterns
2. Identify top spending categories
3. Suggest areas for optimization
4. Offer actionable next steps

Be specific and helpful!"""

            response = await self.generate_response(prompt, context, temperature=0.7, max_tokens=500)

            return response

        except Exception as e:
            print(f"❌ Error in transaction analysis: {e}")
            return "Let me analyze your transactions... I'm having trouble accessing the data right now. Please try again!"

    async def _handle_greeting(self, user_id: str) -> str:
        """Handle greeting messages"""
        greetings = [
            "Hey there! I'm MARK, your personal finance assistant. How can I help you save money today?",
            "Hello! Ready to make your money work smarter? I'm here to help!",
            "Hi! I've got my team of specialized agents ready to help you with budgets, deals, and finance insights. What would you like to know?",
        ]

        import random
        return random.choice(greetings)

    async def _handle_general_query(self, user_id: str, message: str, conversation_history: List[Dict]) -> str:
        """Handle general queries using LLM"""
        # Build conversation context
        recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history

        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in recent_history
        ])

        context = {
            "user_id": user_id,
            "conversation_history": history_text,
            "available_capabilities": ", ".join(self.capabilities)
        }

        prompt = f"""Previous conversation:
{history_text}

User's new message: "{message}"

As MARK, the main personal finance agent, provide a helpful response that:
1. Addresses their question directly
2. Offers relevant financial guidance
3. Suggests how my specialized agents (BountyHunter1 for coupons, BountyHunter2 for news) can help
4. Is friendly and conversational

Available capabilities: {context['available_capabilities']}"""

        response = await self.generate_response(prompt, context, temperature=0.7, max_tokens=600)

        return response

    async def receive_broadcast(self, message: Dict[str, Any]):
        """Receive broadcast messages from MCP server"""
        print(f"📢 MARK received broadcast: {message}")

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Get conversation history for a user"""
        return self.conversations.get(user_id, [])
