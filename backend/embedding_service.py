"""
Embedding service using Gemini API for transaction classification and vectorization
"""
import os
import google.generativeai as genai
from typing import List, Dict
import json
import numpy as np
from datetime import datetime

class EmbeddingService:
    def __init__(self):
        """Initialize Gemini API for embeddings"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Transaction categories
        self.categories = {
            'Food & Dining': ['restaurant', 'food', 'dining', 'cafe', 'coffee', 'pizza', 'burger', 'fast food'],
            'Groceries': ['grocery', 'supermarket', 'whole foods', 'trader joe', 'safeway', 'kroger'],
            'Transportation': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'parking', 'airline', 'flight'],
            'Shopping': ['amazon', 'walmart', 'target', 'store', 'retail', 'adidas', 'nike', 'clothing'],
            'Entertainment': ['netflix', 'spotify', 'movie', 'theater', 'game', 'entertainment', 'streaming'],
            'Bills & Utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'utility', 'cable'],
            'Health & Fitness': ['gym', 'fitness', 'pharmacy', 'doctor', 'medical', 'health', 'cvs', 'walgreens'],
            'EMI & Loans': ['emi', 'loan', 'payment', 'installment', 'mortgage', 'credit card payment'],
            'Credit Cards': ['credit card', 'cc payment', 'card payment'],
            'Income': ['salary', 'deposit', 'paycheck', 'income', 'refund', 'interest earned'],
            'Fun & Leisure': ['fun', 'hobby', 'recreation', 'vacation', 'travel', 'hotel'],
            'Other': []
        }
    
    def classify_transaction(self, transaction: Dict) -> str:
        """Classify transaction into a category using keyword matching"""
        merchant = transaction.get('merchant', '').lower()
        category = transaction.get('category', '').lower()
        amount = transaction.get('amount', 0)
        
        # Check for income (negative amounts)
        if amount < 0:
            return 'Income'
        
        # Check for EMI/Loan keywords
        if any(keyword in merchant for keyword in ['emi', 'loan', 'mortgage', 'payment']):
            if 'credit card' in merchant:
                return 'Credit Cards'
            return 'EMI & Loans'
        
        # Match against category keywords
        text = f"{merchant} {category}".lower()
        
        for cat_name, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text:
                    return cat_name
        
        return 'Other'
    
    def generate_embedding_text(self, transaction: Dict) -> str:
        """Generate comprehensive text representation for embedding with all transaction info"""
        merchant = transaction.get('merchant', 'Unknown')
        amount = transaction.get('amount', 0)
        date = transaction.get('date', '')
        category = transaction.get('category', 'Other')
        pending = transaction.get('pending', False)
        account_type = transaction.get('account_type', 'Unknown Account')
        account_id = transaction.get('account_id', 'unknown')
        txn_id = transaction.get('id', 'unknown')
        
        # Determine transaction type
        txn_type = "income/credit" if amount < 0 else "expense/debit"
        
        # Build comprehensive description
        text_parts = [
            f"Transaction ID: {txn_id}",
            f"Merchant: {merchant}",
            f"Amount: ${abs(amount):.2f}",
            f"Type: {txn_type}",
            f"Category: {category}",
            f"Date: {date}",
            f"Account: {account_type} ({account_id})",
            f"Status: {'Pending' if pending else 'Completed'}"
        ]
        
        # Add classified category if available
        if 'classified_category' in transaction:
            text_parts.append(f"Classified as: {transaction['classified_category']}")
        
        return " | ".join(text_parts)
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding using Gemini API"""
        try:
            # Use Gemini's embedding model
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error creating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    def process_transaction(self, transaction: Dict) -> Dict:
        """Process a single transaction: classify and create embedding with full info"""
        # Classify transaction first
        classified_category = self.classify_transaction(transaction)
        transaction['classified_category'] = classified_category
        
        # Generate comprehensive embedding text (includes all transaction info)
        embedding_text = self.generate_embedding_text(transaction)
        
        # Create embedding with all transaction information
        embedding = self.create_embedding(embedding_text)
        
        # Store everything in transaction
        transaction['embedding'] = embedding
        transaction['embedding_text'] = embedding_text
        transaction['processed_at'] = datetime.now().isoformat()
        
        # Add metadata for easier querying
        transaction['embedding_metadata'] = {
            'merchant': transaction.get('merchant'),
            'amount': transaction.get('amount'),
            'category': transaction.get('category'),
            'classified_category': classified_category,
            'date': transaction.get('date'),
            'account_type': transaction.get('account_type'),
            'is_income': transaction.get('amount', 0) < 0
        }
        
        print(f"Processed: {transaction['merchant']} (${abs(transaction.get('amount', 0)):.2f}) -> {classified_category}")
        
        return transaction
    
    def batch_process_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Process multiple transactions in batch"""
        processed = []
        
        print(f"\n🔄 Processing {len(transactions)} transactions...")
        
        for i, txn in enumerate(transactions):
            try:
                processed_txn = self.process_transaction(txn)
                processed.append(processed_txn)
                
                if (i + 1) % 50 == 0:
                    print(f"✓ Processed {i + 1}/{len(transactions)} transactions")
            except Exception as e:
                print(f"Error processing transaction {txn.get('id')}: {e}")
                processed.append(txn)
        
        print(f"✅ Completed processing {len(processed)} transactions\n")
        
        return processed
    
    def get_category_summary(self, transactions: List[Dict]) -> Dict:
        """Get summary of transactions by category"""
        summary = {}
        
        for txn in transactions:
            category = txn.get('classified_category', 'Other')
            amount = abs(txn.get('amount', 0))
            
            if category not in summary:
                summary[category] = {
                    'count': 0,
                    'total_amount': 0,
                    'transactions': []
                }
            
            summary[category]['count'] += 1
            summary[category]['total_amount'] += amount
            summary[category]['transactions'].append(txn['id'])
        
        return summary
