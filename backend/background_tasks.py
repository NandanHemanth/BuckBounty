"""
Background tasks for processing transactions
"""
import asyncio
from typing import List, Dict
from embedding_service import EmbeddingService
from vector_db import VectorDB
import json
import os

class BackgroundProcessor:
    def __init__(self, vector_db: VectorDB):
        self.vector_db = vector_db
        self.embedding_service = EmbeddingService()
        self.processing = False
        self.processed_file = './data/processed_transactions.json'
        
        # Create data directory
        os.makedirs('./data', exist_ok=True)
        
        # Load processed transaction IDs
        self.processed_ids = self._load_processed_ids()
    
    def _load_processed_ids(self) -> set:
        """Load IDs of already processed transactions"""
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_ids', []))
            except:
                return set()
        return set()
    
    def _save_processed_ids(self):
        """Save processed transaction IDs"""
        with open(self.processed_file, 'w') as f:
            json.dump({
                'processed_ids': list(self.processed_ids),
                'total_processed': len(self.processed_ids)
            }, f, indent=2)
    
    async def process_transactions_background(self):
        """Process all unprocessed transactions in background"""
        if self.processing:
            print("⚠️ Background processing already in progress")
            return
        
        self.processing = True
        print("\n🚀 Starting background transaction processing...")
        
        try:
            # Get all transactions from vector DB
            all_transactions = self.vector_db.get_all_transactions()
            
            # Filter out already processed transactions
            unprocessed = [
                txn for txn in all_transactions 
                if txn.get('id') not in self.processed_ids
            ]
            
            if not unprocessed:
                print("✅ All transactions already processed!")
                self.processing = False
                return
            
            print(f"📊 Found {len(unprocessed)} unprocessed transactions")
            
            # Process in batches to avoid overwhelming the API
            batch_size = 10
            for i in range(0, len(unprocessed), batch_size):
                batch = unprocessed[i:i + batch_size]
                
                # Process batch
                processed_batch = self.embedding_service.batch_process_transactions(batch)
                
                # Update vector DB with classifications
                for txn in processed_batch:
                    # Update metadata in vector DB
                    txn_id = txn.get('id')
                    for j, meta_txn in enumerate(self.vector_db.metadata):
                        if meta_txn.get('id') == txn_id:
                            self.vector_db.metadata[j]['classified_category'] = txn.get('classified_category')
                            self.vector_db.metadata[j]['embedding_text'] = txn.get('embedding_text')
                            break
                    
                    # Mark as processed
                    self.processed_ids.add(txn_id)
                
                # Save progress
                self.vector_db._save()
                self._save_processed_ids()
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
            
            # Generate category summary
            summary = self.embedding_service.get_category_summary(all_transactions)
            
            print("\n📈 Category Summary:")
            for category, data in sorted(summary.items(), key=lambda x: x[1]['total_amount'], reverse=True):
                print(f"  {category}: {data['count']} transactions, ${data['total_amount']:.2f}")
            
            print("\n✅ Background processing completed!")
            
        except Exception as e:
            print(f"❌ Error in background processing: {e}")
        finally:
            self.processing = False
    
    def get_status(self) -> Dict:
        """Get processing status"""
        total = len(self.vector_db.get_all_transactions())
        processed = len(self.processed_ids)
        
        return {
            'processing': self.processing,
            'total_transactions': total,
            'processed_transactions': processed,
            'pending_transactions': total - processed
        }
