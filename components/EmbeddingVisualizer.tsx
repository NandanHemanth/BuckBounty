'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface CategoryData {
  count: number;
  total_amount: number;
  avg_amount: number;
}

interface CategoryStats {
  [key: string]: CategoryData;
}

export default function EmbeddingVisualizer({ userId }: { userId: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [stats, setStats] = useState<CategoryStats>({});
  const [timeFilter, setTimeFilter] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<any>(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/stats/categories?time_filter=${timeFilter}`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
    setLoading(false);
  };

  const fetchProcessingStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/processing/status');
      setProcessingStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStats();
      fetchProcessingStatus();
      
      // Poll processing status every 5 seconds
      const interval = setInterval(fetchProcessingStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [isOpen, timeFilter]);

  const filteredStats = stats;
  const sortedCategories = Object.entries(filteredStats).sort(
    (a, b) => b[1].total_amount - a[1].total_amount
  );

  const totalSpent = Object.values(filteredStats).reduce(
    (sum, cat) => sum + cat.total_amount,
    0
  );

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'Food & Dining': 'bg-orange-500',
      'Groceries': 'bg-green-500',
      'Transportation': 'bg-blue-500',
      'Shopping': 'bg-purple-500',
      'Entertainment': 'bg-pink-500',
      'Bills & Utilities': 'bg-yellow-500',
      'Health & Fitness': 'bg-red-500',
      'EMI & Loans': 'bg-indigo-500',
      'Credit Cards': 'bg-cyan-500',
      'Income': 'bg-emerald-500',
      'Fun & Leisure': 'bg-rose-500',
      'Other': 'bg-gray-500'
    };
    return colors[category] || 'bg-gray-500';
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      'Food & Dining': '🍔',
      'Groceries': '🛒',
      'Transportation': '🚗',
      'Shopping': '🛍️',
      'Entertainment': '🎬',
      'Bills & Utilities': '💡',
      'Health & Fitness': '💪',
      'EMI & Loans': '💳',
      'Credit Cards': '💳',
      'Income': '💰',
      'Fun & Leisure': '🎉',
      'Other': '📦'
    };
    return icons[category] || '📦';
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-6 bottom-6 z-50 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white p-4 rounded-full shadow-2xl transition-all duration-300 hover:scale-110"
        title="View Embedding Analytics"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">📊 Embedding Analytics</h2>
                  <p className="text-purple-100 text-sm mt-1">
                    AI-powered transaction insights
                  </p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Processing Status */}
              {processingStatus && (
                <div className="mt-4 bg-white bg-opacity-20 rounded-lg p-3">
                  <div className="flex items-center justify-between text-sm">
                    <span>
                      {processingStatus.processing ? '🔄 Processing...' : '✅ All processed'}
                    </span>
                    <span>
                      {processingStatus.processed_transactions} / {processingStatus.total_transactions} transactions
                    </span>
                  </div>
                  {processingStatus.processing && (
                    <div className="mt-2 bg-white bg-opacity-30 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-white h-full transition-all duration-300"
                        style={{
                          width: `${(processingStatus.processed_transactions / processingStatus.total_transactions) * 100}%`
                        }}
                      />
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Time Filters */}
            <div className="p-6 border-b">
              <div className="flex gap-2 flex-wrap">
                {['1m', '3m', '6m', '1y', 'all'].map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setTimeFilter(filter)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      timeFilter === filter
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    }`}
                  >
                    {filter === '1m' && '1 Month'}
                    {filter === '3m' && '3 Months'}
                    {filter === '6m' && '6 Months'}
                    {filter === '1y' && '1 Year'}
                    {filter === 'all' && 'All Time'}
                  </button>
                ))}
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {loading ? (
                <div className="text-center py-12 text-gray-500">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                  Loading analytics...
                </div>
              ) : sortedCategories.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  No data available. Process transactions first.
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Summary Cards */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
                      <div className="text-sm text-blue-600 font-medium">Total Spent</div>
                      <div className="text-2xl font-bold text-blue-900 mt-1">
                        ${totalSpent.toFixed(2)}
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4">
                      <div className="text-sm text-purple-600 font-medium">Categories</div>
                      <div className="text-2xl font-bold text-purple-900 mt-1">
                        {sortedCategories.length}
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
                      <div className="text-sm text-green-600 font-medium">Transactions</div>
                      <div className="text-2xl font-bold text-green-900 mt-1">
                        {Object.values(filteredStats).reduce((sum, cat) => sum + cat.count, 0)}
                      </div>
                    </div>
                  </div>

                  {/* Category Breakdown */}
                  <div className="space-y-3">
                    <h3 className="text-lg font-bold text-gray-800">Category Breakdown</h3>
                    {sortedCategories.map(([category, data]) => {
                      const percentage = (data.total_amount / totalSpent) * 100;
                      return (
                        <div key={category} className="bg-gray-50 rounded-xl p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">{getCategoryIcon(category)}</span>
                              <div>
                                <div className="font-semibold text-gray-800">{category}</div>
                                <div className="text-sm text-gray-500">
                                  {data.count} transactions • Avg: ${data.avg_amount.toFixed(2)}
                                </div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-bold text-gray-900">
                                ${data.total_amount.toFixed(2)}
                              </div>
                              <div className="text-sm text-gray-500">
                                {percentage.toFixed(1)}%
                              </div>
                            </div>
                          </div>
                          <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                            <div
                              className={`${getCategoryColor(category)} h-full transition-all duration-500`}
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
