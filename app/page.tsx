'use client';

import { useState } from 'react';
import PlaidLink from '@/components/PlaidLink';
import TransactionList from '@/components/TransactionList';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));

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
            <Dashboard userId={userId} />
            <TransactionList userId={userId} />
          </div>
        )}

        {/* Features Section */}
        <div className="mt-16 grid md:grid-cols-3 gap-6">
          <FeatureCard 
            icon="🤖"
            title="AI Assistant (MARK)"
            description="Get personalized financial advice and insights"
          />
          <FeatureCard 
            icon="🔍"
            title="Smart Search"
            description="Find transactions using natural language"
          />
          <FeatureCard 
            icon="💾"
            title="Vector DB Storage"
            description="All transactions stored locally with AI embeddings"
          />
        </div>
      </div>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 text-center">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
