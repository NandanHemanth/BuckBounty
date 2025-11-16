'use client';

import { useState } from 'react';
import { X, Upload, Loader2, Check } from 'lucide-react';
import axios from 'axios';

interface BillItem {
  name: string;
  quantity: number;
  price: number;
  selected: boolean;
  splitBy: number;
}

interface ParsedBill {
  items: BillItem[];
  subtotal: number;
  tax: number;
  tip: number;
  total: number;
}

interface BillSplitModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  onTransactionAdded: () => void;
}

export default function BillSplitModal({ isOpen, onClose, userId, onTransactionAdded }: BillSplitModalProps) {
  const [step, setStep] = useState<'upload' | 'review' | 'payment'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [parsedBill, setParsedBill] = useState<ParsedBill | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:8000/api/bill/parse', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setParsedBill(response.data);
      setStep('review');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to parse bill');
    } finally {
      setLoading(false);
    }
  };

  const toggleItemSelection = (index: number) => {
    if (!parsedBill) return;
    const newItems = [...parsedBill.items];
    newItems[index].selected = !newItems[index].selected;
    setParsedBill({ ...parsedBill, items: newItems });
  };

  const updateSplitBy = (index: number, value: number) => {
    if (!parsedBill) return;
    const newItems = [...parsedBill.items];
    newItems[index].splitBy = value;
    setParsedBill({ ...parsedBill, items: newItems });
  };

  const calculateTotal = () => {
    if (!parsedBill) return 0;
    
    const selectedItems = parsedBill.items.filter(item => item.selected);
    const itemsTotal = selectedItems.reduce((sum, item) => 
      sum + (item.price * item.quantity / item.splitBy), 0
    );
    
    const totalBeforeTaxTip = parsedBill.items.reduce((sum, item) => 
      sum + (item.price * item.quantity), 0
    );
    
    const taxProportion = totalBeforeTaxTip > 0 ? itemsTotal / totalBeforeTaxTip : 0;
    const myTax = parsedBill.tax * taxProportion;
    const myTip = parsedBill.tip * taxProportion;
    
    return itemsTotal + myTax + myTip;
  };

  const handlePayment = async () => {
    setLoading(true);
    setError(null);

    try {
      const total = calculateTotal();
      
      // Create Stripe checkout session
      const response = await axios.post('http://localhost:8000/api/bill/create-payment', {
        amount: total,
        user_id: userId,
        bill_items: parsedBill?.items.filter(item => item.selected)
      });

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create payment');
      setLoading(false);
    }
  };

  const handleSkipPayment = async () => {
    setLoading(true);
    setError(null);

    try {
      const total = calculateTotal();
      
      // Add transaction without payment
      await axios.post('http://localhost:8000/api/bill/add-transaction', {
        amount: total,
        user_id: userId,
        bill_items: parsedBill?.items.filter(item => item.selected),
        paid: false
      });

      onTransactionAdded();
      handleClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add transaction');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setStep('upload');
    setFile(null);
    setPreview(null);
    setParsedBill(null);
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Split Bill</h2>
            <p className="text-sm text-gray-500 mt-1">
              {step === 'upload' && 'Upload your bill to get started'}
              {step === 'review' && 'Select items and split quantities'}
              {step === 'payment' && 'Complete payment'}
            </p>
          </div>
          <button
            onClick={handleClose}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
              {error}
            </div>
          )}

          {step === 'upload' && (
            <div className="space-y-6">
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-indigo-400 transition-colors">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="bill-upload"
                />
                <label htmlFor="bill-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    Click to upload bill image
                  </p>
                  <p className="text-sm text-gray-500">
                    PNG, JPG up to 10MB
                  </p>
                </label>
              </div>

              {preview && (
                <div className="space-y-4">
                  <img 
                    src={preview} 
                    alt="Bill preview" 
                    className="w-full max-h-96 object-contain rounded-lg border border-gray-200"
                  />
                  <button
                    onClick={handleUpload}
                    disabled={loading}
                    className="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Parsing bill...
                      </>
                    ) : (
                      'Parse Bill'
                    )}
                  </button>
                </div>
              )}
            </div>
          )}

          {step === 'review' && parsedBill && (
            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-800">Bill Items</h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {parsedBill.items.map((item, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          item.selected
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-gray-200 bg-white'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={item.selected}
                            onChange={() => toggleItemSelection(index)}
                            className="mt-1 w-4 h-4 text-indigo-600 rounded"
                          />
                          <div className="flex-1">
                            <div className="flex justify-between items-start mb-2">
                              <span className="font-medium text-gray-800">{item.name}</span>
                              <span className="text-gray-600">${item.price.toFixed(2)}</span>
                            </div>
                            <div className="flex items-center gap-4 text-sm">
                              <span className="text-gray-500">Qty: {item.quantity}</span>
                              {item.selected && (
                                <div className="flex items-center gap-2">
                                  <label className="text-gray-600">Split by:</label>
                                  <select
                                    value={item.splitBy}
                                    onChange={(e) => updateSplitBy(index, parseInt(e.target.value))}
                                    className="px-2 py-1 border border-gray-300 rounded text-sm"
                                  >
                                    {[1, 2, 3, 4, 5].map(n => (
                                      <option key={n} value={n}>{n}</option>
                                    ))}
                                  </select>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-800">Summary</h3>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Subtotal</span>
                      <span className="text-gray-800">${parsedBill.subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Tax</span>
                      <span className="text-gray-800">${parsedBill.tax.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Tip</span>
                      <span className="text-gray-800">${parsedBill.tip.toFixed(2)}</span>
                    </div>
                    <div className="border-t border-gray-300 pt-3">
                      <div className="flex justify-between font-semibold">
                        <span className="text-gray-800">Bill Total</span>
                        <span className="text-gray-800">${parsedBill.total.toFixed(2)}</span>
                      </div>
                    </div>
                    <div className="border-t-2 border-indigo-500 pt-3 mt-3">
                      <div className="flex justify-between font-bold text-lg">
                        <span className="text-indigo-600">Your Share</span>
                        <span className="text-indigo-600">${calculateTotal().toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep('upload')}
                  className="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep('payment')}
                  disabled={!parsedBill.items.some(item => item.selected)}
                  className="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continue to Payment
                </button>
              </div>
            </div>
          )}

          {step === 'payment' && (
            <div className="space-y-6">
              <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-6 text-center">
                <div className="text-4xl mb-4">💳</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                  ${calculateTotal().toFixed(2)}
                </h3>
                <p className="text-gray-600">Your share of the bill</p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={handlePayment}
                  disabled={loading}
                  className="w-full py-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Check className="w-5 h-5" />
                      Pay with Stripe
                    </>
                  )}
                </button>

                <button
                  onClick={handleSkipPayment}
                  disabled={loading}
                  className="w-full py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Skip Payment & Add to Dashboard
                </button>

                <button
                  onClick={handleClose}
                  className="w-full py-3 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
