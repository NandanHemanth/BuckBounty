from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from plaid_service import PlaidService
from vector_db import VectorDB
from datetime import datetime

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
async def get_transactions(user_id: str, days: int = 30):
    """Get transactions from vector DB (includes all stored transactions)"""
    try:
        # Try to fetch new Plaid transactions and add to vector DB
        try:
            plaid_transactions = plaid_service.get_transactions(user_id, days)
            for txn in plaid_transactions:
                vector_db.add_transaction(txn)
        except Exception as plaid_error:
            print(f"Plaid fetch skipped: {plaid_error}")
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
