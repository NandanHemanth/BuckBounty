'use client';

import { useState } from 'react';
import PlaidLink from '@/components/PlaidLink';
import TransactionList from '@/components/TransactionList';
import Dashboard from '@/components/Dashboard';
import EmbeddingVisualizer from '@/components/EmbeddingVisualizer';
import BillSplitModal from '@/components/BillSplitModal';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [userId] = useState('user_' + Math.random().toString(36).substring(2, 11));
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isBillSplitOpen, setIsBillSplitOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Debug: Log state changes
  console.log('Chat state:', { isConnected, isChatOpen });

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex">
      {/* Main Dashboard Area */}
      <div className={`transition-all duration-300 ${isChatOpen ? 'w-2/3' : 'w-full'}`}>
        <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12 relative">
          <div className="flex items-center justify-center gap-4 mb-2">
            {isConnected && (
              <>
                <button
                  onClick={() => setIsBillSplitOpen(true)}
                  className="absolute left-0 top-1/2 -translate-y-1/2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2"
                >
                  <span className="text-2xl">🧾</span>
                  <span>Split Bill</span>
                </button>
                <div className="absolute right-0 top-1/2 -translate-y-1/2 flex flex-col gap-3">
                  <button
                    onClick={() => window.open('https://polymarket.com', '_blank')}
                    className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2"
                  >
                    <span className="text-2xl">📊</span>
                    <span>PolyMarket</span>
                  </button>
                  <button
                    onClick={() => window.open('https://robinhood.com', '_blank')}
                    className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-2"
                  >
                    <span className="text-2xl">📈</span>
                    <span>Stocks</span>
                  </button>
                </div>
              </>
            )}
            <h1 className="text-5xl font-bold text-gray-800">
              💰 BuckBounty
            </h1>
          </div>
          <p className="text-xl text-gray-600">
            Your AI-Powered Personal Finance Assistant
          </p>
        </header>

        {/* Main Content */}
        {!isConnected ? (
          <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">🏦</div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                Connect Your Bank Account
              </h2>
              <p className="text-gray-600 mb-6">
                Securely connect your bank account using Plaid to start tracking
                your transactions and get AI-powered insights.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-800">
                  🔒 <strong>Sandbox Mode:</strong> We're using Plaid's free sandbox
                  environment for testing. Your real bank data is safe!
                </p>
              </div>
            </div>
            
            <PlaidLink 
              userId={userId} 
              onSuccess={() => setIsConnected(true)}
            />
          </div>
        ) : (
          <div className="space-y-6">
            <Dashboard userId={userId} refreshTrigger={refreshTrigger} />
            <TransactionList 
              userId={userId} 
              onTransactionAdded={() => setRefreshTrigger(prev => prev + 1)}
              refreshTrigger={refreshTrigger}
            />
          </div>
        )}

        </div>

        {/* Embedding Visualizer - Bottom Left */}
        {isConnected && <EmbeddingVisualizer userId={userId} />}

      {/* Bill Split Modal */}
      <BillSplitModal
        isOpen={isBillSplitOpen}
        onClose={() => setIsBillSplitOpen(false)}
        userId={userId}
        onTransactionAdded={() => setRefreshTrigger(prev => prev + 1)}
      />

        {/* MARK - Animated Agent in Bottom Right (only show when chat is closed and connected) */}
        {isConnected && !isChatOpen && (
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              console.log('MARK clicked! Current state:', { isConnected, isChatOpen });
              console.log('Setting isChatOpen to true...');
              setIsChatOpen(true);
              console.log('State update called');
            }}
            className="fixed bottom-6 right-6 z-[100] bg-white rounded-full shadow-2xl p-4 cursor-pointer transform transition-all duration-300 hover:scale-110 active:scale-95 group"
            aria-label="Open MARK Assistant"
          >
            <div className="text-4xl relative z-10">🤖</div>
            
            {/* Tooltip */}
            <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              <div className="bg-gray-800 text-white text-sm rounded-lg py-2 px-3 whitespace-nowrap">
                Hi! I'm MARK, your AI assistant
              </div>
            </div>

            {/* Pulse Effect */}
            <div className="absolute inset-0 rounded-full bg-indigo-400 opacity-75 animate-ping -z-10"></div>
          </button>
        )}
      </div>

      {/* Chat Interface - Right Side (1/3 of screen) */}
      <div className={`transition-all duration-300 ease-in-out ${isChatOpen ? 'w-1/3' : 'w-0'} overflow-hidden`}>
        {isChatOpen && (
          <div className="h-screen w-full">
            <ChatInterface
              isOpen={isChatOpen}
              onClose={() => {
                console.log('Closing chat...');
                setIsChatOpen(false);
              }}
              userId={userId}
            />
          </div>
        )}
      </div>
    </main>
  );
}
