# Dashboard Features

## Overview
The enhanced dashboard provides modern, interactive visualizations of your transaction data using AI-powered embeddings and category classification.

## Features

### 1. Summary Cards
- **Total Transactions**: Count of transactions in current month
- **Total Spent**: Total spending with trend indicator (vs previous month)
- **Average Transaction**: Average transaction amount
- **Top Category**: Most frequent spending category

### 2. Interactive Charts

#### Radar Chart - Current vs Previous Month
- Compares spending across top 6 categories
- Shows current month (blue) vs previous month (purple)
- Click to expand to full screen
- Hover for detailed amounts

#### Pie Chart - Category Distribution
- Shows current month spending breakdown by category
- Color-coded categories
- Displays percentage and transaction count
- Click to expand to full screen

### 3. Category Details Table
- Lists all categories with spending comparison
- Shows current vs previous month amounts
- Transaction counts for each category
- Trend indicators (up/down arrows with percentage change)

### 4. Smart Real-Time Updates
- Dashboard **only** refreshes when new transactions are detected
- Transaction list silently polls every 10 seconds in the background
- No unnecessary re-renders or flickering
- Smooth animations and transitions only when data changes

## Technical Implementation

### Backend API
- **Endpoint**: `GET /api/dashboard/stats`
- **Features**:
  - Calculates current vs previous month statistics
  - Groups transactions by AI-classified categories
  - Computes spending trends and changes
  - Returns comprehensive comparison data

### Frontend Components
- **Dashboard.tsx**: Main dashboard with charts and stats
- **TransactionList.tsx**: Transaction list with auto-refresh
- **Charts**: Built with Recharts library
  - Radar chart for multi-category comparison
  - Pie chart for distribution visualization
  - Responsive and interactive

### AI Integration
- Uses Gemini API for transaction embeddings
- Automatic category classification
- Smart merchant recognition
- Semantic transaction search

## Usage

1. **Connect Bank Account**: Use Plaid Link to connect your bank
2. **View Dashboard**: Automatically loads with transaction data
3. **Interact with Charts**: Click any chart to expand to full screen
4. **Monitor Updates**: Dashboard refreshes automatically when new transactions arrive

## Category Classification

The system automatically classifies transactions into:
- Food & Dining
- Groceries
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Health & Fitness
- EMI & Loans
- Credit Cards
- Income
- Fun & Leisure
- Other

## Performance
- Efficient data fetching with caching
- Optimized rendering with React hooks
- Smooth animations and transitions
- Responsive design for all screen sizes
