import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from datetime import datetime
from typing import List, Dict

class VectorDB:
    def __init__(self, db_path='./data/vector_db'):
        """Initialize FAISS vector database for transactions"""
        self.db_path = db_path
        self.index_path = os.path.join(db_path, 'transactions.index')
        self.metadata_path = os.path.join(db_path, 'metadata.json')
        self.budget_path = os.path.join(db_path, 'budgets.json')
        
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize sentence transformer
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        
        # Load or create index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
        
        # Load or create budgets
        if os.path.exists(self.budget_path):
            with open(self.budget_path, 'r') as f:
                self.budgets = json.load(f)
        else:
            self.budgets = {}
        
        print(f"Vector DB initialized with {self.index.ntotal} transactions")
    
    def add_transaction(self, transaction: Dict):
        """Add a transaction to the vector database"""
        # Check if transaction already exists
        existing_ids = [t.get('id') for t in self.metadata]
        if transaction.get('id') in existing_ids:
            return  # Skip duplicates
        
        # Use pre-computed embedding if available, otherwise generate one
        if 'embedding' in transaction and transaction['embedding']:
            embedding = np.array([transaction['embedding']], dtype='float32')
        else:
            # Create text representation for embedding
            text = f"{transaction['merchant']} {transaction['category']} ${transaction['amount']} on {transaction['date']}"
            # Generate embedding
            embedding = self.encoder.encode([text])[0]
            embedding = np.array([embedding], dtype='float32')
        
        # Add to FAISS index
        self.index.add(embedding)
        
        # Store metadata
        transaction['added_at'] = datetime.now().isoformat()
        transaction['vector_id'] = self.index.ntotal - 1
        self.metadata.append(transaction)
        
        # Save to disk
        self._save()
        
        print(f"Added transaction: {transaction['merchant']} - ${transaction['amount']}")
    
    def search_transactions(self, query: str, k: int = 10):
        """Search for similar transactions using vector similarity"""
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.encoder.encode([query])[0]
        query_embedding = np.array([query_embedding], dtype='float32')
        
        # Search in FAISS
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)
        
        # Retrieve metadata for results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                
                # Include embedding metadata if available
                if 'embedding_metadata' in result:
                    result['search_metadata'] = result['embedding_metadata']
                
                results.append(result)
        
        return results
    
    def get_transactions_by_category(self, category: str):
        """Get all transactions in a specific classified category"""
        return [
            txn for txn in self.metadata 
            if txn.get('classified_category') == category
        ]
    
    def get_category_stats(self):
        """Get statistics for each category"""
        stats = {}
        for txn in self.metadata:
            category = txn.get('classified_category', 'Other')
            if category not in stats:
                stats[category] = {
                    'count': 0,
                    'total_amount': 0,
                    'avg_amount': 0
                }
            stats[category]['count'] += 1
            stats[category]['total_amount'] += abs(txn.get('amount', 0))
        
        # Calculate averages
        for category in stats:
            if stats[category]['count'] > 0:
                stats[category]['avg_amount'] = stats[category]['total_amount'] / stats[category]['count']
        
        return stats
    
    def get_all_transactions(self):
        """Get all transactions from the database"""
        return self.metadata
    
    def is_initialized(self):
        """Check if the database is initialized"""
        return self.index.ntotal > 0
    
    def _save(self):
        """Save index and metadata to disk"""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def auto_sync_webhook(self, transaction: Dict):
        """
        Webhook handler for automatic transaction syncing
        Call this method when Plaid sends a webhook notification
        """
        self.add_transaction(transaction)
        return {"status": "synced", "transaction_id": transaction.get('id')}
    
    def set_budget(self, user_id: str, month: str, amount: float):
        """Set or update budget for a specific user and month with Gemini embedding"""
        import google.generativeai as genai
        import os
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
        
        # Create budget key
        budget_key = f"{user_id}_{month}"
        
        # Generate embedding for budget using Gemini
        budget_text = f"Monthly budget for {month}: ${amount:.2f} USD. User: {user_id}. Budget limit set for financial tracking and spending control."
        
        try:
            # Use Gemini's embedding model
            result = genai.embed_content(
                model="models/embedding-001",
                content=budget_text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
        except Exception as e:
            print(f"Error creating Gemini embedding for budget: {e}")
            embedding = None
        
        # Store budget with embedding
        self.budgets[budget_key] = {
            'user_id': user_id,
            'month': month,
            'amount': amount,
            'embedding': embedding,
            'embedding_text': budget_text,
            'updated_at': datetime.now().isoformat()
        }
        
        # Save to disk
        self._save_budgets()
        
        print(f"Budget set for {user_id} ({month}): ${amount:.2f}")
        return self.budgets[budget_key]
    
    def get_budget(self, user_id: str, month: str) -> float:
        """Get budget for a specific user and month"""
        budget_key = f"{user_id}_{month}"
        budget_data = self.budgets.get(budget_key)
        
        if budget_data:
            return budget_data.get('amount', 0.0)
        return 0.0
    
    def _save_budgets(self):
        """Save budgets to disk"""
        with open(self.budget_path, 'w') as f:
            json.dump(self.budgets, f, indent=2)
