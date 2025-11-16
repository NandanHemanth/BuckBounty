"""
PolyMarket API Service
Fetches prediction market data from PolyMarket
"""
import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PolyMarketService:
    def __init__(self):
        self.api_key = os.getenv('POLYMARKET_API_KEY', '019a887f-4e29-7dfa-9a49-25d6bf64b871')
        self.secret_key = os.getenv('POLYMARKET_SECRET_KEY', 'sG_Wpln0_8KAZOz8D7pwW9QSIal7dDdSysnbfQPL40c=')
        self.base_url = 'https://gamma-api.polymarket.com'
        self.clob_url = 'https://clob.polymarket.com'
        
    async def get_trending_markets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending prediction markets - using curated mock data"""
        logger.info("Using curated mock markets")
        return self._get_mock_markets()
    
    async def get_market_details(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed market information"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f'{self.clob_url}/markets/{market_id}')
                
                if response.status_code == 200:
                    return response.json()
                return None
                
        except Exception as e:
            logger.error(f"Error fetching market details: {e}")
            return None
    
    async def search_markets(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search markets by keyword"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f'{self.clob_url}/markets',
                    params={'search': query, 'limit': limit}
                )
                
                if response.status_code == 200:
                    markets = response.json()
                    return self._format_markets(markets)
                return []
                
        except Exception as e:
            logger.error(f"Error searching markets: {e}")
            return []
    
    def _format_markets(self, markets: List[Dict]) -> List[Dict[str, Any]]:
        """Format market data for frontend"""
        formatted = []
        
        for market in markets:
            try:
                outcome_prices = market.get('outcome_prices', [0.5, 0.5])
                
                if isinstance(outcome_prices, str):
                    outcome_prices = [0.5, 0.5]
                elif not isinstance(outcome_prices, list):
                    outcome_prices = [0.5, 0.5]
                
                yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else 0.5
                no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else 0.5
                
                formatted.append({
                    'id': market.get('condition_id', market.get('id', 'unknown')),
                    'question': market.get('question', market.get('description', 'Unknown Market')),
                    'odds': {
                        'yes': round(yes_price * 100, 1),
                        'no': round(no_price * 100, 1)
                    },
                    'volume': float(market.get('volume', 0)),
                    'liquidity': float(market.get('liquidity', 0)),
                    'end_date': market.get('end_date_iso', market.get('endDate', None)),
                    'category': market.get('category', 'General'),
                    'active': market.get('active', True)
                })
            except Exception as e:
                logger.error(f"Error formatting market: {e}")
                continue
                
        return formatted
    
    def _get_mock_markets(self) -> List[Dict[str, Any]]:
        """Return curated mock prediction markets"""
        return [
            {
                'id': 'btc-100k-2025',
                'question': 'Will Bitcoin reach $100,000 by end of 2025?',
                'odds': {'yes': 67.0, 'no': 33.0},
                'volume': 2300000,
                'liquidity': 450000,
                'end_date': '2025-12-31T23:59:59Z',
                'category': 'Crypto',
                'active': True
            },
            {
                'id': 'fed-rate-cut-dec',
                'question': 'Will the Fed cut interest rates in December 2025?',
                'odds': {'yes': 62.0, 'no': 38.0},
                'volume': 1800000,
                'liquidity': 320000,
                'end_date': '2025-12-15T23:59:59Z',
                'category': 'Economics',
                'active': True
            },
            {
                'id': 'sp500-up-10',
                'question': 'Will S&P 500 be up 10% or more this year?',
                'odds': {'yes': 82.0, 'no': 18.0},
                'volume': 1200000,
                'liquidity': 280000,
                'end_date': '2025-12-31T23:59:59Z',
                'category': 'Stock Market',
                'active': True
            },
            {
                'id': 'tesla-300',
                'question': 'Will Tesla stock hit $300 by end of 2025?',
                'odds': {'yes': 38.0, 'no': 62.0},
                'volume': 950000,
                'liquidity': 180000,
                'end_date': '2025-12-31T23:59:59Z',
                'category': 'Stock Market',
                'active': True
            },
            {
                'id': 'inflation-below-3',
                'question': 'Will US inflation be below 3% by year end?',
                'odds': {'yes': 78.0, 'no': 22.0},
                'volume': 850000,
                'liquidity': 160000,
                'end_date': '2025-12-31T23:59:59Z',
                'category': 'Economics',
                'active': True
            }
        ]
    
    def calculate_potential_return(self, investment: float, odds: float) -> Dict[str, float]:
        """Calculate potential return on investment"""
        if odds >= 100:
            return {'investment': investment, 'potential_win': investment, 'return_pct': 0}
        
        potential_win = investment / (odds / 100)
        profit = potential_win - investment
        return_pct = (profit / investment) * 100
        
        return {
            'investment': round(investment, 2),
            'potential_win': round(potential_win, 2),
            'profit': round(profit, 2),
            'return_pct': round(return_pct, 1)
        }

# Global instance
polymarket_service = PolyMarketService()
