'use client';

import { useState, useEffect } from 'react';
import { Bell, X, Check, AlertCircle, CreditCard, Zap } from 'lucide-react';

interface BillReminder {
  id: string;
  type: 'bill' | 'emi';
  category: string;
  name: string;
  amount: number;
  due_date: string;
  min_due: number;
  emi_details?: {
    current_emi: number;
    total_emis: number;
    remaining_emis: number;
  };
  status: string;
}

interface NotificationSettings {
  bills: boolean;
  emis: boolean;
  coupons: boolean;
  utilities: boolean;
  subscriptions: boolean;
  loans: boolean;
  insurance: boolean;
  rent: boolean;
}

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [reminders, setReminders] = useState<BillReminder[]>([]);
  const [activeNotification, setActiveNotification] = useState<BillReminder | null>(null);
  const [settings, setSettings] = useState<NotificationSettings>({
    bills: true,
    emis: true,
    coupons: true,
    utilities: true,
    subscriptions: true,
    loans: true,
    insurance: true,
    rent: true,
  });

  // Load reminders
  useEffect(() => {
    fetchReminders();
  }, []);

  // Show notification every minute
  useEffect(() => {
    const interval = setInterval(() => {
      showNextReminder();
    }, 60000); // Every 60 seconds

    // Show first notification after 5 seconds
    const timeout = setTimeout(() => {
      showNextReminder();
    }, 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [reminders, settings]);

  const fetchReminders = async () => {
    try {
      const response = await fetch('/api/reminders');
      const data = await response.json();
      setReminders(data);
    } catch (error) {
      console.error('Error fetching reminders:', error);
      // Use mock data for now
      setReminders([
        {
          id: 'bill_001',
          type: 'bill',
          category: 'utilities',
          name: 'Electric Bill',
          amount: 125.50,
          due_date: '2024-11-25',
          min_due: 25.00,
          status: 'pending'
        },
        {
          id: 'emi_001',
          type: 'emi',
          category: 'loan',
          name: 'Student Loan',
          amount: 350.00,
          due_date: '2024-11-15',
          min_due: 350.00,
          emi_details: {
            current_emi: 23,
            total_emis: 72,
            remaining_emis: 49
          },
          status: 'pending'
        }
      ]);
    }
  };

  const showNextReminder = () => {
    if (reminders.length === 0) return;

    // Filter reminders based on settings
    const filteredReminders = reminders.filter(reminder => {
      if (reminder.type === 'bill' && !settings.bills) return false;
      if (reminder.type === 'emi' && !settings.emis) return false;
      if (reminder.category === 'utilities' && !settings.utilities) return false;
      if (reminder.category === 'subscription' && !settings.subscriptions) return false;
      if (reminder.category === 'loan' && !settings.loans) return false;
      if (reminder.category === 'insurance' && !settings.insurance) return false;
      if (reminder.category === 'rent' && !settings.rent) return false;
      return true;
    });

    if (filteredReminders.length === 0) return;

    // Show random reminder
    const randomIndex = Math.floor(Math.random() * filteredReminders.length);
    setActiveNotification(filteredReminders[randomIndex]);
  };

  const dismissNotification = () => {
    setActiveNotification(null);
  };

  const getDaysUntilDue = (dueDate: string) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getUrgencyColor = (daysUntil: number) => {
    if (daysUntil < 0) return 'text-red-600 bg-red-50 border-red-200';
    if (daysUntil <= 3) return 'text-orange-600 bg-orange-50 border-orange-200';
    if (daysUntil <= 7) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-blue-600 bg-blue-50 border-blue-200';
  };

  const pendingCount = reminders.filter(r => r.status === 'pending').length;

  return (
    <>
      {/* Bell Icon Button - Bottom Left */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 left-6 w-16 h-16 glass border-green-500/30 rounded-full shadow-2xl hover:glow transform hover:scale-110 transition-all duration-300 flex items-center justify-center z-40 group"
      >
        <Bell className="w-8 h-8 text-green-500 group-hover:animate-bounce" />
        {pendingCount > 0 && (
          <span className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 text-black text-xs font-bold rounded-full flex items-center justify-center animate-pulse">
            {pendingCount}
          </span>
        )}
      </button>

      {/* Notification Popup - Top Left */}
      {activeNotification && (
        <div className="fixed top-6 left-6 w-96 glass glow rounded-xl shadow-2xl border-2 border-green-500/30 z-50 animate-slide-in-left">
          <div className={`p-4 rounded-t-xl border-b-2 border-green-500/30 bg-black/30`}>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-green-500" />
                <h3 className="font-bold text-lg text-green-500">Payment Reminder</h3>
              </div>
              <button
                onClick={dismissNotification}
                className="text-green-400 hover:text-green-300 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          <div className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-green-500 text-lg">{activeNotification.name}</h4>
              <span className="text-2xl font-bold text-green-500">${activeNotification.amount.toFixed(2)}</span>
            </div>

            {activeNotification.emi_details && (
              <div className="mb-3 p-3 glass rounded-lg border border-green-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <CreditCard className="w-4 h-4 text-green-500" />
                  <span className="text-sm font-semibold text-green-500">EMI Progress</span>
                </div>
                <div className="text-sm text-green-400">
                  {activeNotification.emi_details.current_emi} / {activeNotification.emi_details.total_emis} EMIs paid
                </div>
                <div className="w-full bg-green-900/30 rounded-full h-2 mt-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(activeNotification.emi_details.current_emi / activeNotification.emi_details.total_emis) * 100}%` }}
                  ></div>
                </div>
                <div className="text-xs text-green-400 mt-1">
                  {activeNotification.emi_details.remaining_emis} EMIs remaining
                </div>
              </div>
            )}

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-green-400">Due Date:</span>
                <span className="font-semibold text-green-500">{new Date(activeNotification.due_date).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-400">Days Until Due:</span>
                <span className={`font-semibold ${getDaysUntilDue(activeNotification.due_date) <= 3 ? 'text-red-500' : 'text-green-500'}`}>
                  {getDaysUntilDue(activeNotification.due_date)} days
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-400">Minimum Due:</span>
                <span className="font-semibold text-green-500">${activeNotification.min_due.toFixed(2)}</span>
              </div>
            </div>

            <button
              onClick={dismissNotification}
              className="w-full mt-4 px-4 py-2 glass border border-green-500/30 text-green-500 rounded-lg font-semibold hover:glow hover:bg-green-500 hover:text-black transform hover:scale-105 transition-all duration-200"
            >
              Mark as Seen
            </button>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-70 z-40 flex items-center justify-center" onClick={() => setIsOpen(false)}>
          <div className="glass glow rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden border border-green-500/30" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="bg-gradient-green p-6 text-black">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="w-8 h-8" />
                  <div>
                    <h2 className="text-2xl font-bold">Notification Settings</h2>
                    <p className="text-sm opacity-90">Manage your payment reminders</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-all"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
              {/* Notification Types */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Notification Types</h3>
                <div className="space-y-3">
                  <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <AlertCircle className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-800">Bill Reminders</div>
                        <div className="text-sm text-gray-600">Get notified about upcoming bills</div>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.bills}
                      onChange={(e) => setSettings({...settings, bills: e.target.checked})}
                      className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  </label>

                  <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                        <CreditCard className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-800">EMI Reminders</div>
                        <div className="text-sm text-gray-600">Track your loan EMI payments</div>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.emis}
                      onChange={(e) => setSettings({...settings, emis: e.target.checked})}
                      className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
                    />
                  </label>

                  <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <Zap className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-800">Coupon Alerts</div>
                        <div className="text-sm text-gray-600">New coupons and deals</div>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.coupons}
                      onChange={(e) => setSettings({...settings, coupons: e.target.checked})}
                      className="w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
                    />
                  </label>
                </div>
              </div>

              {/* Categories */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Categories</h3>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries({
                    utilities: 'Utilities',
                    subscriptions: 'Subscriptions',
                    loans: 'Loans',
                    insurance: 'Insurance',
                    rent: 'Rent'
                  }).map(([key, label]) => (
                    <label key={key} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings[key as keyof NotificationSettings]}
                        onChange={(e) => setSettings({...settings, [key]: e.target.checked})}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-700">{label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Upcoming Reminders */}
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Upcoming Payments ({reminders.length})</h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {reminders.slice(0, 5).map((reminder) => {
                    const daysUntil = getDaysUntilDue(reminder.due_date);
                    return (
                      <div key={reminder.id} className={`p-3 rounded-lg border-2 ${getUrgencyColor(daysUntil)}`}>
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-semibold">{reminder.name}</div>
                            <div className="text-sm">Due: {new Date(reminder.due_date).toLocaleDateString()} ({daysUntil} days)</div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold">${reminder.amount.toFixed(2)}</div>
                            {reminder.emi_details && (
                              <div className="text-xs">{reminder.emi_details.current_emi}/{reminder.emi_details.total_emis} EMIs</div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes slide-in-left {
          from {
            transform: translateX(-100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in-left {
          animation: slide-in-left 0.3s ease-out;
        }
      `}</style>
    </>
  );
}
