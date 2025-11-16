"use client";

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';

interface Market {
  id: string;
  question: string;
  odds: {
    yes: number;
    no: number;
  };
  volume: number;
  liquidity: number;
  category: string;
  end_date: string | null;
  active: boolean;
}

export default function PolyMarketWidget() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrendingMarkets();
  }, []);

  const fetchTrendingMarkets = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/polymarket/trending?limit=5');
      const data = await response.json();
      setMarkets(data.markets || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching PolyMarket data:', err);
      setError('Unable to load prediction markets');
    } finally {
      setLoading(false);
    }
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `$${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `$${(volume / 1000).toFixed(0)}K`;
    }
    return `$${volume.toFixed(0)}`;
  };

  const getOddsColor = (odds: number) => {
    if (odds >= 70) return 'text-green-600';
    if (odds >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCategoryEmoji = (category: string) => {
    const categoryMap: { [key: string]: string } = {
      'Crypto': '₿',
      'Economics': '📊',
      'Stock Market': '📈',
      'Politics': '🏛️',
      'Sports': '⚽',
      'General': '🎯'
    };
    return categoryMap[category] || '🎯';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-gray-100 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          🔮 Prediction Markets
        </h3>
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchTrendingMarkets}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <Activity className="w-5 h-5" />
          🔮 Prediction Markets
        </h3>
        <button
          onClick={fetchTrendingMarkets}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {markets.map((market) => (
          <div
            key={market.id}
            className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">{getCategoryEmoji(market.category)}</span>
                  <span className="text-xs font-semibold text-gray-500 uppercase">
                    {market.category}
                  </span>
                </div>
                <h4 className="font-semibold text-sm leading-tight">
                  {market.question}
                </h4>
              </div>
            </div>

            <div className="flex items-center justify-between mt-3">
              <div className="flex gap-4">
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <span className={`font-bold ${getOddsColor(market.odds.yes)}`}>
                    {market.odds.yes}%
                  </span>
                  <span className="text-xs text-gray-500">Yes</span>
                </div>
                <div className="flex items-center gap-1">
                  <TrendingDown className="w-4 h-4 text-red-600" />
                  <span className={`font-bold ${getOddsColor(market.odds.no)}`}>
                    {market.odds.no}%
                  </span>
                  <span className="text-xs text-gray-500">No</span>
                </div>
              </div>

              <div className="flex items-center gap-1 text-gray-600">
                <DollarSign className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {formatVolume(market.volume)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          💡 Ask MARK: "Analyze PolyMarket opportunities" for AI insights
        </p>
      </div>
    </div>
  );
}
