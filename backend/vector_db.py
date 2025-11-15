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
        
        print(f"Vector DB initialized with {self.index.ntotal} transactions")
    
    def add_transaction(self, transaction: Dict):
        """Add a transaction to the vector database"""
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
                results.append(result)
        
        return results
    
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
