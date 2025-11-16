'use client';

import { useState } from 'react';
import PlaidLink from '@/components/PlaidLink';
import TransactionList from '@/components/TransactionList';
import Dashboard from '@/components/Dashboard';
import BillSplitModal from '@/components/BillSplitModal';
import ChatInterface from '@/components/ChatInterface';
import NotificationBell from '@/components/NotificationBell';
import FinancialTipsLoader from '@/components/FinancialTipsLoader';
import PolyMarketWidget from '@/components/PolyMarketWidget';
import VantaBackground from '@/components/VantaBackground';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);
  const [userId] = useState('user_' + Math.random().toString(36).substring(2, 11));
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isBillSplitOpen, setIsBillSplitOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <main className="min-h-screen bg-black text-green-500 flex relative">
      {/* Vanta.js Animated Background */}
      <VantaBackground />
      
      {/* Main Dashboard Area */}
      <div className={`transition-all duration-300 ${isChatOpen ? 'w-2/3' : 'w-full'} relative z-10`}>
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="text-center mb-12 relative">
            <div className="flex items-center justify-center gap-4 mb-2">
              {isConnected && (
                <>
                  <Button
                    onClick={() => setIsBillSplitOpen(true)}
                    className="absolute left-0 top-1/2 -translate-y-1/2 bg-gradient-green text-black hover:glow hover-lift"
                  >
                    <span className="text-2xl mr-2">🧾</span>
                    Split Bill
                  </Button>
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 flex flex-col gap-3">
                    <Button
                      onClick={() => window.open('https://polymarket.com', '_blank')}
                      className="bg-green-600 hover:bg-green-700 text-black hover-lift"
                    >
                      <span className="text-2xl mr-2">📊</span>
                      PolyMarket
                    </Button>
                    <Button
                      onClick={() => window.open('https://robinhood.com', '_blank')}
                      className="bg-green-600 hover:bg-green-700 text-black hover-lift"
                    >
                      <span className="text-2xl mr-2">📈</span>
                      Stocks
                    </Button>
                  </div>
                </>
              )}
              <h1 className="text-6xl font-bold text-green-500 glow-text">
                💰 BuckBounty
              </h1>
            </div>
            <p className="text-xl text-green-400">
              Your AI-Powered Personal Finance Assistant
            </p>
          </header>

          {/* Main Content */}
          {!isConnected ? (
            <Card className="max-w-2xl mx-auto glass glow p-8 border-green-500/30">
              <div className="text-center">
                <div className="text-6xl mb-4">🏦</div>
                <h2 className="text-3xl font-bold text-green-500 mb-4 glow-text">
                  Connect Your Bank Account
                </h2>
                <p className="text-green-400 mb-6">
                  Securely connect your bank account using Plaid to start tracking
                  your transactions and get AI-powered insights.
                </p>
                <PlaidLink
                  userId={userId}
                  onSuccess={() => {
                    setIsConnected(true);
                    setRefreshTrigger(prev => prev + 1);
                  }}
                />
              </div>
            </Card>
          ) : (
            <div className="space-y-6">
              <Dashboard userId={userId} refreshTrigger={refreshTrigger} />
              <PolyMarketWidget />
              <TransactionList 
                userId={userId} 
                onTransactionAdded={() => setRefreshTrigger(prev => prev + 1)}
                refreshTrigger={refreshTrigger}
              />
            </div>
          )}
        </div>

        {/* Notification Bell */}
        {isConnected && <NotificationBell />}
      </div>

      {/* Chat Interface */}
      {isConnected && (
        <div className={`fixed right-0 top-0 h-full transition-all duration-300 ${isChatOpen ? 'w-1/3' : 'w-0'} z-50`}>
          {isChatOpen && (
            <ChatInterface
              isOpen={isChatOpen}
              onClose={() => setIsChatOpen(false)}
              userId={userId}
            />
          )}
        </div>
      )}

      {/* Chat Toggle Button */}
      {isConnected && (
        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className="fixed bottom-8 right-8 z-40 glass border-2 border-green-500 text-green-500 hover:bg-green-500 hover:text-black rounded-full w-20 h-20 shadow-2xl flex items-center justify-center text-3xl transition-all duration-300 animate-float glow-pulse"
        >
          {isChatOpen ? '✕' : '💬'}
        </button>
      )}

      {/* Bill Split Modal */}
      <BillSplitModal
        isOpen={isBillSplitOpen}
        onClose={() => setIsBillSplitOpen(false)}
        userId={userId}
        onTransactionAdded={() => setRefreshTrigger(prev => prev + 1)}
      />
    </main>
  );
}
