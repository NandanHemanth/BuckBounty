# Dashboard User Guide

## 🎯 Overview
Your new dashboard provides intelligent, interactive visualizations of your spending patterns with AI-powered insights.

## 📊 Dashboard Components

### Summary Cards (Top Row)
Four clean, modern cards showing:
1. **Transactions** - Total count for current month
2. **Total Spent** - With trend indicator (↑ or ↓ vs last month)
3. **Avg Transaction** - Average spending per transaction
4. **Top Category** - Your most frequent spending category

### Interactive Charts

#### 🎯 Radar Chart - Monthly Comparison
- **What it shows**: Top 6 spending categories
- **Blue area**: Current month spending
- **Purple area**: Previous month spending
- **How to use**: 
  - Hover over points to see exact amounts
  - Click anywhere on the chart to expand to full screen
  - Click the X button to close expanded view

#### 🥧 Pie Chart - Category Breakdown
- **What it shows**: Current month spending distribution
- **Colors**: Each category has a unique color
- **Labels**: Show category name and percentage (if >5%)
- **How to use**:
  - Hover over slices to see amount and transaction count
  - Click to expand to full screen
  - Visual breakdown of where your money goes

### 📋 Category Details Table
- Lists all spending categories
- Shows current vs previous month comparison
- Transaction counts in parentheses
- Trend indicators with percentage change
- Color-coded: Red ↑ (spending increased), Green ↓ (spending decreased)

## 🔄 Smart Updates

### How It Works
1. **Background Monitoring**: System checks for new transactions every 10 seconds
2. **Smart Detection**: Only updates dashboard when NEW transactions are added
3. **No Flickering**: Charts stay stable until actual data changes
4. **Instant Updates**: When new transaction detected, dashboard refreshes automatically

### What You'll See
- ✅ Smooth, stable charts during normal viewing
- ✅ Automatic refresh when you add transactions
- ✅ No loading spinners during background checks
- ✅ Clean, professional experience

## 🎨 Design Features

### Modern & Clean
- Soft shadows and rounded corners
- Smooth hover effects
- Professional color scheme
- Responsive layout (works on all screen sizes)

### Interactive Elements
- **Hover Effects**: Cards and charts respond to mouse hover
- **Click to Expand**: Any chart can be viewed full screen
- **Smooth Animations**: Transitions are fluid and natural
- **Tooltips**: Detailed information on hover

## 💡 Tips

1. **Expand Charts**: Click any chart for a detailed full-screen view
2. **Compare Months**: Use the radar chart to spot spending pattern changes
3. **Track Categories**: Watch the pie chart to see where most money goes
4. **Monitor Trends**: Check the trend arrows in summary cards
5. **Review Details**: Scroll down to the table for exact numbers

## 🔧 Technical Notes

### Data Sources
- All data comes from your connected bank accounts via Plaid
- Transactions are automatically categorized using AI (Gemini)
- Embeddings enable smart search and classification

### Update Frequency
- Background check: Every 10 seconds
- Dashboard refresh: Only when new transactions detected
- No manual refresh needed (but available via Refresh button)

### Categories
The system recognizes these categories:
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

## 🚀 Getting Started

1. Connect your bank account using Plaid Link
2. Wait for transactions to sync (automatic)
3. Dashboard loads with your data
4. Explore charts by clicking and hovering
5. Monitor spending patterns over time

## ❓ Troubleshooting

**Dashboard not loading?**
- Check if backend is running (should be on port 8000)
- Verify transactions are synced
- Click the Retry button if error appears

**Charts not updating?**
- New transactions take ~10 seconds to detect
- Manual refresh available via Refresh button
- Check browser console for errors

**Categories seem wrong?**
- AI classification improves over time
- Based on merchant names and transaction details
- Most accurate for common merchants

---

Enjoy your new intelligent financial dashboard! 💰✨
