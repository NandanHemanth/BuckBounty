# Plaid Sandbox - Maximum Transactions Guide

## Important: Plaid Sandbox Limitations

**Plaid's Sandbox environment has FIXED test data:**
- Each test account provides **8-20 transactions** (this is a Plaid limitation)
- Transactions are pre-generated and cannot be increased beyond this limit
- This is the same for ALL Plaid sandbox users

## How to Get Maximum Transactions (100+)

### Option 1: Connect Multiple Test Accounts (Recommended)

Connect 5-10 different test bank accounts to accumulate 100+ transactions:

1. **First Platypus Bank** - `user_good` / `pass_good`
2. **Tattersall Federal Credit Union** - `user_good` / `pass_good`  
3. **Tartan Bank** - `user_good` / `pass_good`
4. **Houndstooth Bank** - `user_good` / `pass_good`
5. **Royal Bank of Canada** - `user_good` / `pass_good`

For each connection:
- Select ALL account types (Checking, Savings, Credit Card, Loan)
- Use verification code: `1234`

### Option 2: Use Custom Test Credentials

Try these alternative test users:
- `user_custom` / `pass_good` - Custom test data
- `user_good` / `pass_good` - Standard test data

### Option 3: Production Environment

To get REAL unlimited transactions:
1. Upgrade to Plaid Production environment
2. Connect real bank accounts
3. Get actual transaction history (up to 2 years)

## Current Setup

Your app is configured to fetch:
- ✅ 730 days (2 years) of history
- ✅ All account types (checking, savings, credit, loans)
- ✅ Pagination for 500+ transactions
- ✅ Multiple accounts support

**The limitation is Plaid Sandbox's fixed test data, not your code.**

## Test Account Details

| Username | Password | Transactions | Notes |
|----------|----------|--------------|-------|
| user_good | pass_good | ~8-16 | Standard test account |
| user_custom | pass_good | ~8-16 | Custom test data |
| user_bad | pass_good | 0 | Fails (for error testing) |

## Verification Code
Always use: **1234**

## Next Steps

1. **For Testing**: Connect 5-10 different banks with `user_good`
2. **For Production**: Upgrade to Plaid Production and connect real accounts
3. **Current Status**: You have 16 transactions (normal for 1 sandbox account)
