"use client";

import React, { useState, useEffect } from 'react';

interface AgentStatus {
  bounty_hunter_1: string;
  bounty_hunter_2: string;
  mark: string;
}

export default function AgentStatusIndicator() {
  const [status, setStatus] = useState<AgentStatus>({
    bounty_hunter_1: 'Ready',
    bounty_hunter_2: 'Ready',
    mark: 'Ready'
  });

  useEffect(() => {
    // Fetch status initially
    fetchStatus();

    // Poll every 2 seconds
    const interval = setInterval(fetchStatus, 2000);

    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/status');
      const data = await response.json();
      
      if (data.agent_status) {
        setStatus(data.agent_status);
      }
    } catch (error) {
      console.error('Error fetching agent status:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Running':
        return 'bg-yellow-400 animate-pulse';
      case 'Ready':
        return 'bg-green-400';
      case 'Error':
        return 'bg-red-400';
      default:
        return 'bg-gray-400';
    }
  };

  const agents = [
    { id: 'mark', name: 'MARK', icon: '👔' },
    { id: 'bounty_hunter_1', name: 'BH1', icon: '🎟️' },
    { id: 'bounty_hunter_2', name: 'BH2', icon: '📰' }
  ];

  return (
    <div className="flex items-center gap-3">
      {agents.map((agent) => {
        const agentStatus = status[agent.id as keyof AgentStatus] || 'Ready';
        
        return (
          <div
            key={agent.id}
            className="flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200"
          >
            <span className="text-sm">{agent.icon}</span>
            <span className="text-xs font-medium text-gray-700">
              {agent.name}
            </span>
            <div className={`w-2 h-2 rounded-full ${getStatusColor(agentStatus)}`} />
          </div>
        );
      })}
    </div>
  );
}
