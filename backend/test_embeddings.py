"""
Test script to verify embedding generation and classification
"""
from embedding_service import EmbeddingService
from vector_db import VectorDB

def test_embeddings():
    print("🧪 Testing Embedding Service\n")
    
    # Initialize services
    embedding_service = EmbeddingService()
    vector_db = VectorDB()
    
    # Get a sample transaction
    all_transactions = vector_db.get_all_transactions()
    
    if not all_transactions:
        print("❌ No transactions found in vector DB")
        return
    
    sample_txn = all_transactions[0]
    
    print(f"📝 Sample Transaction:")
    print(f"   Merchant: {sample_txn.get('merchant')}")
    print(f"   Amount: ${sample_txn.get('amount')}")
    print(f"   Category: {sample_txn.get('category')}")
    print(f"   Date: {sample_txn.get('date')}\n")
    
    # Process transaction
    print("🔄 Processing transaction...\n")
    processed = embedding_service.process_transaction(sample_txn.copy())
    
    print(f"✅ Processed Transaction:")
    print(f"   Classified Category: {processed.get('classified_category')}")
    print(f"   Embedding Dimension: {len(processed.get('embedding', []))}")
    print(f"   Embedding Text: {processed.get('embedding_text')[:200]}...")
    print(f"\n📊 Embedding Metadata:")
    for key, value in processed.get('embedding_metadata', {}).items():
        print(f"   {key}: {value}")
    
    print("\n✅ Embedding test completed!")

if __name__ == "__main__":
    test_embeddings()
