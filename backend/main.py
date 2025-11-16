# Fix Windows console encoding FIRST (before any imports that print)
import sys
import os
if sys.platform == 'win32' and os.name == 'nt':
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except Exception:
        pass  # Silently fail if encoding setup doesn't work

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from plaid_service import PlaidService
from vector_db import VectorDB
from background_tasks import BackgroundProcessor
from bill_service import BillService
from datetime import datetime
import asyncio
import stripe
from contextlib import asynccontextmanager

# Import agents
from agents.mcp_server import mcp_server
from agents.mark_agent import MarkAgent
from agents.bounty_hunter_1 import BountyHunter1
from agents.bounty_hunter_2 import BountyHunter2
from agents.scheduler import agent_scheduler

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MCP server and start background tasks"""
    print("🚀 Starting BuckBounty API with MCP Agents...")

    # Start MCP server
    await mcp_server.start()

    # Schedule BountyHunter2 to scrape every 24 hours
    agent_scheduler.add_task(
        task_id="bh2_finance_news_scrape",
        task_func=bounty_hunter_2.scrape_finance_news,
        interval_hours=24,
        run_immediately=True  # Run on startup if 24 hours have passed
    )

    # Start the scheduler in background
    asyncio.create_task(agent_scheduler.start())

    print("✅ All agents initialized and ready!")
    
    yield
    
    # Cleanup on shutdown (if needed)
    print("🛑 Shutting down BuckBounty API...")

app = FastAPI(title="BuckBounty API", lifespan=lifespan)

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
bill_service = BillService()

# Initialize Stripe
stripe_key = os.getenv('STRIPE_API_KEY', '')
if stripe_key.startswith('sk_'):
    stripe.api_key = stripe_key

# Initialize Agents
bounty_hunter_1 = BountyHunter1()
bounty_hunter_2 = BountyHunter2()
mark_agent = MarkAgent(bounty_hunter_1, bounty_hunter_2)

# Register agents with MCP server
mcp_server.register_agent("mark", mark_agent)
mcp_server.register_agent("bounty_hunter_1", bounty_hunter_1)
mcp_server.register_agent("bounty_hunter_2", bounty_hunter_2)

class LinkTokenRequest(BaseModel):
    user_id: str

class PublicTokenRequest(BaseModel):
    public_token: str
    user_id: str

class BillPaymentRequest(BaseModel):
    amount: float
    user_id: str
    bill_items: List[dict]

class BillTransactionRequest(BaseModel):
    amount: float
    user_id: str
    bill_items: List[dict]
    paid: bool = False

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

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(user_id: str = "default"):
    """Get comprehensive dashboard statistics with current vs previous month comparison"""
    try:
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        all_transactions = vector_db.get_all_transactions()
        
        # Get current date
        now = datetime.now()
        current_month_start = now.replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)
        
        # Split transactions by month
        current_month_txns = []
        previous_month_txns = []
        
        for txn in all_transactions:
            txn_date_str = txn.get('date', '')
            if not txn_date_str:
                continue
            
            try:
                txn_date = datetime.strptime(txn_date_str, '%Y-%m-%d')
                if txn_date >= current_month_start:
                    current_month_txns.append(txn)
                elif previous_month_start <= txn_date < current_month_start:
                    previous_month_txns.append(txn)
            except:
                continue
        
        # Calculate category stats for both months
        def calculate_category_stats(transactions):
            stats = defaultdict(lambda: {'count': 0, 'amount': 0})
            total_spent = 0
            
            for txn in transactions:
                amount = abs(txn.get('amount', 0))
                category = txn.get('classified_category', 'Other')
                
                # Skip income transactions for spending stats
                if txn.get('amount', 0) < 0:
                    continue
                
                stats[category]['count'] += 1
                stats[category]['amount'] += amount
                total_spent += amount
            
            return dict(stats), total_spent
        
        current_stats, current_total = calculate_category_stats(current_month_txns)
        previous_stats, previous_total = calculate_category_stats(previous_month_txns)
        
        # Get all unique categories
        all_categories = set(list(current_stats.keys()) + list(previous_stats.keys()))
        
        # Build comparison data
        category_comparison = []
        for category in all_categories:
            category_comparison.append({
                'category': category,
                'current_amount': current_stats.get(category, {}).get('amount', 0),
                'previous_amount': previous_stats.get(category, {}).get('amount', 0),
                'current_count': current_stats.get(category, {}).get('count', 0),
                'previous_count': previous_stats.get(category, {}).get('count', 0)
            })
        
        # Sort by current amount
        category_comparison.sort(key=lambda x: x['current_amount'], reverse=True)
        
        # Calculate top category
        top_category = category_comparison[0]['category'] if category_comparison else 'N/A'
        
        # Calculate average transaction
        avg_transaction = current_total / len(current_month_txns) if current_month_txns else 0
        
        # Get current month budget
        budget = vector_db.get_budget(user_id, current_month_start.strftime('%Y-%m'))
        
        return {
            'summary': {
                'total_transactions': len(current_month_txns),
                'total_spent': current_total,
                'avg_transaction': avg_transaction,
                'top_category': top_category,
                'budget': budget
            },
            'category_comparison': category_comparison,
            'current_month': {
                'transactions': len(current_month_txns),
                'total': current_total
            },
            'previous_month': {
                'transactions': len(previous_month_txns),
                'total': previous_total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/budget/set")
async def set_budget(user_id: str, amount: float, month: Optional[str] = None):
    """Set or update budget for a specific month"""
    try:
        from datetime import datetime
        
        # Use current month if not specified
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        # Validate amount
        if amount < 0:
            raise HTTPException(status_code=400, detail="Budget amount must be positive")
        
        # Save budget with embedding
        vector_db.set_budget(user_id, month, amount)
        
        return {
            'success': True,
            'user_id': user_id,
            'month': month,
            'amount': amount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/budget/get")
async def get_budget(user_id: str, month: Optional[str] = None):
    """Get budget for a specific month"""
    try:
        from datetime import datetime
        
        # Use current month if not specified
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        budget = vector_db.get_budget(user_id, month)
        
        return {
            'user_id': user_id,
            'month': month,
            'amount': budget
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bill/parse")
async def parse_bill(file: UploadFile = File(...)):
    """Parse bill image using Gemini Vision API"""
    try:
        # Read file content
        content = await file.read()
        
        # Parse bill using Gemini
        parsed_data = bill_service.parse_bill_image(content)
        
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bill/create-payment")
async def create_payment(request: BillPaymentRequest):
    """Create Stripe checkout session for bill payment"""
    try:
        if not stripe.api_key:
            raise HTTPException(status_code=500, detail="Stripe not configured")
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Bill Split Payment',
                        'description': f"{len(request.bill_items)} items",
                    },
                    'unit_amount': int(request.amount * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:3000?payment=success',
            cancel_url='http://localhost:3000?payment=cancelled',
            metadata={
                'user_id': request.user_id,
                'bill_items': str(request.bill_items)
            }
        )
        
        return {
            'checkout_url': session.url,
            'session_id': session.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bill/add-transaction")
async def add_bill_transaction(request: BillTransactionRequest):
    """Add bill split transaction to dashboard"""
    try:
        from datetime import datetime
        
        # Create transaction object
        transaction = {
            'id': f"bill_{datetime.now().timestamp()}",
            'transaction_id': f"bill_{datetime.now().timestamp()}",
            'user_id': request.user_id,
            'amount': request.amount,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'name': f"Bill Split - {len(request.bill_items)} items",
            'merchant': 'Bill Split',
            'merchant_name': 'Bill Split',
            'category': ['Food and Drink', 'Restaurants'],
            'classified_category': 'Dining',
            'paid': request.paid,
            'bill_items': request.bill_items
        }
        
        # Add to vector DB
        vector_db.add_transaction(transaction)
        
        return {
            'success': True,
            'transaction': transaction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bill/webhook")
async def stripe_webhook(request: dict):
    """Handle Stripe webhook events"""
    try:
        event = request

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']

            # Add transaction as paid
            # This would be called after successful payment
            pass

        return {'status': 'success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AGENT ENDPOINTS ====================

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []
    target_agent: Optional[str] = None

@app.post("/api/agents/chat")
async def agent_chat(request: ChatRequest):
    """Chat with MARK and the agent team"""
    try:
        # Route request through MCP server
        result = await mcp_server.route_request(
            user_id=request.user_id,
            message=request.message,
            conversation_history=request.conversation_history,
            target_agent=request.target_agent
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/status")
async def get_agent_status():
    """Get status of all agents and MCP server"""
    try:
        return mcp_server.get_server_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/bounty-hunter-1/scrape")
async def trigger_bh1_scrape(background_tasks: BackgroundTasks):
    """Manually trigger BountyHunter1 coupon scraping"""
    try:
        background_tasks.add_task(bounty_hunter_1.scrape_all_sources)
        return {
            "success": True,
            "message": "BountyHunter1 scraping started in background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/bounty-hunter-2/scrape")
async def trigger_bh2_scrape(background_tasks: BackgroundTasks):
    """Manually trigger BountyHunter2 finance news scraping"""
    try:
        background_tasks.add_task(bounty_hunter_2.scrape_finance_news)
        return {
            "success": True,
            "message": "BountyHunter2 scraping started in background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/bounty-hunter-1/coupons")
async def get_coupons(query: Optional[str] = None):
    """Get coupons from BountyHunter1"""
    try:
        if query:
            coupons = await bounty_hunter_1._search_coupons(query)
        else:
            coupons = bounty_hunter_1.coupons

        return {
            "coupons": coupons,
            "count": len(coupons),
            "last_scrape": bounty_hunter_1.last_scrape.isoformat() if bounty_hunter_1.last_scrape else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/bounty-hunter-2/news")
async def get_finance_news(query: Optional[str] = None):
    """Get finance news from BountyHunter2"""
    try:
        if query:
            news = await bounty_hunter_2._get_personalized_news("default", query)
        else:
            news = bounty_hunter_2.news_articles

        return {
            "news": news,
            "count": len(news),
            "last_scrape": bounty_hunter_2.last_scrape.isoformat() if bounty_hunter_2.last_scrape else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
