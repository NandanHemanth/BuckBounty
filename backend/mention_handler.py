"""
Handler for @ mentions in user messages
Analyzes transaction data and provides savings suggestions
"""

import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

class MentionHandler:
    def __init__(self, vector_db=None, rag_service=None):
        self.vector_db = vector_db
        self.rag_service = rag_service
        self.coupons_path = Path("backend/data/coupons/all_coupons.json")
        self.coupons = self._load_coupons()
    
    def _load_coupons(self) -> List[Dict[str, Any]]:
        """Load all coupons"""
        try:
            if self.coupons_path.exists():
                with open(self.coupons_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading coupons: {e}")
            return []
    
    def extract_mentions(self, message: str) -> List[str]:
        """Extract @ mentions from message"""
        # Match @word patterns
        mentions = re.findall(r'@(\w+)', message)
        return [m.lower() for m in mentions]
    
    def find_merchant_transactions(self, merchant_name: str) -> List[Dict[str, Any]]:
        """Find all transactions for a specific merchant"""
        merchant_lower = merchant_name.lower()
        matching_transactions = []
        
        print(f"\n🔍 Searching for merchant: {merchant_name}")
        
        # Primary Strategy: Direct metadata scan (most reliable)
        if self.vector_db and hasattr(self.vector_db, 'metadata'):
            print(f"   Scanning {len(self.vector_db.metadata)} transactions in vector_db...")
            for tx in self.vector_db.metadata:
                merchant = tx.get('merchant', '').lower()
                # Flexible matching: check if merchant name contains the search term or vice versa
                if merchant_lower in merchant or merchant in merchant_lower:
                    matching_transactions.append(tx)
                    print(f"   ✓ Found: {tx.get('merchant')} - ${tx.get('amount')} on {tx.get('date')}")
        
        # Fallback: Check RAG service if available
        if not matching_transactions and self.rag_service:
            print(f"   Checking RAG service...")
            try:
                # Check current month transactions
                for tx in self.rag_service.get_current_month_transactions():
                    merchant = tx.get('merchant', '').lower()
                    if merchant_lower in merchant or merchant in merchant_lower:
                        matching_transactions.append(tx)
                        print(f"   ✓ Found in FLAT: {tx.get('merchant')} - ${tx.get('amount')}")
                
                # Check historical transactions
                for tx in self.rag_service.get_historical_transactions():
                    merchant = tx.get('merchant', '').lower()
                    if merchant_lower in merchant or merchant in merchant_lower:
                        if not any(t.get('id') == tx.get('id') for t in matching_transactions):
                            matching_transactions.append(tx)
                            print(f"   ✓ Found in HNSW: {tx.get('merchant')} - ${tx.get('amount')}")
            except Exception as e:
                print(f"   ⚠️ RAG service error: {e}")
        
        print(f"   📊 Total found: {len(matching_transactions)} transactions for {merchant_name}\n")
        return matching_transactions
    
    def find_merchant_coupons(self, merchant_name: str) -> List[Dict[str, Any]]:
        """Find coupons for a specific merchant"""
        merchant_lower = merchant_name.lower()
        matching_coupons = []
        
        for coupon in self.coupons:
            coupon_merchant = coupon.get('merchant', '').lower()
            if merchant_lower in coupon_merchant or coupon_merchant in merchant_lower:
                # Check if coupon is not expired
                expiry = coupon.get('expiry_date')
                if expiry:
                    try:
                        expiry_date = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                        if expiry_date > datetime.now():
                            matching_coupons.append(coupon)
                    except:
                        matching_coupons.append(coupon)
                else:
                    matching_coupons.append(coupon)
        
        return matching_coupons
    
    def generate_savings_suggestions(self, merchant_name: str, transactions: List[Dict], coupons: List[Dict]) -> List[Dict[str, Any]]:
        """Generate savings suggestions based on merchant and transaction data"""
        suggestions = []
        
        # Add coupon suggestions
        for coupon in coupons[:3]:  # Limit to top 3 coupons
            suggestions.append({
                "type": "coupon",
                "merchant": coupon.get('merchant'),
                "code": coupon.get('code'),
                "description": coupon.get('description'),
                "discount_value": coupon.get('discount_value'),
                "expiry_date": coupon.get('expiry_date')
            })
        
        # Add alternative suggestions based on merchant type
        merchant_lower = merchant_name.lower()
        
        if any(keyword in merchant_lower for keyword in ['uber', 'lyft', 'taxi', 'ride']):
            suggestions.append({
                "type": "alternative",
                "title": "Public Transportation",
                "suggestion": "Consider taking the subway or bus instead",
                "estimated_savings": "$10-15 per trip",
                "environmental_benefit": "Reduces carbon footprint by 45%"
            })
            suggestions.append({
                "type": "alternative",
                "title": "Bike Share",
                "suggestion": "Use bike-sharing services for short distances",
                "estimated_savings": "$5-10 per trip",
                "health_benefit": "Great exercise and faster in traffic"
            })
        
        elif any(keyword in merchant_lower for keyword in ['starbucks', 'coffee', 'cafe']):
            suggestions.append({
                "type": "alternative",
                "title": "Home Brewing",
                "suggestion": "Brew coffee at home and bring it in a thermos",
                "estimated_savings": "$100-150 per month",
                "tip": "Invest in a good coffee maker - pays for itself in 2 months"
            })
        
        elif any(keyword in merchant_lower for keyword in ['doordash', 'ubereats', 'grubhub', 'delivery']):
            suggestions.append({
                "type": "alternative",
                "title": "Meal Prep",
                "suggestion": "Cook meals at home and meal prep for the week",
                "estimated_savings": "$200-300 per month",
                "tip": "Batch cooking on Sundays saves time and money"
            })
            suggestions.append({
                "type": "alternative",
                "title": "Pickup Instead of Delivery",
                "suggestion": "Pick up food yourself to avoid delivery fees",
                "estimated_savings": "$5-10 per order"
            })
        
        elif any(keyword in merchant_lower for keyword in ['amazon', 'shopping', 'retail']):
            suggestions.append({
                "type": "alternative",
                "title": "Wait for Sales",
                "suggestion": "Add items to wishlist and wait for Prime Day or Black Friday",
                "estimated_savings": "20-50% off regular prices"
            })
            suggestions.append({
                "type": "alternative",
                "title": "Buy Used or Refurbished",
                "suggestion": "Check Amazon Warehouse or eBay for like-new items",
                "estimated_savings": "30-60% off new prices"
            })
        
        return suggestions
    
    def analyze_merchant_spending(self, merchant_name: str, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze spending patterns for a merchant"""
        if not transactions:
            return {
                "merchant": merchant_name,
                "total_spent": 0,
                "transaction_count": 0,
                "avg_per_transaction": 0,
                "monthly_average": 0,
                "message": f"No transactions found for {merchant_name}. This could mean you haven't spent money there recently, or the account isn't linked yet."
            }
        
        # Handle both positive and negative amounts (debits vs credits)
        total = sum(abs(tx.get('amount', 0)) for tx in transactions)
        count = len(transactions)
        avg = total / count if count > 0 else 0
        
        # Calculate monthly average (assuming last 30 days)
        recent_transactions = [
            tx for tx in transactions
            if self._is_recent(tx.get('date'), days=30)
        ]
        monthly_total = sum(abs(tx.get('amount', 0)) for tx in recent_transactions)
        
        # Get date range
        dates = [tx.get('date') for tx in transactions if tx.get('date')]
        date_range = ""
        if dates:
            dates.sort()
            date_range = f"{dates[0]} to {dates[-1]}"
        
        return {
            "merchant": merchant_name,
            "total_spent": round(total, 2),
            "transaction_count": count,
            "avg_per_transaction": round(avg, 2),
            "monthly_average": round(monthly_total, 2),
            "recent_transaction_count": len(recent_transactions),
            "date_range": date_range,
            "message": f"Found {count} transactions totaling ${round(total, 2)}"
        }
    
    def _is_recent(self, date_str: Optional[str], days: int = 30) -> bool:
        """Check if a date is within the last N days"""
        if not date_str:
            return False
        try:
            tx_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            cutoff = datetime.now() - timedelta(days=days)
            return tx_date > cutoff
        except:
            return False
    
    def process_mentions(self, message: str) -> Dict[str, Any]:
        """Process all @ mentions in a message and return analysis"""
        mentions = self.extract_mentions(message)
        
        if not mentions:
            return {
                "has_mentions": False,
                "mentions": []
            }
        
        results = []
        for merchant in mentions:
            transactions = self.find_merchant_transactions(merchant)
            coupons = self.find_merchant_coupons(merchant)
            spending_analysis = self.analyze_merchant_spending(merchant, transactions)
            suggestions = self.generate_savings_suggestions(merchant, transactions, coupons)
            
            results.append({
                "merchant": merchant,
                "spending_analysis": spending_analysis,
                "coupons": coupons,
                "savings_suggestions": suggestions
            })
        
        return {
            "has_mentions": True,
            "mentions": results
        }
