'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, X, Loader2, Target, TrendingUp } from 'lucide-react';
import axios from 'axios';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: 'mark' | 'bounty_hunter_1' | 'bounty_hunter_2';
}

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
}

interface AgentStatus {
  name: string;
  icon: string;
  emoji: string;
  description: string;
  color: string;
  isActive: boolean;
}

export default function ChatInterface({ isOpen, onClose, userId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm MARK, your AI finance assistant. I'm backed by a team of specialized agents:\n\n🎯 BountyHunter1: Finds coupons and deals\n📊 BountyHunter2: Analyzes finance trends\n\nHow can I help you today?",
      timestamp: new Date(),
      agent: 'mark'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([
    {
      name: 'BountyHunter1',
      icon: 'Target',
      emoji: '🎯',
      description: 'Coupon & Deal Hunter',
      color: 'bg-purple-500',
      isActive: true
    },
    {
      name: 'BountyHunter2',
      icon: 'TrendingUp',
      emoji: '📊',
      description: 'Finance News Analyst',
      color: 'bg-blue-500',
      isActive: true
    }
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call backend agent API
      const response = await axios.post('http://localhost:8000/api/agents/chat', {
        user_id: userId,
        message: currentMessage,
        conversation_history: messages.map(m => ({
          role: m.role,
          content: m.content
        }))
      });

      const data = response.data;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date(),
        agent: data.agent || 'mark'
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error connecting to the agent system. Please make sure the backend server is running on port 8000.',
        timestamp: new Date(),
        agent: 'mark'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        const audioChunks: Blob[] = [];

        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

          // TODO: Send audio to speech-to-text service
          console.log('Audio recording completed', audioBlob);

          // For now, show a placeholder message
          const voiceMessage: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'Voice input received! Speech-to-text processing will be implemented soon.',
            timestamp: new Date(),
            agent: 'mark'
          };
          setMessages(prev => [...prev, voiceMessage]);

          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Unable to access microphone. Please check permissions.');
      }
    } else {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    }
  };

  const getAgentIcon = (agent?: string) => {
    switch (agent) {
      case 'bounty_hunter_1': return '🎯';
      case 'bounty_hunter_2': return '📊';
      case 'mark':
      default: return '🤖';
    }
  };

  const getAgentName = (agent?: string) => {
    switch (agent) {
      case 'bounty_hunter_1': return 'BountyHunter1';
      case 'bounty_hunter_2': return 'BountyHunter2';
      case 'mark':
      default: return 'MARK';
    }
  };

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200 shadow-2xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-3xl">🤖</div>
          <div>
            <h2 className="text-xl font-bold">MARK Assistant</h2>
            <p className="text-xs text-indigo-100">Multi-Agent Finance System</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          aria-label="Close chat"
        >
          <X size={24} />
        </button>
      </div>

      {/* Agent Status Cards */}
      <div className="p-4 bg-gradient-to-br from-gray-50 to-white border-b border-gray-200">
        <div className="grid grid-cols-2 gap-3">
          {agentStatuses.map((agent, index) => (
            <div
              key={index}
              className={`p-3 rounded-xl border-2 transition-all duration-200 ${
                agent.isActive
                  ? 'border-green-400 bg-green-50 hover:shadow-md'
                  : 'border-gray-300 bg-gray-50 opacity-60'
              }`}
            >
              <div className="flex items-start gap-2">
                <div className="text-2xl">{agent.emoji}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-sm text-gray-800 truncate">
                      {agent.name}
                    </h3>
                    {agent.isActive && (
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 mt-0.5">{agent.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-4 ${
                message.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-indigo-600">
                  <span>{getAgentIcon(message.agent)}</span>
                  <span>{getAgentName(message.agent)}</span>
                </div>
              )}
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
              <p className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
              }`}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl p-4">
              <div className="flex items-center gap-2 text-gray-600">
                <Loader2 className="animate-spin" size={20} />
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex gap-2">
          {/* Voice Button */}
          <button
            onClick={handleVoiceInput}
            className={`px-4 py-3 rounded-xl font-semibold transition-all duration-200 flex items-center gap-2 ${
              isRecording
                ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
                : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
            }`}
            title={isRecording ? 'Stop recording' : 'Start voice input'}
          >
            {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
          </button>

          {/* Text Input */}
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask MARK anything about your finances..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={isLoading}
          />

          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={20} />
            <span>Send</span>
          </button>
        </div>

        {/* Agent Status Indicators */}
        <div className="mt-3 flex items-center gap-4 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>MARK Online</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>BH1 Ready</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>BH2 Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
}
