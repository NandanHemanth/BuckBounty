'use client';

import { useState } from 'react';
import PlaidLink from '@/components/PlaidLink';
import TransactionList from '@/components/TransactionList';
import Dashboard from '@/components/Dashboard';
import EmbeddingVisualizer from '@/components/EmbeddingVisualizer';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-2">
            💰 BuckBounty
          </h1>
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
            <TransactionList userId={userId} onTransactionAdded={() => setRefreshTrigger(prev => prev + 1)} />
          </div>
        )}

      </div>

      {/* Embedding Visualizer - Bottom Left */}
      {isConnected && <EmbeddingVisualizer userId={userId} />}

      {/* MARK - Animated Agent in Bottom Right */}
      <div className="fixed bottom-6 right-6 z-50">
        <div className="relative group">
          {/* Agent Container */}
          <div className="bg-white rounded-full shadow-2xl p-4 cursor-pointer transform transition-all duration-300 hover:scale-110 animate-bounce">
            <div className="text-4xl">🤖</div>
          </div>
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
            <div className="bg-gray-800 text-white text-sm rounded-lg py-2 px-3 whitespace-nowrap">
              Hi! I'm MARK, your AI assistant
            </div>
          </div>
          
          {/* Pulse Effect */}
          <div className="absolute inset-0 rounded-full bg-indigo-400 opacity-75 animate-ping"></div>
        </div>
      </div>
    </main>
  );
}
