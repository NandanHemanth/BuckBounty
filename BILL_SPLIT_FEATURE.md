# Bill Split Feature

## Overview
The Bill Split feature allows users to upload bill images, parse them using Gemini AI, select items to split, and optionally pay through Stripe.

## Features
- 📸 Upload bill images (PNG, JPG)
- 🤖 AI-powered parsing with Gemini Vision API
- ✅ Select specific items from the bill
- 🔢 Split quantities (1-5 people)
- 💰 Proportional tax & tip calculation
- 💳 Stripe payment integration
- 📊 Automatic transaction addition to dashboard

## How It Works

### 1. Upload Bill
- Click the "Split Bill" button (left of BuckBounty header)
- Upload a bill image from your device
- Gemini AI parses the bill automatically

### 2. Review & Select
- View all parsed items with quantities and prices
- Select which items you want to pay for
- Choose split quantity for each item (1-5 people)
- See your calculated share including proportional tax & tip

### 3. Payment
- Pay with Stripe (redirects to Stripe checkout)
- Or skip payment and add transaction to dashboard
- Transaction automatically appears in your dashboard

## API Endpoints

### POST /api/bill/parse
Parse bill image using Gemini Vision API
- **Input**: Multipart form data with image file
- **Output**: Parsed bill data (items, tax, tip, total)

### POST /api/bill/create-payment
Create Stripe checkout session
- **Input**: Amount, user_id, bill_items
- **Output**: Stripe checkout URL

### POST /api/bill/add-transaction
Add bill transaction to dashboard without payment
- **Input**: Amount, user_id, bill_items, paid status
- **Output**: Transaction object

## Environment Variables Required
```
GEMINI_API_KEY=your_gemini_api_key
STRIPE_API_KEY=your_stripe_secret_key
```

## Installation

1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Make sure your .env file has the required API keys

3. Start the backend:
```bash
python main.py
```

4. Start the frontend:
```bash
npm run dev
```

## Usage Example

1. Connect your bank account (if not already connected)
2. Click "Split Bill" button
3. Upload a restaurant receipt
4. Gemini will parse:
   - Item names
   - Quantities
   - Prices
   - Tax
   - Tip
5. Select your items and split quantities
6. Choose to pay or skip payment
7. Transaction appears in dashboard

## Technical Details

### Bill Parsing
- Uses Gemini 1.5 Flash model
- Extracts structured JSON from bill images
- Handles various receipt formats
- Proportionally splits tax and tip based on selected items

### Payment Flow
- Stripe Checkout integration
- Secure payment processing
- Webhook support for payment confirmation
- Fallback to manual transaction entry

### Transaction Storage
- Stored in Vector DB with embeddings
- Categorized as "Dining"
- Includes bill item details
- Searchable and analyzable

## Future Enhancements
- [ ] Support for multiple currencies
- [ ] Group bill splitting with multiple users
- [ ] QR code sharing for group payments
- [ ] Receipt history and analytics
- [ ] OCR fallback for better accuracy
- [ ] Custom tip percentage calculator
