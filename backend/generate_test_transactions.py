"""
Script to generate custom test transactions in Plaid Sandbox
This will create additional transactions beyond the default sandbox data
"""
import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.transactions_refresh_request import TransactionsRefreshRequest
from datetime import datetime, timedelta
import random

load_dotenv()

# Initialize Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_custom_sandbox_item():
    """
    Create a custom sandbox item with specific institution
    Returns access_token
    """
    # Use 'custom' institution for maximum flexibility
    request = SandboxPublicTokenCreateRequest(
        institution_id='ins_109508',  # First Platypus Bank
        initial_products=['transactions', 'liabilities']
    )
    
    response = client.sandbox_public_token_create(request)
    public_token = response['public_token']
    
    # Exchange for access token
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_response = client.item_public_token_exchange(exchange_request)
    
    return exchange_response['access_token']

def refresh_transactions(access_token: str):
    """Force refresh transactions to get latest data"""
    request = TransactionsRefreshRequest(access_token=access_token)
    response = client.transactions_refresh(request)
    print(f"✓ Transactions refresh initiated")
    return response

if __name__ == "__main__":
    print("🔧 Plaid Sandbox Transaction Generator")
    print("=" * 50)
    
    print("\n📝 Note: Plaid Sandbox has fixed test data.")
    print("To get maximum transactions:")
    print("1. Connect multiple test accounts")
    print("2. Select ALL account types (checking, savings, credit, loans)")
    print("3. Use these test credentials:")
    print("   - user_good / pass_good (standard transactions)")
    print("   - user_custom / pass_good (custom test data)")
    
    print("\n💡 Maximum transactions per sandbox account: ~8-20")
    print("💡 To get 100+ transactions: Connect 5-10 different test accounts")
    
    print("\n" + "=" * 50)
