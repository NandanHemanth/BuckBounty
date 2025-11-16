"use client";

import React, { useState, useRef, useEffect } from 'react';
import SavingsOptimizationButton from './SavingsOptimizationButton';
import AgentStatusIndicator from './AgentStatusIndicator';
import IdealPromptButtons from './IdealPromptButtons';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  cached?: boolean;
  inference_time?: string;
}

export default function MarkChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm MARK, your AI finance assistant. I'm backed by a team of specialized agents ready to help you maximize savings and build wealth. Click the button above to get started!",
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [savingsLoading, setSavingsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSavingsOptimization = async () => {
    setSavingsLoading(true);
    await sendMessage("Analyze my current month transactions and show me how to maximize savings with credit cards, coupons, and build a wealth investment portfolio");
    setSavingsLoading(false);
  };

  const sendMessage = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/agents/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'default',
          message: textToSend,
          conversation_history: messages
        })
      });

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || 'Sorry, I encountered an error.',
        timestamp: new Date().toISOString(),
        cached: data.cached,
        inference_time: data.inference_time
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error connecting to the server. Please make sure the backend is running.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-full p-2">
                <span className="text-2xl">👔</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">MARK Assistant</h1>
                <p className="text-sm text-gray-600">Multi-Agent Finance System</p>
              </div>
            </div>
            
            {/* Agent Status */}
            <div className="hidden md:block">
              <AgentStatusIndicator />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-5xl mx-auto h-full flex flex-col px-4 py-4">
          
          {/* Savings Optimization Button - Takes 1/3 space */}
          <div className="mb-4">
            <SavingsOptimizationButton 
              onOptimize={handleSavingsOptimization}
              loading={savingsLoading}
            />
          </div>

          {/* Ideal Prompt Buttons */}
          <div className="mb-4">
            <IdealPromptButtons onPromptClick={sendMessage} />
          </div>

          {/* Messages Area - Takes 2/3 space */}
          <div className="flex-1 overflow-y-auto bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">👔</span>
                        <span className="font-semibold text-sm">MARK</span>
                        {message.cached && (
                          <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">
                            ⚡ Cached
                          </span>
                        )}
                      </div>
                    )}
                    
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    
                    <div className="flex items-center gap-2 mt-2 text-xs opacity-70">
                      <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                      {message.inference_time && (
                        <span>• {message.inference_time}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent" />
                      <span className="text-gray-600">MARK is thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <button className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors">
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </button>

              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask MARK anything about your finances..."
                disabled={loading}
                className="flex-1 px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              />

              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <span>Send</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>

            {/* Mobile Agent Status */}
            <div className="md:hidden mt-3">
              <AgentStatusIndicator />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
