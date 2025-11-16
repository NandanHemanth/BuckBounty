'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, Target, Edit2, Check, X } from 'lucide-react';

interface DashboardStats {
  summary: {
    total_transactions: number;
    total_spent: number;
    avg_transaction: number;
    top_category: string;
    budget?: number;
  };
  category_comparison: Array<{
    category: string;
    current_amount: number;
    previous_amount: number;
    current_count: number;
    previous_count: number;
  }>;
  current_month: {
    transactions: number;
    total: number;
  };
  previous_month: {
    transactions: number;
    total: number;
  };
}

const COLORS = [
  '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
  '#06b6d4', '#6366f1', '#f97316', '#14b8a6', '#a855f7'
];

export default function Dashboard({ userId, refreshTrigger }: { userId: string; refreshTrigger?: number }) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChart, setSelectedChart] = useState<string | null>(null);
  const [budget, setBudget] = useState<number>(0);
  const [isEditingBudget, setIsEditingBudget] = useState(false);
  const [budgetInput, setBudgetInput] = useState<string>('');

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`http://localhost:8000/api/dashboard/stats?user_id=${userId}`);
      setStats(response.data);
      setBudget(response.data.summary.budget || 0);
      setBudgetInput((response.data.summary.budget || 0).toFixed(2));
    } catch (err: any) {
      console.error('Error fetching dashboard stats:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard stats');
    } finally {
      setLoading(false);
    }
  };

  const saveBudget = async () => {
    try {
      const amount = parseFloat(budgetInput);
      if (isNaN(amount) || amount < 0) {
        alert('Please enter a valid budget amount');
        return;
      }

      await axios.post(`http://localhost:8000/api/budget/set?user_id=${userId}&amount=${amount}`);
      setBudget(amount);
      setIsEditingBudget(false);
      fetchStats();
    } catch (err: any) {
      console.error('Error saving budget:', err);
      alert('Failed to save budget');
    }
  };

  useEffect(() => {
    fetchStats();
  }, [userId]);

  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      console.log('Dashboard refreshing due to new transaction');
      fetchStats();
    }
  }, [refreshTrigger]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <p className="text-sm text-red-600 mb-3">{error}</p>
        <button 
          onClick={fetchStats}
          className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all duration-200 inline-flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Retry
        </button>
      </div>
    );
  }

  if (!stats) return null;

  const { summary, category_comparison } = stats;

  const radarData = category_comparison.slice(0, 6).map(cat => ({
    category: cat.category.length > 15 ? cat.category.substring(0, 15) + '...' : cat.category,
    current: Math.round(cat.current_amount),
    previous: Math.round(cat.previous_amount)
  }));

  const pieData = category_comparison
    .filter(cat => cat.current_amount > 0)
    .map(cat => ({
      name: cat.category,
      value: Math.round(cat.current_amount),
      count: cat.current_count
    }));

  const spendingChange = stats.previous_month.total > 0
    ? ((stats.current_month.total - stats.previous_month.total) / stats.previous_month.total) * 100
    : 0;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatCard
          icon={<ShoppingCart className="w-4 h-4" />}
          label="Transactions"
          value={summary.total_transactions.toString()}
          iconBg="bg-blue-50"
          iconColor="text-blue-600"
        />
        <StatCard
          icon={<DollarSign className="w-4 h-4" />}
          label="Total Spent"
          value={`$${summary.total_spent.toFixed(2)}`}
          iconBg="bg-green-50"
          iconColor="text-green-600"
          trend={spendingChange}
        />
        <StatCard
          icon={<TrendingUp className="w-4 h-4" />}
          label="Avg Transaction"
          value={`$${summary.avg_transaction.toFixed(2)}`}
          iconBg="bg-purple-50"
          iconColor="text-purple-600"
        />
        <StatCard
          icon={<span className="text-lg">🏆</span>}
          label="Top Category"
          value={summary.top_category}
          iconBg="bg-orange-50"
          iconColor="text-orange-600"
        />
        <BudgetCard
          budget={budget}
          spent={summary.total_spent}
          isEditing={isEditingBudget}
          budgetInput={budgetInput}
          onEdit={() => setIsEditingBudget(true)}
          onSave={saveBudget}
          onCancel={() => {
            setIsEditingBudget(false);
            setBudgetInput(budget.toFixed(2));
          }}
          onChange={(value) => setBudgetInput(value)}
        />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <ChartCard
          title="Current vs Previous Month"
          subtitle="Compare spending across categories"
          isExpanded={selectedChart === 'radar'}
          onToggle={() => setSelectedChart(selectedChart === 'radar' ? null : 'radar')}
        >
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis 
                dataKey="category" 
                tick={{ fill: '#6b7280', fontSize: 12 }}
              />
              <PolarRadiusAxis angle={90} domain={[0, 'auto']} tick={{ fill: '#6b7280' }} />
              <Radar
                name="Current Month"
                dataKey="current"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.6}
              />
              <Radar
                name="Previous Month"
                dataKey="previous"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.3}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '8px'
                }}
                formatter={(value: any) => `$${value}`}
              />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Spending by Category"
          subtitle="Current month breakdown"
          isExpanded={selectedChart === 'pie'}
          onToggle={() => setSelectedChart(selectedChart === 'pie' ? null : 'pie')}
        >
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => 
                  percent > 0.05 ? `${name} ${(percent * 100).toFixed(0)}%` : ''
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '8px'
                }}
                formatter={(value: any, name: any, props: any) => [
                  `$${value} (${props.payload.count} transactions)`,
                  name
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Category Details</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Category</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">Current</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">Previous</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">Change</th>
              </tr>
            </thead>
            <tbody>
              {category_comparison.slice(0, 8).map((cat, idx) => {
                const change = cat.previous_amount > 0
                  ? ((cat.current_amount - cat.previous_amount) / cat.previous_amount) * 100
                  : cat.current_amount > 0 ? 100 : 0;
                
                return (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50 transition">
                    <td className="py-3 px-4 text-sm text-gray-800">{cat.category}</td>
                    <td className="py-3 px-4 text-sm text-right text-gray-800">
                      ${cat.current_amount.toFixed(2)}
                      <span className="text-xs text-gray-500 ml-1">({cat.current_count})</span>
                    </td>
                    <td className="py-3 px-4 text-sm text-right text-gray-600">
                      ${cat.previous_amount.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-sm text-right">
                      {change !== 0 && (
                        <span className={`inline-flex items-center ${
                          change > 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {change > 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                          {Math.abs(change).toFixed(1)}%
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ 
  icon, 
  label, 
  value, 
  iconBg, 
  iconColor,
  trend 
}: { 
  icon: React.ReactNode; 
  label: string; 
  value: string; 
  iconBg: string;
  iconColor: string;
  trend?: number;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-3.5 hover:shadow-md transition-all duration-200 border border-gray-100">
      <div className="flex items-start justify-between mb-2">
        <div className={`${iconBg} ${iconColor} p-2 rounded-lg`}>
          {icon}
        </div>
        {trend !== undefined && trend !== 0 && (
          <div className={`flex items-center text-[10px] font-medium px-1.5 py-0.5 rounded ${
            trend > 0 ? 'text-red-600 bg-red-50' : 'text-green-600 bg-green-50'
          }`}>
            {trend > 0 ? <TrendingUp className="w-2.5 h-2.5 mr-0.5" /> : <TrendingDown className="w-2.5 h-2.5 mr-0.5" />}
            {Math.abs(trend).toFixed(1)}%
          </div>
        )}
      </div>
      <div className="text-[10px] text-gray-500 mb-0.5 uppercase tracking-wide">{label}</div>
      <div className="text-lg font-bold text-gray-800 truncate">{value}</div>
    </div>
  );
}

function BudgetCard({
  budget,
  spent,
  isEditing,
  budgetInput,
  onEdit,
  onSave,
  onCancel,
  onChange
}: {
  budget: number;
  spent: number;
  isEditing: boolean;
  budgetInput: string;
  onEdit: () => void;
  onSave: () => void;
  onCancel: () => void;
  onChange: (value: string) => void;
}) {
  const percentage = budget > 0 ? (spent / budget) * 100 : 0;
  const isOverBudget = percentage > 100;

  return (
    <div className="bg-white rounded-xl shadow-sm p-3.5 hover:shadow-md transition-all duration-200 border border-gray-100">
      <div className="flex items-start justify-between mb-2">
        <div className={`bg-indigo-50 text-indigo-600 p-2 rounded-lg`}>
          <Target className="w-4 h-4" />
        </div>
        {!isEditing && (
          <button
            onClick={onEdit}
            className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <Edit2 className="w-3 h-3" />
          </button>
        )}
      </div>
      <div className="text-[10px] text-gray-500 mb-0.5 uppercase tracking-wide">Budget</div>
      
      {isEditing ? (
        <div className="flex items-center gap-1 mt-1">
          <div className="relative flex-1">
            <span className="absolute left-2 top-1/2 -translate-y-1/2 text-sm text-gray-500">$</span>
            <input
              type="number"
              step="0.01"
              value={budgetInput}
              onChange={(e) => onChange(e.target.value)}
              className="w-full pl-5 pr-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="0.00"
              autoFocus
            />
          </div>
          <button
            onClick={onSave}
            className="p-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition-colors"
          >
            <Check className="w-3 h-3" />
          </button>
          <button
            onClick={onCancel}
            className="p-1 bg-gray-200 text-gray-600 rounded hover:bg-gray-300 transition-colors"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      ) : (
        <>
          <div className="text-lg font-bold text-gray-800 truncate">
            ${budget > 0 ? budget.toFixed(2) : '0.00'}
          </div>
          {budget > 0 && (
            <div className="mt-2">
              <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                <span>${spent.toFixed(2)} spent</span>
                <span className={isOverBudget ? 'text-red-600 font-medium' : ''}>
                  {percentage.toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    isOverBudget ? 'bg-red-500' : 'bg-indigo-600'
                  }`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ChartCard({ 
  title, 
  subtitle, 
  children, 
  isExpanded, 
  onToggle 
}: { 
  title: string; 
  subtitle: string; 
  children: React.ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div 
      className={`bg-white rounded-xl shadow-lg p-6 transition-all duration-300 hover:shadow-xl ${
        isExpanded ? 'fixed inset-8 z-50 overflow-auto' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        </div>
        <button 
          className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-all duration-200"
          onClick={(e) => {
            e.stopPropagation();
            onToggle();
          }}
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          {isExpanded ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          )}
        </button>
      </div>
      <div onClick={(e) => isExpanded && e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}
