"""
MCP (Model Context Protocol) Server
Orchestrates communication between agents and routes requests
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class MCPServer:
    """
    MCP Server for agent orchestration
    Manages agent lifecycle, routing, and inter-agent communication
    """

    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False

        print("🚀 MCP Server initialized")

    def register_agent(self, agent_id: str, agent_instance: Any):
        """Register an agent with the MCP server"""
        self.agents[agent_id] = {
            "instance": agent_instance,
            "registered_at": datetime.now(),
            "message_count": 0
        }
        print(f"✅ Agent registered: {agent_id}")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"❌ Agent unregistered: {agent_id}")

    async def route_request(
        self,
        user_id: str,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        target_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route a user request to the appropriate agent(s)
        """
        # Create or retrieve session
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0
            }

        session = self.sessions[user_id]
        session["last_activity"] = datetime.now()
        session["message_count"] += 1

        # Determine which agent should handle this
        if target_agent and target_agent in self.agents:
            agent_id = target_agent
        else:
            # Default to MARK agent for orchestration
            agent_id = "mark"

        # Get the agent instance
        if agent_id not in self.agents:
            return {
                "success": False,
                "error": f"Agent '{agent_id}' not available",
                "agent": None,
                "response": "I apologize, but the requested agent is not available right now."
            }

        agent_info = self.agents[agent_id]
        agent = agent_info["instance"]

        # Process the request
        try:
            result = await agent.process_request({
                "user_id": user_id,
                "message": message,
                "conversation_history": conversation_history or [],
                "session": session
            })

            agent_info["message_count"] += 1

            return {
                "success": True,
                "agent": agent_id,
                "response": result.get("response", ""),
                "data": result.get("data", {}),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Error processing request with {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": agent_id,
                "response": f"I encountered an error while processing your request: {str(e)}"
            }

    async def broadcast_to_agents(self, message: Dict[str, Any], exclude: Optional[List[str]] = None):
        """Broadcast a message to all agents (or subset)"""
        exclude = exclude or []
        tasks = []

        for agent_id, agent_info in self.agents.items():
            if agent_id not in exclude:
                agent = agent_info["instance"]
                if hasattr(agent, "receive_broadcast"):
                    tasks.append(agent.receive_broadcast(message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_server_status(self) -> Dict[str, Any]:
        """Get MCP server status"""
        return {
            "is_running": self.is_running,
            "active_agents": len(self.agents),
            "active_sessions": len(self.sessions),
            "agents": {
                agent_id: {
                    "message_count": info["message_count"],
                    "registered_at": info["registered_at"].isoformat(),
                    "status": info["instance"].get_status()
                }
                for agent_id, info in self.agents.items()
            }
        }

    async def start(self):
        """Start the MCP server"""
        self.is_running = True
        print("✅ MCP Server started")

    async def stop(self):
        """Stop the MCP server"""
        self.is_running = False
        print("⏹️ MCP Server stopped")


# Global MCP server instance
mcp_server = MCPServer()
