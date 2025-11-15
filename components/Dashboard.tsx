'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Dashboard({ userId }: { userId: string }) {
  const [stats, setStats] = useState({
    totalTransactions: 0,
    totalSpent: 0,
    avgTransaction: 0,
    topCategory: 'N/A'
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/transactions/${userId}?days=30`);
        const transactions = response.data.transactions;
        
        if (transactions.length > 0) {
          const total = transactions.reduce((sum: number, t: any) => sum + Math.abs(t.amount), 0);
          const categories = transactions.reduce((acc: any, t: any) => {
            acc[t.category] = (acc[t.category] || 0) + 1;
            return acc;
          }, {});
          
          const topCat = Object.entries(categories).sort((a: any, b: any) => b[1] - a[1])[0];
          
          setStats({
            totalTransactions: transactions.length,
            totalSpent: total,
            avgTransaction: total / transactions.length,
            topCategory: topCat ? topCat[0] : 'N/A'
          });
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
  }, [userId]);

  return (
    <div className="grid md:grid-cols-4 gap-4">
      <StatCard
        icon="📊"
        label="Total Transactions"
        value={stats.totalTransactions.toString()}
      />
      <StatCard
        icon="💸"
        label="Total Spent"
        value={`$${stats.totalSpent.toFixed(2)}`}
      />
      <StatCard
        icon="📈"
        label="Avg Transaction"
        value={`$${stats.avgTransaction.toFixed(2)}`}
      />
      <StatCard
        icon="🏆"
        label="Top Category"
        value={stats.topCategory}
      />
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="text-3xl mb-2">{icon}</div>
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className="text-2xl font-bold text-gray-800">{value}</div>
    </div>
  );
}
