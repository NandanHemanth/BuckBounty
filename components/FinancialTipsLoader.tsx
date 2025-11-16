'use client';

import { useState, useEffect } from 'react';
import { Loader2, TrendingUp, Home, CreditCard, PiggyBank, Target, DollarSign } from 'lucide-react';

const financialTips = [
  {
    icon: CreditCard,
    title: "Building Credit Score",
    tip: "Pay all bills on time - Payment history accounts for 35% of your credit score. Even one late payment can drop your score by 100 points.",
    category: "Credit"
  },
  {
    icon: CreditCard,
    title: "Credit Utilization",
    tip: "Keep credit card balances below 30% of your limit. Ideally, aim for under 10% for the best credit score impact.",
    category: "Credit"
  },
  {
    icon: CreditCard,
    title: "Credit Mix Matters",
    tip: "Having different types of credit (credit cards, auto loans, mortgages) can improve your score by 10%. Diversity shows you can manage various credit types.",
    category: "Credit"
  },
  {
    icon: CreditCard,
    title: "Don't Close Old Cards",
    tip: "Length of credit history matters! Keep your oldest credit card open even if you don't use it. It helps your average account age.",
    category: "Credit"
  },
  {
    icon: CreditCard,
    title: "Limit Hard Inquiries",
    tip: "Each credit application creates a hard inquiry that can lower your score by 5-10 points. Space out applications by 6 months.",
    category: "Credit"
  },
  {
    icon: Home,
    title: "Buying vs Renting",
    tip: "Buy if you plan to stay 5+ years. Renting offers flexibility, buying builds equity. Consider: 20% down payment, 3x monthly income for mortgage.",
    category: "Housing"
  },
  {
    icon: Home,
    title: "The 28/36 Rule",
    tip: "Housing costs shouldn't exceed 28% of gross income. Total debt (including mortgage) shouldn't exceed 36%. This ensures financial stability.",
    category: "Housing"
  },
  {
    icon: Home,
    title: "Hidden Costs of Buying",
    tip: "Budget 1-4% of home value annually for maintenance, plus property taxes, insurance, and HOA fees. Renting includes these in rent.",
    category: "Housing"
  },
  {
    icon: Home,
    title: "Rent vs Buy Calculator",
    tip: "Break-even point is typically 5-7 years. Factor in: down payment opportunity cost, closing costs (2-5%), and potential appreciation (3-4% annually).",
    category: "Housing"
  },
  {
    icon: PiggyBank,
    title: "Emergency Fund First",
    tip: "Save 3-6 months of expenses before investing. This prevents debt during emergencies and provides peace of mind.",
    category: "Savings"
  },
  {
    icon: Target,
    title: "50/30/20 Budget Rule",
    tip: "Allocate 50% to needs, 30% to wants, 20% to savings/debt. This balanced approach ensures you save while enjoying life.",
    category: "Budgeting"
  },
  {
    icon: DollarSign,
    title: "Compound Interest Power",
    tip: "Investing $500/month at 7% return = $600,000 in 30 years. Start early - time is your biggest advantage in wealth building.",
    category: "Investing"
  },
  {
    icon: TrendingUp,
    title: "Index Funds Win",
    tip: "95% of actively managed funds underperform index funds over 15 years. Low-cost index funds (VOO, VTI) are the smart choice.",
    category: "Investing"
  },
  {
    icon: CreditCard,
    title: "Become an Authorized User",
    tip: "Being added to someone's old credit card with good history can boost your score quickly. Their positive history becomes yours.",
    category: "Credit"
  },
  {
    icon: CreditCard,
    title: "Dispute Credit Errors",
    tip: "30% of credit reports have errors. Check your report annually (free at annualcreditreport.com) and dispute any mistakes.",
    category: "Credit"
  },
  {
    icon: Home,
    title: "Rent for Flexibility",
    tip: "Rent if: you might relocate, housing market is overpriced, or you're building emergency fund. Flexibility has value.",
    category: "Housing"
  },
  {
    icon: DollarSign,
    title: "Automate Savings",
    tip: "Set up automatic transfers on payday. 'Pay yourself first' - you won't miss money you never see in checking.",
    category: "Savings"
  },
  {
    icon: Target,
    title: "Track Every Dollar",
    tip: "People who track spending save 20% more. Use apps or spreadsheets - awareness is the first step to control.",
    category: "Budgeting"
  }
];

interface FinancialTipsLoaderProps {
  isLoading: boolean;
}

export default function FinancialTipsLoader({ isLoading }: FinancialTipsLoaderProps) {
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  const [fadeIn, setFadeIn] = useState(true);

  useEffect(() => {
    if (!isLoading) return;

    const interval = setInterval(() => {
      setFadeIn(false);
      
      setTimeout(() => {
        setCurrentTipIndex((prev) => (prev + 1) % financialTips.length);
        setFadeIn(true);
      }, 500); // Fade out duration
    }, 10000); // Change tip every 10 seconds

    return () => clearInterval(interval);
  }, [isLoading]);

  if (!isLoading) return null;

  const currentTip = financialTips[currentTipIndex];
  const Icon = currentTip.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Blurred Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 backdrop-blur-md"></div>
      
      {/* Content */}
      <div className="relative z-10 max-w-2xl mx-auto px-6">
        {/* Spinner */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <Loader2 className="w-16 h-16 text-indigo-600 animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 bg-indigo-100 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Loading Text */}
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-4">
          Setting Up Your Dashboard
        </h2>
        <p className="text-center text-gray-600 mb-12">
          While we prepare your personalized financial insights...
        </p>

        {/* Financial Tip Card */}
        <div 
          className={`bg-white rounded-2xl shadow-2xl p-8 border-2 border-indigo-200 transition-all duration-500 ${
            fadeIn ? 'opacity-100 transform scale-100' : 'opacity-0 transform scale-95'
          }`}
        >
          {/* Category Badge */}
          <div className="flex items-center justify-between mb-4">
            <span className="px-4 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-semibold">
              {currentTip.category}
            </span>
            <span className="text-sm text-gray-500">
              Tip {currentTipIndex + 1} of {financialTips.length}
            </span>
          </div>

          {/* Icon and Title */}
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <Icon className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800">
              {currentTip.title}
            </h3>
          </div>

          {/* Tip Content */}
          <p className="text-lg text-gray-700 leading-relaxed">
            {currentTip.tip}
          </p>

          {/* Progress Indicator */}
          <div className="mt-6">
            <div className="flex gap-1">
              {financialTips.map((_, index) => (
                <div
                  key={index}
                  className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                    index === currentTipIndex
                      ? 'bg-indigo-600'
                      : index < currentTipIndex
                      ? 'bg-indigo-300'
                      : 'bg-gray-200'
                  }`}
                ></div>
              ))}
            </div>
          </div>
        </div>

        {/* Fun Fact Footer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            💡 <span className="font-semibold">Did you know?</span> These tips can save you thousands of dollars over your lifetime!
          </p>
        </div>
      </div>
    </div>
  );
}
