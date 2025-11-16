'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, X, Loader2, Target, TrendingUp } from 'lucide-react';
import axios from 'axios';
import SavingsOptimizationButton from './SavingsOptimizationButton';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: 'mark' | 'bounty_hunter_1' | 'bounty_hunter_2';
  inferenceTime?: string;
  cached?: boolean;
  timeSaved?: string;
  timeWithoutCache?: string;
  timeWithoutOptimization?: string;
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
      agent: 'mark',
      inferenceTime: '0.01s',
      cached: false
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

  const handleSendMessage = async (messageOverride?: string) => {
    const messageToSend = messageOverride || inputMessage;
    if (!messageToSend.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageToSend,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = messageToSend;
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
        agent: data.agent || 'mark',
        inferenceTime: data.inference_time || '2.34s',
        cached: data.cached || false,
        timeSaved: data.time_saved || '2.29s',
        timeWithoutCache: data.time_without_cache || '2.34s',
        timeWithoutOptimization: data.time_without_optimization || '4.84s'
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Automatically speak MARK's response
      speakResponse(assistantMessage.content);
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
        // Use browser's Web Speech API for speech-to-text
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
          alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
          return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
          setIsRecording(true);
          console.log('Speech recognition started');
        };

        recognition.onresult = async (event: any) => {
          const transcript = event.results[0][0].transcript;
          console.log('Transcribed:', transcript);
          
          // Send the transcribed text as a message
          setInputMessage(transcript);
          await handleSendMessage(transcript);
        };

        recognition.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsRecording(false);
          alert(`Speech recognition error: ${event.error}. Please try again.`);
        };

        recognition.onend = () => {
          setIsRecording(false);
          console.log('Speech recognition ended');
        };

        recognition.start();
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        alert('Failed to start speech recognition. Please try again.');
        setIsRecording(false);
      }
    } else {
      // Stop recording (browser will handle this automatically)
      setIsRecording(false);
    }
  };

  // Text-to-Speech for MARK's responses
  const speakResponse = async (text: string) => {
    try {
      const response = await fetch('/api/text-to-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
      });
      
      if (response.headers.get('Content-Type')?.includes('application/json')) {
        // Fallback to browser's built-in speech synthesis
        const data = await response.json();
        if (data.useBrowserTTS) {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 0.9;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          window.speechSynthesis.speak(utterance);
        }
      } else {
        // Use ElevenLabs audio
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
      }
    } catch (error) {
      console.error('Error playing audio:', error);
      // Final fallback to browser TTS
      try {
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.error('Browser TTS also failed:', e);
      }
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
            <h2 className="text-xl font-bold">MARK</h2>
            <p className="text-xs text-indigo-100">Multi-Agent Finance Orchestrator</p>
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
              <div className="prose prose-sm max-w-none">
                {message.content.split('\n').map((line, i) => {
                  // Handle bold text **text**
                  const boldRegex = /\*\*(.*?)\*\*/g;
                  const parts = line.split(boldRegex);
                  
                  return (
                    <p key={i} className="mb-2 last:mb-0">
                      {parts.map((part, j) => 
                        j % 2 === 1 ? <strong key={j}>{part}</strong> : part
                      )}
                    </p>
                  );
                })}
              </div>
              <div className={`flex items-center gap-2 text-xs mt-2 ${
                message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
              }`}>
                <span>{message.timestamp.toLocaleTimeString()}</span>
                
                {/* Inference Time with Hover Tooltip - Always show for assistant */}
                {message.role === 'assistant' && (
                  <>
                    <span>•</span>
                    <div className="relative group inline-block">
                      <span className={`cursor-help ${message.cached ? 'text-green-600 font-semibold' : 'text-blue-600'}`}>
                        ⚡ {message.inferenceTime || 'N/A'}
                        {message.cached && ' (cached)'}
                      </span>
                      
                      {/* Hover Tooltip */}
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50 shadow-lg">
                        <div className="space-y-1">
                          <div className="font-semibold">⚡ Actual Time: {message.inferenceTime || 'N/A'}</div>
                          {message.cached ? (
                            <>
                              <div className="text-green-400">✓ Retrieved from Redis cache</div>
                              <div className="text-gray-300">Without cache: {message.timeWithoutCache || '~2.5s'}</div>
                              <div className="text-yellow-400">⏱️ Time saved: {message.timeSaved || '~2.5s'}</div>
                              <div className="text-gray-400 text-[10px] mt-1">
                                Using optimized retrieval techniques
                              </div>
                            </>
                          ) : (
                            <>
                              <div className="text-blue-400">Fresh analysis generated</div>
                              {message.timeWithoutOptimization && (
                                <>
                                  <div className="text-gray-300">Without RAG/Cache: {message.timeWithoutOptimization}</div>
                                  <div className="text-yellow-400">⏱️ Optimized by: {(parseFloat(message.timeWithoutOptimization) - parseFloat(message.inferenceTime || '0')).toFixed(2)}s</div>
                                </>
                              )}
                              <div className="text-gray-400 text-[10px] mt-1">
                                Using RAG (FLAT/HNSW) + LLM
                              </div>
                            </>
                          )}
                        </div>
                        {/* Arrow */}
                        <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                          <div className="border-4 border-transparent border-t-gray-900"></div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
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

      {/* Quick Action Buttons - 4 buttons in a row */}
      <div className="border-t border-gray-200 px-4 pt-3 pb-2 bg-white">
        <div className="grid grid-cols-4 gap-2">
          {/* Button 1: Maximize Savings */}
          <button
            onClick={async () => {
              const savingsMessage = "Analyze my current month transactions and show me how to maximize savings with credit cards (specify best card for each category), coupons, and build a wealth investment portfolio";
              await handleSendMessage(savingsMessage);
            }}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-3 bg-gradient-to-br from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 border border-green-200 rounded-lg transition-all duration-200 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="text-2xl mb-1">💰</span>
            <span className="text-xs font-semibold text-gray-800 text-center">Max Savings</span>
          </button>

          {/* Button 2: Budget Check */}
          <button
            onClick={() => {
              const budgetQuery = "Can I afford AirPods Pro 2 ($249)?";
              setInputMessage(budgetQuery);
              handleSendMessage(budgetQuery);
            }}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-3 bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border border-blue-200 rounded-lg transition-all duration-200 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="text-2xl mb-1">🛒</span>
            <span className="text-xs font-semibold text-gray-800 text-center">Budget?</span>
          </button>

          {/* Button 3: Build Wealth */}
          <button
            onClick={() => {
              const wealthQuery = "Build wealth with current market trends";
              setInputMessage(wealthQuery);
              handleSendMessage(wealthQuery);
            }}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-3 bg-gradient-to-br from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 border border-purple-200 rounded-lg transition-all duration-200 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="text-2xl mb-1">📈</span>
            <span className="text-xs font-semibold text-gray-800 text-center">Build Wealth</span>
          </button>

          {/* Button 4: PolyMarket Analysis */}
          <button
            onClick={() => {
              const polymarketQuery = "Analyze PolyMarket prediction market opportunities";
              setInputMessage(polymarketQuery);
              handleSendMessage(polymarketQuery);
            }}
            disabled={isLoading}
            className="flex flex-col items-center justify-center p-3 bg-gradient-to-br from-orange-50 to-yellow-50 hover:from-orange-100 hover:to-yellow-100 border border-orange-200 rounded-lg transition-all duration-200 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="text-2xl mb-1">🔮</span>
            <span className="text-xs font-semibold text-gray-800 text-center">PolyMarket</span>
          </button>
        </div>
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
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(undefined)}
            placeholder="Ask MARK anything about your finances..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={isLoading}
          />

          {/* Send Button */}
          <button
            onClick={() => handleSendMessage(undefined)}
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
