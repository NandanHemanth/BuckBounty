"""
Credit Card Optimizer
Analyzes transactions and recommends best credit cards for maximum savings and points
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class CreditCardOptimizer:
    """Optimize credit card usage for maximum rewards and savings"""

    def __init__(self):
        """Load credit card data"""
        self.credit_cards_path = Path("./credit_cards.json")
        self.credit_cards = self._load_credit_cards()
        
        # Category mapping to credit card reward categories
        self.category_mapping = {
            'Dining': ['dining', 'restaurants'],
            'Groceries': ['supermarkets', 'grocery'],
            'Travel': ['travel', 'flights', 'hotels'],
            'Gas': ['gas stations', 'fuel'],
            'Shopping': ['retail', 'online shopping'],
            'Entertainment': ['streaming', 'entertainment'],
            'Transit': ['transit', 'transportation'],
            'Drugstores': ['drugstore', 'pharmacy']
        }

        print(f"💳 Loaded {len(self.credit_cards)} credit cards for optimization")

    def _load_credit_cards(self) -> List[Dict]:
        """Load credit card data from JSON"""
        try:
            with open(self.credit_cards_path, 'r') as f:
                data = json.load(f)
                return data.get('credit_cards', [])
        except Exception as e:
            print(f"❌ Error loading credit cards: {e}")
            return []

    def analyze_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Analyze transactions and recommend best credit cards
        
        Returns:
            - category_spending: Breakdown by category
            - recommended_cards: Best cards for user's spending pattern
            - best_card_per_category: Best card for each spending category
            - potential_savings: Estimated savings with optimal cards
            - current_vs_optimal: Comparison
        """
        # Calculate spending by category
        category_spending = {}
        total_spending = 0

        for txn in transactions:
            amount = abs(txn.get('amount', 0))
            category = txn.get('classified_category', 'Other')

            # Skip income
            if txn.get('amount', 0) < 0:
                continue

            if category not in category_spending:
                category_spending[category] = {
                    'total': 0,
                    'count': 0,
                    'transactions': []
                }

            category_spending[category]['total'] += amount
            category_spending[category]['count'] += 1
            category_spending[category]['transactions'].append(txn)
            total_spending += amount

        # Calculate percentages
        for category in category_spending:
            category_spending[category]['percentage'] = (
                category_spending[category]['total'] / total_spending * 100
                if total_spending > 0 else 0
            )

        # Find best cards for each category
        card_recommendations = self._recommend_cards_by_category(category_spending)

        # Find best card for EACH category
        best_card_per_category = self._find_best_card_per_category(category_spending)

        # Calculate potential savings
        savings_analysis = self._calculate_savings(category_spending, card_recommendations)

        return {
            'total_spending': total_spending,
            'category_spending': category_spending,
            'recommended_cards': card_recommendations,
            'best_card_per_category': best_card_per_category,
            'savings_analysis': savings_analysis,
            'analyzed_at': datetime.now().isoformat()
        }

    def _recommend_cards_by_category(self, category_spending: Dict) -> List[Dict]:
        """Recommend best credit cards based on spending categories"""
        recommendations = []

        # Analyze each card's rewards for user's spending
        for card in self.credit_cards:
            card_score = 0
            card_rewards = {}

            # Parse rewards
            rewards = card.get('rewards', [])

            for category, data in category_spending.items():
                spending = data['total']
                best_rate = 0

                # Find best reward rate for this category
                for reward in rewards:
                    reward_lower = reward.lower()
                    rate = self._extract_reward_rate(reward)

                    # Check if reward applies to this category
                    if self._category_matches(category, reward_lower):
                        if rate > best_rate:
                            best_rate = rate

                # Calculate points/cashback for this category
                if best_rate > 0:
                    card_rewards[category] = {
                        'rate': best_rate,
                        'spending': spending,
                        'value': spending * (best_rate / 100)
                    }
                    card_score += spending * (best_rate / 100)

            # Add card to recommendations
            recommendations.append({
                'card': card,
                'total_value': card_score,
                'category_rewards': card_rewards,
                'annual_fee': card.get('annual_fee', '$0')
            })

        # Sort by total value
        recommendations.sort(key=lambda x: x['total_value'], reverse=True)

        return recommendations[:5]  # Top 5 cards

    def _extract_reward_rate(self, reward_text: str) -> float:
        """Extract reward rate from text (e.g., '3x points' -> 3.0)"""
        import re

        # Look for patterns like "3x", "3%", "3 points"
        patterns = [
            r'(\d+(?:\.\d+)?)x',
            r'(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)\s*points',
            r'(\d+(?:\.\d+)?)\s*cash\s*back'
        ]

        for pattern in patterns:
            match = re.search(pattern, reward_text.lower())
            if match:
                return float(match.group(1))

        return 0.0

    def _category_matches(self, user_category: str, reward_text: str) -> bool:
        """Check if user's spending category matches reward category"""
        user_category_lower = user_category.lower()

        # Direct match
        if user_category_lower in reward_text:
            return True

        # Check mapping
        if user_category in self.category_mapping:
            for keyword in self.category_mapping[user_category]:
                if keyword in reward_text:
                    return True

        # Special cases
        if user_category == 'Dining' and any(word in reward_text for word in ['dining', 'restaurant', 'food']):
            return True
        if user_category == 'Groceries' and any(word in reward_text for word in ['grocery', 'supermarket']):
            return True
        if user_category == 'Travel' and any(word in reward_text for word in ['travel', 'flight', 'hotel', 'airline']):
            return True

        return False

    def _calculate_savings(self, category_spending: Dict, recommendations: List[Dict]) -> Dict:
        """Calculate potential savings with optimal credit card strategy"""
        if not recommendations:
            return {
                'current_rewards': 0,
                'optimal_rewards': 0,
                'potential_savings': 0,
                'savings_percentage': 0
            }

        # Assume current: 1% cashback on everything (baseline)
        total_spending = sum(cat['total'] for cat in category_spending.values())
        current_rewards = total_spending * 0.01

        # Optimal: Use best card for each category
        optimal_rewards = 0
        best_card = recommendations[0]

        for category, data in category_spending.items():
            spending = data['total']

            # Find best rate for this category across all recommended cards
            best_rate = 1.0  # Default 1%

            for rec in recommendations:
                category_rewards = rec.get('category_rewards', {})
                if category in category_rewards:
                    rate = category_rewards[category]['rate']
                    if rate > best_rate:
                        best_rate = rate

            optimal_rewards += spending * (best_rate / 100)

        # Calculate savings
        potential_savings = optimal_rewards - current_rewards
        savings_percentage = (potential_savings / total_spending * 100) if total_spending > 0 else 0

        # Subtract annual fees (simplified - use top card's fee)
        annual_fee_str = best_card['card'].get('annual_fee', '$0')
        annual_fee = float(annual_fee_str.replace('$', '').replace(',', '')) if '$' in annual_fee_str else 0

        net_savings = potential_savings - annual_fee

        return {
            'current_rewards': round(current_rewards, 2),
            'optimal_rewards': round(optimal_rewards, 2),
            'potential_savings': round(potential_savings, 2),
            'annual_fee': annual_fee,
            'net_savings': round(net_savings, 2),
            'savings_percentage': round(savings_percentage, 2),
            'recommendation': f"Switch to {best_card['card']['name']} for maximum rewards"
        }

    def get_card_details(self, card_name: str) -> Optional[Dict]:
        """Get details for a specific credit card"""
        for card in self.credit_cards:
            if card['name'].lower() == card_name.lower():
                return card
        return None

    def _find_best_card_per_category(self, category_spending: Dict) -> Dict[str, Dict]:
        """Find the single best credit card for each spending category"""
        best_cards = {}

        for category, data in category_spending.items():
            spending = data['total']
            best_card = None
            best_rate = 0
            best_value = 0

            # Check each card for this category
            for card in self.credit_cards:
                # Find best reward rate for this category
                category_rate = 1.0  # Default 1%

                for reward in card.get('rewards', []):
                    rate = self._extract_reward_rate(reward)
                    if self._category_matches(category, reward.lower()):
                        if rate > category_rate:
                            category_rate = rate

                # Calculate value
                value = spending * (category_rate / 100)

                # Track best card
                if value > best_value:
                    best_value = value
                    best_rate = category_rate
                    best_card = card

            if best_card:
                best_cards[category] = {
                    'card_name': best_card['name'],
                    'card_issuer': best_card['issuer'],
                    'reward_rate': f"{best_rate}%",
                    'spending': spending,
                    'annual_value': round(best_value, 2),
                    'annual_fee': best_card.get('annual_fee', '$0')
                }

        return best_cards

    def compare_cards(self, card_names: List[str], transactions: List[Dict]) -> Dict:
        """Compare specific cards for user's spending pattern"""
        comparison = []

        for card_name in card_names:
            card = self.get_card_details(card_name)
            if not card:
                continue

            # Calculate value for this card
            total_value = 0
            category_breakdown = {}

            # Analyze spending
            for txn in transactions:
                amount = abs(txn.get('amount', 0))
                category = txn.get('classified_category', 'Other')

                if txn.get('amount', 0) < 0:  # Skip income
                    continue

                # Find best reward rate
                best_rate = 1.0  # Default
                for reward in card.get('rewards', []):
                    rate = self._extract_reward_rate(reward)
                    if self._category_matches(category, reward.lower()):
                        if rate > best_rate:
                            best_rate = rate

                value = amount * (best_rate / 100)
                total_value += value

                if category not in category_breakdown:
                    category_breakdown[category] = {'value': 0, 'rate': best_rate}
                category_breakdown[category]['value'] += value

            comparison.append({
                'card': card,
                'total_value': round(total_value, 2),
                'category_breakdown': category_breakdown
            })

        # Sort by value
        comparison.sort(key=lambda x: x['total_value'], reverse=True)

        return {
            'comparison': comparison,
            'winner': comparison[0]['card']['name'] if comparison else None
        }


# Global optimizer instance
credit_card_optimizer = CreditCardOptimizer()
