"use client";

import React, { useState } from 'react';

interface SavingsOptimizationButtonProps {
  onOptimize: () => void;
  loading?: boolean;
}

export default function SavingsOptimizationButton({ 
  onOptimize, 
  loading = false 
}: SavingsOptimizationButtonProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="w-full mb-4">
      <button
        onClick={onOptimize}
        disabled={loading}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="w-full bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 hover:from-green-600 hover:via-emerald-600 hover:to-teal-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        style={{ minHeight: '120px' }}
      >
        <div className="flex items-center justify-between px-6 py-4 h-full">
          {/* Left Section - Icon and Title */}
          <div className="flex items-center gap-4 flex-1">
            <div className="bg-white/20 backdrop-blur-sm rounded-full p-4 flex items-center justify-center">
              {loading ? (
                <div className="animate-spin rounded-full h-10 w-10 border-4 border-white border-t-transparent" />
              ) : (
                <span className="text-4xl">💰</span>
              )}
            </div>
            
            <div className="text-left">
              <h2 className="text-2xl font-bold mb-1 flex items-center gap-2">
                Maximize My Savings
                {!loading && (
                  <span className="text-sm bg-white/20 px-2 py-1 rounded-full">
                    Current Month
                  </span>
                )}
              </h2>
              <p className="text-white/90 text-sm">
                {loading 
                  ? "Analyzing your transactions..." 
                  : "Get credit card recommendations, coupon savings & investment portfolio"
                }
              </p>
            </div>
          </div>

          {/* Right Section - Stats Preview */}
          {!loading && (
            <div className="hidden md:flex flex-col items-end gap-2 bg-white/10 backdrop-blur-sm rounded-lg p-4 min-w-[200px]">
              <div className="flex items-center gap-2">
                <span className="text-2xl">💳</span>
                <div className="text-left">
                  <div className="text-xs text-white/80">Credit Cards</div>
                  <div className="text-lg font-bold">Optimize</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl">🎟️</span>
                <div className="text-left">
                  <div className="text-xs text-white/80">Coupons</div>
                  <div className="text-lg font-bold">Save More</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl">📈</span>
                <div className="text-left">
                  <div className="text-xs text-white/80">Investment</div>
                  <div className="text-lg font-bold">Build Wealth</div>
                </div>
              </div>
            </div>
          )}

          {/* Arrow Icon */}
          {!loading && (
            <div className={`ml-4 transition-transform duration-300 ${isHovered ? 'translate-x-2' : ''}`}>
              <svg 
                className="w-8 h-8" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M13 7l5 5m0 0l-5 5m5-5H6" 
                />
              </svg>
            </div>
          )}
        </div>

        {/* Bottom Progress Bar (when loading) */}
        {loading && (
          <div className="w-full bg-white/20 h-1 overflow-hidden">
            <div className="h-full bg-white animate-progress-bar" />
          </div>
        )}
      </button>

      {/* Quick Stats Bar */}
      <div className="mt-2 flex items-center justify-center gap-4 text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>AI-Powered Analysis</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
          <span>Real Credit Card Data</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
          <span>10-Year Projections</span>
        </div>
      </div>

      <style jsx>{`
        @keyframes progress-bar {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
        .animate-progress-bar {
          animation: progress-bar 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
