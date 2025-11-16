# Budget Feature Documentation

## Overview
Added a 5th card to the dashboard for budget management with Gemini AI embeddings. Users can set and update their monthly budget, which is stored with AI-powered embeddings for advanced financial tracking.

## Features

### Budget Card
- **Location**: 5th card in the dashboard summary row
- **Icon**: Target icon (🎯)
- **Functionality**:
  - Display current month budget
  - Show spending progress with visual progress bar
  - Edit budget inline with save/cancel buttons
  - Budget percentage indicator
  - Over-budget warning (red color when >100%)

### Budget Input
- **Format**: USD with 2 decimal places (e.g., 1500.00)
- **Validation**: Must be positive number
- **Edit Mode**: Click edit icon to enter edit mode
- **Save**: Click checkmark to save
- **Cancel**: Click X to cancel changes

### AI Embeddings
- **Technology**: Gemini API (embedding-001 model)
- **Storage**: Budget stored with AI embedding in vector database
- **Embedding Text**: Includes user ID, month, amount, and context
- **Override**: New budget replaces old embedding for the same month

## UI/UX Improvements

### Modern Card Design
All 5 cards now feature:
- ✅ Smaller, cleaner design
- ✅ Compact padding (p-3.5)
- ✅ Subtle shadows (shadow-sm → shadow-md on hover)
- ✅ Border for definition (border-gray-100)
- ✅ Smaller icons (w-4 h-4)
- ✅ Uppercase labels with tracking
- ✅ Responsive grid (2 cols mobile, 5 cols desktop)

### Budget Card Specific
- ✅ Inline edit mode with input field
- ✅ Save/Cancel buttons with icons
- ✅ Progress bar showing budget usage
- ✅ Percentage indicator
- ✅ Color-coded: Blue (normal), Red (over budget)
- ✅ Smooth transitions

## Backend Implementation

### API Endpoints

#### Set Budget
```
POST /api/budget/set?user_id={user_id}&amount={amount}&month={month}
```
- Sets or updates budget for specified month
- Generates Gemini embedding
- Stores in vector database
- Returns success confirmation

#### Get Budget
```
GET /api/budget/get?user_id={user_id}&month={month}
```
- Retrieves budget for specified month
- Returns amount (0.00 if not set)

#### Dashboard Stats (Updated)
```
GET /api/dashboard/stats?user_id={user_id}
```
- Now includes budget in summary
- Returns all dashboard data including budget

### Database Storage

#### Budget Data Structure
```json
{
  "user_id_2024-11": {
    "user_id": "user_123",
    "month": "2024-11",
    "amount": 1500.00,
    "embedding": [...],  // Gemini embedding vector
    "embedding_text": "Monthly budget for 2024-11: $1500.00 USD...",
    "updated_at": "2024-11-15T10:30:00"
  }
}
```

#### Storage Location
- File: `data/vector_db/budgets.json`
- Format: JSON with user_month keys
- Persistent across restarts

### Gemini Integration

#### Embedding Generation
```python
genai.embed_content(
    model="models/embedding-001",
    content=budget_text,
    task_type="retrieval_document"
)
```

#### Embedding Text Format
```
Monthly budget for {month}: ${amount} USD. 
User: {user_id}. 
Budget limit set for financial tracking and spending control.
```

## Usage Flow

1. **View Budget**: Budget card shows current month budget (or $0.00 if not set)
2. **Edit Budget**: Click edit icon (pencil) to enter edit mode
3. **Enter Amount**: Type budget amount (e.g., 1500.00)
4. **Save**: Click checkmark to save
5. **AI Processing**: Backend generates Gemini embedding and stores
6. **Display**: Card updates with new budget and progress bar
7. **Track Progress**: Progress bar shows spending vs budget
8. **Over Budget**: Card turns red if spending exceeds budget

## Visual Design

### Card Layout
```
┌─────────────────────────┐
│ 🎯              ✏️      │  Icon + Edit button
│ BUDGET                  │  Label
│ $1,500.00              │  Amount
│ $875.96 spent    58%   │  Progress info
│ ████████░░░░░░░░░░░░   │  Progress bar
└─────────────────────────┘
```

### Edit Mode
```
┌─────────────────────────┐
│ 🎯                      │  Icon only
│ BUDGET                  │  Label
│ $ [1500.00] ✓ ✗       │  Input + Save/Cancel
└─────────────────────────┘
```

## Benefits

### For Users
- ✅ Easy budget tracking
- ✅ Visual progress indicator
- ✅ Quick inline editing
- ✅ Over-budget warnings
- ✅ Monthly budget management

### For System
- ✅ AI-powered budget embeddings
- ✅ Semantic budget search capability
- ✅ Historical budget tracking
- ✅ Integration with transaction analysis
- ✅ Scalable storage

## Technical Details

### Dependencies
- Gemini API (google.generativeai)
- React hooks (useState, useEffect)
- Lucide React icons
- Axios for API calls

### State Management
- `budget`: Current budget amount
- `isEditingBudget`: Edit mode flag
- `budgetInput`: Input field value
- Synced with dashboard stats

### Error Handling
- Validates positive numbers
- Handles API failures gracefully
- Shows user-friendly error messages
- Maintains state consistency

## Future Enhancements

Potential improvements:
- Budget recommendations based on spending patterns
- Multi-month budget planning
- Category-specific budgets
- Budget alerts and notifications
- Budget vs actual reports
- AI-powered budget suggestions

---

The budget feature provides a clean, modern way to track spending against monthly goals with AI-powered embeddings for advanced financial insights.
