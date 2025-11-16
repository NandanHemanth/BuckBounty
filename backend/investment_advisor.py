"""
Investment Advisor
Generates investment portfolio breakdown based on savings from credit card optimization
"""

from typing import Dict, Any, List
from datetime import datetime


class InvestmentAdvisor:
    """Generate investment portfolio recommendations based on savings"""

    def __init__(self):
        """Initialize investment advisor with portfolio strategies"""
        
        # Portfolio allocation strategies
        self.strategies = {
            'conservative': {
                'name': 'Conservative Growth',
                'risk_level': 'Low',
                'allocation': {
                    'Bonds': 50,
                    'Large Cap Stocks': 25,
                    'Index Funds': 15,
                    'Cash/Money Market': 10
                },
                'expected_return': '4-6% annually',
                'description': 'Low risk, steady growth. Ideal for short-term goals (1-3 years).'
            },
            'moderate': {
                'name': 'Balanced Growth',
                'risk_level': 'Medium',
                'allocation': {
                    'Index Funds (S&P 500)': 35,
                    'Bonds': 25,
                    'Large Cap Stocks': 20,
                    'International Stocks': 10,
                    'REITs': 10
                },
                'expected_return': '6-8% annually',
                'description': 'Balanced risk and reward. Ideal for medium-term goals (3-7 years).'
            },
            'aggressive': {
                'name': 'Aggressive Growth',
                'risk_level': 'High',
                'allocation': {
                    'Growth Stocks': 40,
                    'Index Funds': 25,
                    'Tech Stocks': 15,
                    'International Stocks': 10,
                    'Small Cap Stocks': 10
                },
                'expected_return': '8-12% annually',
                'description': 'High risk, high reward. Ideal for long-term goals (7+ years).'
            },
            'wealth_building': {
                'name': 'Wealth Building',
                'risk_level': 'Medium-High',
                'allocation': {
                    'Index Funds (S&P 500)': 30,
                    'Growth Stocks': 25,
                    'Dividend Stocks': 20,
                    'REITs': 15,
                    'Bonds': 10
                },
                'expected_return': '7-10% annually',
                'description': 'Optimized for long-term wealth accumulation with dividend income.'
            }
        }

        # Specific investment recommendations
        self.investment_options = {
            'Index Funds': [
                {'name': 'Vanguard S&P 500 ETF (VOO)', 'expense_ratio': '0.03%', 'type': 'ETF'},
                {'name': 'Schwab Total Stock Market (SWTSX)', 'expense_ratio': '0.03%', 'type': 'Mutual Fund'},
                {'name': 'Fidelity ZERO Total Market (FZROX)', 'expense_ratio': '0.00%', 'type': 'Mutual Fund'}
            ],
            'Bonds': [
                {'name': 'Vanguard Total Bond Market (BND)', 'expense_ratio': '0.03%', 'type': 'ETF'},
                {'name': 'iShares Core U.S. Aggregate Bond (AGG)', 'expense_ratio': '0.03%', 'type': 'ETF'}
            ],
            'Growth Stocks': [
                {'name': 'Technology Sector ETF (XLK)', 'expense_ratio': '0.10%', 'type': 'ETF'},
                {'name': 'ARK Innovation ETF (ARKK)', 'expense_ratio': '0.75%', 'type': 'ETF'}
            ],
            'Dividend Stocks': [
                {'name': 'Vanguard Dividend Appreciation (VIG)', 'expense_ratio': '0.06%', 'type': 'ETF'},
                {'name': 'Schwab U.S. Dividend Equity (SCHD)', 'expense_ratio': '0.06%', 'type': 'ETF'}
            ],
            'REITs': [
                {'name': 'Vanguard Real Estate ETF (VNQ)', 'expense_ratio': '0.12%', 'type': 'ETF'},
                {'name': 'Schwab U.S. REIT ETF (SCHH)', 'expense_ratio': '0.07%', 'type': 'ETF'}
            ]
        }

        print("📈 Investment Advisor initialized")

    def generate_portfolio(
        self,
        monthly_savings: float,
        time_horizon: str = 'medium',
        risk_tolerance: str = 'moderate'
    ) -> Dict[str, Any]:
        """
        Generate investment portfolio recommendation
        
        Args:
            monthly_savings: Amount saved per month from credit card optimization
            time_horizon: 'short' (1-3 years), 'medium' (3-7 years), 'long' (7+ years)
            risk_tolerance: 'conservative', 'moderate', 'aggressive'
        """
        
        # Select strategy based on inputs
        if time_horizon == 'short':
            strategy_key = 'conservative'
        elif time_horizon == 'long':
            strategy_key = 'aggressive' if risk_tolerance == 'aggressive' else 'wealth_building'
        else:
            strategy_key = risk_tolerance

        strategy = self.strategies.get(strategy_key, self.strategies['moderate'])

        # Calculate investment amounts
        allocation_breakdown = {}
        for asset_class, percentage in strategy['allocation'].items():
            amount = monthly_savings * (percentage / 100)
            allocation_breakdown[asset_class] = {
                'percentage': percentage,
                'monthly_amount': round(amount, 2),
                'annual_amount': round(amount * 12, 2)
            }

        # Add specific investment recommendations
        detailed_recommendations = self._get_detailed_recommendations(allocation_breakdown)

        # Calculate projections
        projections = self._calculate_projections(
            monthly_savings,
            strategy['expected_return'],
            time_horizon
        )

        return {
            'strategy': strategy,
            'monthly_savings': monthly_savings,
            'annual_savings': monthly_savings * 12,
            'allocation_breakdown': allocation_breakdown,
            'detailed_recommendations': detailed_recommendations,
            'projections': projections,
            'next_steps': self._generate_next_steps(monthly_savings),
            'generated_at': datetime.now().isoformat()
        }

    def _get_detailed_recommendations(self, allocation_breakdown: Dict) -> List[Dict]:
        """Get specific fund/stock recommendations for each asset class"""
        recommendations = []

        for asset_class, data in allocation_breakdown.items():
            if asset_class in self.investment_options:
                options = self.investment_options[asset_class]
                recommendations.append({
                    'asset_class': asset_class,
                    'monthly_amount': data['monthly_amount'],
                    'options': options,
                    'recommendation': options[0]['name']  # Recommend first option
                })

        return recommendations

    def _calculate_projections(
        self,
        monthly_investment: float,
        expected_return_str: str,
        time_horizon: str
    ) -> Dict[str, Any]:
        """Calculate investment growth projections"""
        
        # Parse expected return (take average)
        import re
        returns = re.findall(r'(\d+)', expected_return_str)
        if len(returns) >= 2:
            avg_return = (float(returns[0]) + float(returns[1])) / 2 / 100
        else:
            avg_return = 0.07  # Default 7%

        # Time periods
        periods = {
            'short': [1, 2, 3],
            'medium': [1, 3, 5, 7],
            'long': [1, 5, 10, 20]
        }

        years = periods.get(time_horizon, [1, 5, 10])

        projections = []

        for year in years:
            # Future value of annuity formula
            # FV = P * [((1 + r)^n - 1) / r]
            months = year * 12
            monthly_rate = avg_return / 12

            if monthly_rate == 0:
                future_value = monthly_investment * months
            else:
                future_value = monthly_investment * (
                    ((1 + monthly_rate) ** months - 1) / monthly_rate
                )

            total_invested = monthly_investment * months
            gains = future_value - total_invested

            projections.append({
                'year': year,
                'total_invested': round(total_invested, 2),
                'projected_value': round(future_value, 2),
                'gains': round(gains, 2),
                'return_percentage': round((gains / total_invested * 100) if total_invested > 0 else 0, 2)
            })

        return {
            'annual_return_rate': f"{avg_return * 100:.1f}%",
            'projections': projections,
            'note': 'Projections are estimates based on historical averages. Actual returns may vary.'
        }

    def _generate_next_steps(self, monthly_savings: float) -> List[str]:
        """Generate actionable next steps"""
        steps = [
            "Open a brokerage account (Fidelity, Vanguard, or Schwab recommended)",
            f"Set up automatic monthly investment of ${monthly_savings:.2f}",
            "Start with low-cost index funds for diversification",
            "Consider tax-advantaged accounts (IRA, 401k) first",
            "Review and rebalance portfolio quarterly"
        ]

        if monthly_savings >= 500:
            steps.append("Consider consulting with a financial advisor for personalized guidance")

        return steps

    def generate_savings_to_wealth_plan(
        self,
        credit_card_savings: Dict[str, Any],
        coupon_savings: float = 0
    ) -> Dict[str, Any]:
        """
        Complete plan: Credit card savings + coupons → Investment portfolio
        
        Args:
            credit_card_savings: Output from CreditCardOptimizer
            coupon_savings: Estimated monthly savings from coupons
        """
        
        # Calculate total monthly savings
        cc_monthly_savings = credit_card_savings.get('net_savings', 0) / 12
        total_monthly_savings = cc_monthly_savings + coupon_savings

        # Generate portfolio
        portfolio = self.generate_portfolio(
            monthly_savings=total_monthly_savings,
            time_horizon='long',
            risk_tolerance='wealth_building'
        )

        # Add savings breakdown
        portfolio['savings_breakdown'] = {
            'credit_card_optimization': {
                'monthly': round(cc_monthly_savings, 2),
                'annual': round(credit_card_savings.get('net_savings', 0), 2),
                'source': 'Optimized credit card rewards'
            },
            'coupon_savings': {
                'monthly': round(coupon_savings, 2),
                'annual': round(coupon_savings * 12, 2),
                'source': 'Coupons and deals'
            },
            'total': {
                'monthly': round(total_monthly_savings, 2),
                'annual': round(total_monthly_savings * 12, 2)
            }
        }

        # Add wealth building summary
        portfolio['wealth_building_summary'] = self._generate_wealth_summary(
            total_monthly_savings,
            portfolio['projections']
        )

        return portfolio

    def _generate_wealth_summary(self, monthly_savings: float, projections: Dict) -> Dict:
        """Generate wealth building summary"""
        
        # Get 10-year projection
        ten_year = next(
            (p for p in projections['projections'] if p['year'] == 10),
            projections['projections'][-1]
        )

        return {
            'monthly_investment': monthly_savings,
            'ten_year_value': ten_year['projected_value'],
            'total_gains': ten_year['gains'],
            'wealth_multiplier': round(ten_year['projected_value'] / ten_year['total_invested'], 2),
            'message': f"By investing ${monthly_savings:.2f}/month, you could build ${ten_year['projected_value']:,.2f} in {ten_year['year']} years!"
        }


# Global investment advisor instance
investment_advisor = InvestmentAdvisor()
