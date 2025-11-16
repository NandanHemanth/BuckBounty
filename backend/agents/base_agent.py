"""
Base Agent class for all MCP agents
Provides common functionality for agent communication and LLM integration
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini as fallback
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class BaseAgent:
    """Base class for all agents with OpenRouter + Gemini fallback"""

    def __init__(
        self,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        model: str = "anthropic/claude-3.5-sonnet"
    ):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.model = model

        # API Keys
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Fallback model
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Agent state
        self.is_online = True
        self.last_activity = datetime.now()

        print(f"🤖 {agent_name} initialized with capabilities: {', '.join(capabilities)}")

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate response using OpenRouter (Claude) with Gemini fallback
        """
        try:
            # Try OpenRouter first (Claude)
            return await self._call_openrouter(prompt, context, temperature, max_tokens)
        except Exception as e:
            print(f"⚠️ OpenRouter failed: {e}. Falling back to Gemini...")
            try:
                return await self._call_gemini(prompt, context, temperature, max_tokens)
            except Exception as e2:
                print(f"❌ Both APIs failed: {e2}")
                return f"Error: Unable to generate response. Both OpenRouter and Gemini failed."

    async def _call_openrouter(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Call OpenRouter API with Claude model"""
        if not self.openrouter_api_key:
            raise Exception("OpenRouter API key not configured")

        # Build messages with context
        messages = []
        if context:
            messages.append({
                "role": "system",
                "content": self._build_system_prompt(context)
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "HTTP-Referer": "https://buckbounty.app",
                    "X-Title": "BuckBounty"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_gemini(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Call Gemini API as fallback"""
        if not self.gemini_api_key:
            raise Exception("Gemini API key not configured")

        # Build full prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"{self._build_system_prompt(context)}\n\n{prompt}"

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.gemini_model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
        )

        return response.text

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with agent identity and context"""
        system_prompt = f"""You are {self.agent_name}, a specialized AI agent in the BuckBounty personal finance platform.

Your role: {self.agent_type}
Your capabilities: {', '.join(self.capabilities)}

Context:
"""
        for key, value in context.items():
            system_prompt += f"- {key}: {value}\n"

        return system_prompt

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request - to be overridden by subclasses
        """
        raise NotImplementedError("Subclasses must implement process_request")

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "is_online": self.is_online,
            "last_activity": self.last_activity.isoformat(),
            "capabilities": self.capabilities
        }
