import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import datetime, timedelta

class PlaidService:
    def __init__(self):
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,  # Use Sandbox for free testing
            api_key={
                'clientId': os.getenv('PLAID_CLIENT_ID'),
                'secret': os.getenv('PLAID_SECRET'),
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        self.access_tokens = {}  # In production, use encrypted database
        
    def create_link_token(self, user_id: str):
        """Create a link token for Plaid Link"""
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="BuckBounty",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            webhook='https://your-webhook-url.com/plaid/webhook'  # Update in production
        )
        
        response = self.client.link_token_create(request)
        return response['link_token']
    
    def exchange_public_token(self, public_token: str):
        """Exchange public token for access token"""
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.client.item_public_token_exchange(request)
        access_token = response['access_token']
        
        # Store access token (in production, encrypt and store in database)
        self.access_tokens[response['item_id']] = access_token
        
        return access_token
    
    def get_transactions(self, user_id: str, days: int = 30):
        """Fetch transactions from Plaid"""
        # In production, retrieve access_token from database using user_id
        # For now, using the first available token
        if not self.access_tokens:
            raise Exception("No bank accounts connected")
        
        access_token = list(self.access_tokens.values())[0]
        
        start_date = (datetime.now() - timedelta(days=days)).date()
        end_date = datetime.now().date()
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        response = self.client.transactions_get(request)
        transactions = response['transactions']
        
        # Format transactions
        formatted_transactions = []
        for txn in transactions:
            formatted_transactions.append({
                'id': txn['transaction_id'],
                'date': str(txn['date']),
                'amount': txn['amount'],
                'merchant': txn['merchant_name'] or txn['name'],
                'category': txn['category'][0] if txn['category'] else 'Other',
                'pending': txn['pending']
            })
        
        return formatted_transactions
