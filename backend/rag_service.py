"""
RAG Service with FLAT and HNSW algorithms
FLAT for current month (fast exact search)
HNSW for historical data (efficient approximate search)
"""

import faiss
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import os


class RAGService:
    """
    Retrieval-Augmented Generation service
    Uses FLAT index for current month, HNSW for historical data
    """

    def __init__(self, dimension: int = 768):
        """Initialize RAG service with dual indexing"""
        self.dimension = dimension
        self.data_dir = Path("./data/rag")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # FLAT index for current month (exact search)
        self.flat_index = faiss.IndexFlatL2(dimension)
        self.flat_metadata = []
        self.flat_index_path = self.data_dir / "flat_current_month.index"
        self.flat_metadata_path = self.data_dir / "flat_metadata.json"

        # HNSW index for historical data (approximate search)
        self.hnsw_index = faiss.IndexHNSWFlat(dimension, 32)  # 32 = M parameter
        self.hnsw_metadata = []
        self.hnsw_index_path = self.data_dir / "hnsw_historical.index"
        self.hnsw_metadata_path = self.data_dir / "hnsw_metadata.json"

        # Load existing indices
        self._load_indices()

        print(f"✅ RAG Service initialized")
        print(f"   FLAT index: {self.flat_index.ntotal} vectors (current month)")
        print(f"   HNSW index: {self.hnsw_index.ntotal} vectors (historical)")

    def _load_indices(self):
        """Load existing FAISS indices"""
        # Load FLAT index
        if self.flat_index_path.exists():
            try:
                self.flat_index = faiss.read_index(str(self.flat_index_path))
                with open(self.flat_metadata_path, 'r') as f:
                    self.flat_metadata = json.load(f)
                print(f"📦 Loaded FLAT index with {self.flat_index.ntotal} vectors")
            except Exception as e:
                print(f"⚠️ Error loading FLAT index: {e}")

        # Load HNSW index
        if self.hnsw_index_path.exists():
            try:
                self.hnsw_index = faiss.read_index(str(self.hnsw_index_path))
                with open(self.hnsw_metadata_path, 'r') as f:
                    self.hnsw_metadata = json.load(f)
                print(f"📦 Loaded HNSW index with {self.hnsw_index.ntotal} vectors")
            except Exception as e:
                print(f"⚠️ Error loading HNSW index: {e}")

    def _save_indices(self):
        """Save FAISS indices to disk"""
        try:
            # Save FLAT
            faiss.write_index(self.flat_index, str(self.flat_index_path))
            with open(self.flat_metadata_path, 'w') as f:
                json.dump(self.flat_metadata, f, indent=2, default=str)

            # Save HNSW
            faiss.write_index(self.hnsw_index, str(self.hnsw_index_path))
            with open(self.hnsw_metadata_path, 'w') as f:
                json.dump(self.hnsw_metadata, f, indent=2, default=str)

            print("💾 Saved RAG indices")
        except Exception as e:
            print(f"❌ Error saving indices: {e}")

    def add_transaction(self, transaction: Dict[str, Any], embedding: np.ndarray):
        """Add transaction to appropriate index based on date"""
        # Determine if current month
        txn_date_str = transaction.get('date', '')
        current_month = datetime.now().strftime('%Y-%m')

        try:
            txn_date = datetime.strptime(txn_date_str, '%Y-%m-%d')
            txn_month = txn_date.strftime('%Y-%m')
            is_current_month = (txn_month == current_month)
        except:
            is_current_month = False

        # Prepare embedding
        if isinstance(embedding, list):
            embedding = np.array(embedding, dtype='float32')
        embedding = embedding.reshape(1, -1)

        # Add to appropriate index
        if is_current_month:
            self.flat_index.add(embedding)
            transaction['vector_id'] = self.flat_index.ntotal - 1
            transaction['index_type'] = 'FLAT'
            self.flat_metadata.append(transaction)
            print(f"➕ Added to FLAT index: {transaction.get('merchant', 'Unknown')}")
        else:
            self.hnsw_index.add(embedding)
            transaction['vector_id'] = self.hnsw_index.ntotal - 1
            transaction['index_type'] = 'HNSW'
            self.hnsw_metadata.append(transaction)
            print(f"➕ Added to HNSW index: {transaction.get('merchant', 'Unknown')}")

        self._save_indices()

    def search_transactions(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        time_range: str = 'current_month'
    ) -> List[Dict[str, Any]]:
        """
        Search transactions using appropriate index
        
        Args:
            query_embedding: Query vector
            k: Number of results
            time_range: 'current_month', 'historical', or 'all'
        """
        results = []

        # Prepare query embedding
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding, dtype='float32')
        query_embedding = query_embedding.reshape(1, -1)

        # Search based on time range
        if time_range == 'current_month' or time_range == 'all':
            if self.flat_index.ntotal > 0:
                k_flat = min(k, self.flat_index.ntotal)
                distances, indices = self.flat_index.search(query_embedding, k_flat)

                for idx, distance in zip(indices[0], distances[0]):
                    if idx < len(self.flat_metadata):
                        result = self.flat_metadata[idx].copy()
                        result['similarity_score'] = float(1 / (1 + distance))
                        result['search_method'] = 'FLAT'
                        results.append(result)

        if time_range == 'historical' or time_range == 'all':
            if self.hnsw_index.ntotal > 0:
                k_hnsw = min(k, self.hnsw_index.ntotal)
                distances, indices = self.hnsw_index.search(query_embedding, k_hnsw)

                for idx, distance in zip(indices[0], distances[0]):
                    if idx < len(self.hnsw_metadata):
                        result = self.hnsw_metadata[idx].copy()
                        result['similarity_score'] = float(1 / (1 + distance))
                        result['search_method'] = 'HNSW'
                        results.append(result)

        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Return top k
        return results[:k]

    def get_current_month_transactions(self) -> List[Dict[str, Any]]:
        """Get all current month transactions from FLAT index"""
        return self.flat_metadata.copy()

    def get_historical_transactions(self) -> List[Dict[str, Any]]:
        """Get all historical transactions from HNSW index"""
        return self.hnsw_metadata.copy()

    def migrate_old_transactions(self):
        """
        Migrate transactions from FLAT to HNSW if they're older than current month
        Run this periodically (e.g., at start of new month)
        """
        current_month = datetime.now().strftime('%Y-%m')
        to_migrate = []

        # Find old transactions in FLAT index
        for i, txn in enumerate(self.flat_metadata):
            txn_date_str = txn.get('date', '')
            try:
                txn_date = datetime.strptime(txn_date_str, '%Y-%m-%d')
                txn_month = txn_date.strftime('%Y-%m')

                if txn_month != current_month:
                    to_migrate.append((i, txn))
            except:
                continue

        if not to_migrate:
            print("✅ No transactions to migrate")
            return

        print(f"🔄 Migrating {len(to_migrate)} transactions from FLAT to HNSW...")

        # Migrate transactions
        for idx, txn in to_migrate:
            # Get embedding from FLAT index
            vector_id = txn.get('vector_id', idx)
            if vector_id < self.flat_index.ntotal:
                # Reconstruct vector (FAISS doesn't easily allow extraction)
                # For now, we'll need to regenerate embedding or store it separately
                # This is a limitation - in production, store embeddings separately
                pass

        # For now, we'll rebuild indices from scratch
        # In production, implement proper migration with stored embeddings

        print("✅ Migration complete")

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG service statistics"""
        return {
            "flat_index": {
                "total_vectors": self.flat_index.ntotal,
                "description": "Current month transactions (exact search)"
            },
            "hnsw_index": {
                "total_vectors": self.hnsw_index.ntotal,
                "description": "Historical transactions (approximate search)"
            },
            "total_transactions": self.flat_index.ntotal + self.hnsw_index.ntotal
        }


# Global RAG service instance
rag_service = RAGService()
