from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from plaid_service import PlaidService
from vector_db import VectorDB
from background_tasks import BackgroundProcessor
from datetime import datetime
import asyncio

load_dotenv()

app = FastAPI(title="BuckBounty API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
plaid_service = PlaidService()
vector_db = VectorDB()
background_processor = BackgroundProcessor(vector_db)

class LinkTokenRequest(BaseModel):
    user_id: str

class PublicTokenRequest(BaseModel):
    public_token: str
    user_id: str

@app.get("/")
async def root():
    return {"message": "BuckBounty API is running"}

@app.post("/api/plaid/create_link_token")
async def create_link_token(request: LinkTokenRequest):
    """Create Plaid Link token for connecting bank accounts"""
    try:
        link_token = plaid_service.create_link_token(request.user_id)
        return {"link_token": link_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plaid/exchange_public_token")
async def exchange_public_token(request: PublicTokenRequest):
    """Exchange public token for access token"""
    try:
        access_token = plaid_service.exchange_public_token(request.public_token)
        # Store access token securely (in production, use encrypted database)
        return {"success": True, "message": "Bank account connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions/{user_id}")
async def get_transactions(user_id: str, days: int = 30, background_tasks: BackgroundTasks = None):
    """Get transactions from vector DB (includes all stored transactions)"""
    try:
        # Try to fetch new Plaid transactions and add to vector DB
        try:
            plaid_transactions = plaid_service.get_transactions(user_id, days)
            for txn in plaid_transactions:
                vector_db.add_transaction(txn)
        except Exception as plaid_error:
            print(f"Plaid fetch skipped: {plaid_error}")
        
        # Trigger background processing if not already running
        if background_tasks and not background_processor.processing:
            background_tasks.add_task(background_processor.process_transactions_background)
        
        # Return all transactions from vector DB
        all_transactions = vector_db.get_all_transactions()
        
        # Sort by date (newest first)
        all_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return {
            "transactions": all_transactions,
            "count": len(all_transactions),
            "synced_to_vector_db": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions/search")
async def search_transactions(query: str, limit: int = 10):
    """Search transactions using vector similarity"""
    try:
        results = vector_db.search_transactions(query, limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "vector_db_initialized": vector_db.is_initialized(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/processing/status")
async def get_processing_status():
    """Get background processing status"""
    return background_processor.get_status()

@app.post("/api/processing/start")
async def start_processing(background_tasks: BackgroundTasks):
    """Manually trigger background processing"""
    if background_processor.processing:
        return {"message": "Processing already in progress"}
    
    background_tasks.add_task(background_processor.process_transactions_background)
    return {"message": "Background processing started"}

@app.get("/api/categories/summary")
async def get_category_summary():
    """Get transaction summary by category"""
    try:
        from embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        all_transactions = vector_db.get_all_transactions()
        summary = embedding_service.get_category_summary(all_transactions)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories/{category}")
async def get_transactions_by_category(category: str):
    """Get all transactions in a specific category"""
    try:
        transactions = vector_db.get_transactions_by_category(category)
        return {
            "category": category,
            "count": len(transactions),
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/categories")
async def get_category_stats(time_filter: str = 'all'):
    """Get statistics for all categories with optional time filter"""
    try:
        from datetime import datetime, timedelta
        
        all_transactions = vector_db.get_all_transactions()
        
        # Apply time filter
        if time_filter != 'all':
            now = datetime.now()
            filter_days = {
                '1m': 30,
                '3m': 90,
                '6m': 180,
                '1y': 365
            }
            
            if time_filter in filter_days:
                cutoff_date = (now - timedelta(days=filter_days[time_filter])).strftime('%Y-%m-%d')
                all_transactions = [
                    txn for txn in all_transactions 
                    if txn.get('date', '') >= cutoff_date
                ]
        
        # Calculate stats
        stats = {}
        for txn in all_transactions:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
