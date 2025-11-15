# 🚀 BuckBounty Setup Guide

## 📋 Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

## 🔑 Getting API Keys

### 1. Plaid API (Required - FREE Sandbox)
1. Go to https://dashboard.plaid.com/signup
2. Sign up for a free account
3. Navigate to **Team Settings → Keys**
4. Copy your `client_id` and `sandbox` secret
5. Add to `.env` file:
   ```
   PLAID_CLIENT_ID=your_client_id
   PLAID_SECRET=your_sandbox_secret
   ```

**Note:** Sandbox is completely FREE and gives you test bank accounts with fake transactions!

### 2. Stripe API (Optional for now)
1. Go to https://dashboard.stripe.com/register
2. Sign up and get test API keys
3. Add to `.env` (optional for initial setup)

### 3. Polymarket API
- No API key needed! Uses public GraphQL endpoint
- Endpoint: https://api.thegraph.com/subgraphs/name/polymarket/matic-markets

## 🛠️ Installation

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

Backend will run on: http://localhost:8000

### Frontend Setup
```bash
# In a new terminal, from project root
npm install

# Start the development server
npm run dev
```

Frontend will run on: http://localhost:3000

## 🎯 How It Works

### 1. Connect Bank Account
- Click "Connect Bank Account" button
- Use Plaid's sandbox credentials:
  - Username: `user_good`
  - Password: `pass_good`
  - Any MFA code

### 2. Automatic Transaction Sync
- Transactions are fetched from Plaid
- Each transaction is automatically embedded and stored in the local vector database
- Vector DB is saved in `backend/data/vector_db/`

### 3. Smart Search
- Use natural language to search transactions
- Example: "coffee shops", "groceries last week", "expensive purchases"
- Vector similarity search finds relevant transactions

### 4. Auto-Sync on New Transactions
The system includes webhook support for automatic syncing:
- When Plaid detects a new transaction, it sends a webhook
- The `vector_db.auto_sync_webhook()` method automatically adds it to the vector DB
- No manual refresh needed!

## 📁 Project Structure
```
buckbounty/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── plaid_service.py     # Plaid integration
│   ├── vector_db.py         # FAISS vector database
│   ├── requirements.txt     # Python dependencies
│   └── data/                # Local vector DB storage
├── app/
│   ├── page.tsx             # Main page
│   ├── layout.tsx           # Layout
│   └── globals.css          # Styles
├── components/
│   ├── PlaidLink.tsx        # Bank connection
│   ├── Dashboard.tsx        # Stats dashboard
│   └── TransactionList.tsx  # Transaction display
└── .env                     # API keys
```

## 🧪 Testing with Sandbox

Plaid Sandbox provides test accounts:
- **Chase**: `user_good` / `pass_good`
- **Bank of America**: `user_good` / `pass_good`
- **Wells Fargo**: `user_good` / `pass_good`

These accounts have fake transactions you can use for testing!

## 🔧 Troubleshooting

### Backend won't start
- Make sure virtual environment is activated
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.11+)

### Frontend won't start
- Delete `node_modules` and `.next` folders
- Run `npm install` again
- Check Node version: `node --version` (should be 18+)

### Plaid connection fails
- Verify API keys in `.env` are correct
- Make sure you're using sandbox credentials
- Check backend is running on port 8000

## 🎉 Next Steps

Once everything is running:
1. Connect a test bank account
2. View your transactions
3. Try the smart search feature
4. Check the vector DB in `backend/data/vector_db/`

The foundation is ready for adding MARK (AI assistant), bill splitting, and deal hunting features!
