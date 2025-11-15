# Transaction Embedding & Classification System

## Overview
Your BuckBounty app now has a sophisticated embedding and classification system that runs in the background to process all transactions.

## Features

### 1. Rich Embeddings
Each transaction embedding contains:
- Transaction ID
- Merchant name
- Amount and type (income/expense)
- Original category
- Classified category
- Date
- Account type and ID
- Status (pending/completed)

### 2. Automatic Classification
Transactions are automatically classified into these categories:
- **Food & Dining** - Restaurants, cafes, fast food
- **Groceries** - Supermarkets, grocery stores
- **Transportation** - Uber, Lyft, gas, airlines
- **Shopping** - Amazon, retail stores, clothing
- **Entertainment** - Netflix, Spotify, movies, games
- **Bills & Utilities** - Electric, water, internet, phone
- **Health & Fitness** - Gyms, pharmacies, medical
- **EMI & Loans** - Loan payments, installments, mortgages
- **Credit Cards** - Credit card payments
- **Income** - Salary, deposits, refunds, interest
- **Fun & Leisure** - Hobbies, recreation, travel
- **Other** - Everything else

### 3. Background Processing
- Runs automatically when you fetch transactions
- Processes in batches of 10 to avoid rate limits
- Saves progress incrementally
- Doesn't affect frontend performance

### 4. Persistent Storage
- All embeddings stored in `./data/vector_db/`
- Processed transaction IDs tracked in `./data/processed_transactions.json`
- Survives server restarts
- Shared across all agents

## API Endpoints

### Get Processing Status
```
GET /api/processing/status
```
Returns: processing status, total transactions, processed count

### Start Manual Processing
```
POST /api/processing/start
```
Manually trigger background processing

### Get Category Summary
```
GET /api/categories/summary
```
Returns: transaction counts and totals by category

### Get Transactions by Category
```
GET /api/categories/{category}
```
Returns: all transactions in a specific category

### Get Category Statistics
```
GET /api/stats/categories
```
Returns: count, total amount, and average for each category

## How It Works

1. **Fetch Transactions**: When you load transactions, they're added to vector DB
2. **Background Task**: Automatically starts processing unprocessed transactions
3. **Classification**: Each transaction is classified using keyword matching
4. **Embedding Generation**: Gemini API creates rich embeddings with all transaction info
5. **Storage**: Everything saved to local vector DB
6. **Availability**: Other agents can now query this data easily

## For Other Agents

Your other agents can now:
- Search transactions semantically using embeddings
- Filter by classified categories
- Get spending insights by category
- Query transaction history with natural language
- Access rich metadata for each transaction

## Testing

Run the test script to verify embeddings:
```bash
cd backend
python test_embeddings.py
```

## Configuration

Gemini API key is loaded from `.env`:
```
GEMINI_API_KEY=your_key_here
```

## Performance

- Processes ~10 transactions per second
- Batches of 10 to avoid rate limits
- 1 second delay between batches
- 609 transactions = ~60 seconds total processing time
