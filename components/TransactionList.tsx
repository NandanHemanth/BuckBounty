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

export default function TransactionList({ 
  userId, 
  onTransactionAdded 
}: { 
  userId: string;
  onTransactionAdded?: () => void;
}) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [lastTransactionCount, setLastTransactionCount] = useState(0);
  const transactionsPerPage = 100;

  const fetchTransactions = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/transactions/${userId}?days=730`);
      const newTransactions = response.data.transactions;
      
      // Check if new transactions were added (compare count)
      if (lastTransactionCount > 0 && newTransactions.length > lastTransactionCount) {
        console.log(`New transactions detected: ${newTransactions.length - lastTransactionCount} added`);
        onTransactionAdded?.();
      }
      
      setLastTransactionCount(newTransactions.length);
      setTransactions(newTransactions);
      
      if (!silent) {
        setCurrentPage(1); // Reset to first page only on manual refresh
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
    if (!silent) setLoading(false);
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
      setCurrentPage(1); // Reset to first page
    } catch (error) {
      console.error('Error searching transactions:', error);
    }
    setLoading(false);
  };

  // Pagination calculations
  const totalPages = Math.ceil(transactions.length / transactionsPerPage);
  const startIndex = (currentPage - 1) * transactionsPerPage;
  const endIndex = startIndex + transactionsPerPage;
  const currentTransactions = transactions.slice(startIndex, endIndex);

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const goToPage = (page: number) => {
    setCurrentPage(page);
  };

  useEffect(() => {
    fetchTransactions();
    
    // Silent polling every 10 seconds to detect new transactions (doesn't show loading state)
    const interval = setInterval(() => {
      fetchTransactions(true); // Silent refresh
    }, 10000);
    
    return () => clearInterval(interval);
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
          onKeyDown={(e) => e.key === 'Enter' && searchTransactions()}
          className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
        />
        <button
          onClick={searchTransactions}
          className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-all duration-200 flex items-center gap-1.5"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          Search
        </button>
        <button
          onClick={() => fetchTransactions(false)}
          className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-all duration-200 flex items-center gap-1.5"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Transaction List */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : transactions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No transactions found</div>
      ) : (
        <>
          <div className="space-y-3">
            {currentTransactions.map((txn) => (
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

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between border-t pt-4">
              <div className="text-xs text-gray-500">
                Showing {startIndex + 1}-{Math.min(endIndex, transactions.length)} of {transactions.length}
              </div>
              
              <div className="flex items-center gap-1.5">
                <button
                  onClick={goToPrevPage}
                  disabled={currentPage === 1}
                  className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-300 text-gray-700 rounded-lg font-medium transition-all duration-200 flex items-center gap-1"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Prev
                </button>
                
                <div className="flex gap-1">
                  {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 7) {
                      pageNum = i + 1;
                    } else if (currentPage <= 4) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 3) {
                      pageNum = totalPages - 6 + i;
                    } else {
                      pageNum = currentPage - 3 + i;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => goToPage(pageNum)}
                        className={`min-w-[32px] h-8 text-sm rounded-lg font-medium transition-all duration-200 ${
                          currentPage === pageNum
                            ? 'bg-indigo-600 text-white shadow-sm'
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={goToNextPage}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-300 text-gray-700 rounded-lg font-medium transition-all duration-200 flex items-center gap-1"
                >
                  Next
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
