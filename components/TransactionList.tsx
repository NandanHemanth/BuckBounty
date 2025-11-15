'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Transaction {
  id: string;
  date: string;
  amount: number;
  merchant: string;
  category: string;
  pending: boolean;
}

export default function TransactionList({ userId }: { userId: string }) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/transactions/${userId}?days=730`);
      setTransactions(response.data.transactions);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
    setLoading(false);
  };

  const searchTransactions = async () => {
    if (!searchQuery.trim()) {
      fetchTransactions();
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/transactions/search?query=${searchQuery}&limit=20`);
      setTransactions(response.data.results);
    } catch (error) {
      console.error('Error searching transactions:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchTransactions();
  }, [userId]);

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">💳 Transactions</h2>
      
      {/* Search Bar */}
      <div className="mb-6 flex gap-2">
        <input
          type="text"
          placeholder="Search transactions (e.g., 'coffee shops' or 'groceries')"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && searchTransactions()}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
        <button
          onClick={searchTransactions}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium"
        >
          🔍 Search
        </button>
        <button
          onClick={fetchTransactions}
          className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-medium"
        >
          ↻ Refresh
        </button>
      </div>

      {/* Transaction List */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : transactions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No transactions found</div>
      ) : (
        <div className="space-y-3">
          {transactions.map((txn) => (
            <div
              key={txn.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex-1">
                <div className="font-semibold text-gray-800">{txn.merchant}</div>
                <div className="text-sm text-gray-500">
                  {txn.category} • {new Date(txn.date).toLocaleDateString()}
                  {txn.pending && <span className="ml-2 text-yellow-600">⏳ Pending</span>}
                </div>
              </div>
              <div className={`text-lg font-bold ${txn.amount > 0 ? 'text-red-600' : 'text-green-600'}`}>
                ${Math.abs(txn.amount).toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
