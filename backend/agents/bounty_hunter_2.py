"""
BountyHunter2 Agent - Finance News & Market Intelligence
Scrapes Yahoo Finance for market news and financial insights
Uses transaction context from vector DB to provide personalized updates
Runs once every 24 hours in background
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
import re

from .base_agent import BaseAgent


class BountyHunter2(BaseAgent):
    """
    BountyHunter2 Agent - Finance News & Market Intelligence
    """

    def __init__(self):
        super().__init__(
            agent_name="BountyHunter2",
            agent_type="Finance News & Market Intelligence",
            capabilities=[
                "yahoo_finance_scraping",
                "market_news_aggregation",
                "category_trend_analysis",
                "personalized_insights",
                "vector_db_integration"
            ]
        )

        # Data directory
        self.data_dir = Path("./data/finance_news")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # News storage file
        self.news_file = self.data_dir / "finance_news.json"

        # Last scrape timestamp
        self.last_scrape_file = self.data_dir / "last_scrape.json"
        self.last_scrape = self._load_last_scrape()

        # News storage
        self._load_news()

    def _load_last_scrape(self) -> Optional[datetime]:
        """Load last scrape timestamp"""
        if self.last_scrape_file.exists():
            try:
                with open(self.last_scrape_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data['last_scrape'])
            except Exception as e:
                print(f"⚠️ Error loading last scrape time: {e}")
        return None

    def _save_last_scrape(self):
        """Save last scrape timestamp"""
        try:
            with open(self.last_scrape_file, 'w') as f:
                json.dump({
                    'last_scrape': datetime.now().isoformat()
                }, f)
        except Exception as e:
            print(f"❌ Error saving last scrape time: {e}")

    def _load_news(self):
        """Load existing news from JSON file"""
        if self.news_file.exists():
            try:
                with open(self.news_file, 'r') as f:
                    self.news_articles = json.load(f)
                print(f"📰 Loaded {len(self.news_articles)} news articles")
            except Exception as e:
                print(f"⚠️ Error loading news: {e}")
                self.news_articles = []
        else:
            self.news_articles = []

    def _save_news(self):
        """Save news to JSON file"""
        try:
            with open(self.news_file, 'w') as f:
                json.dump(self.news_articles, f, indent=2, default=str)
            print(f"💾 Saved {len(self.news_articles)} news articles to {self.news_file}")
        except Exception as e:
            print(f"❌ Error saving news: {e}")

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process user requests related to finance news"""
        message = request.get("message", "").lower()
        user_id = request.get("user_id")

        # Determine intent
        if any(word in message for word in ["news", "market", "stock", "finance", "trend"]):
            # Get personalized news based on user's transaction categories
            news = await self._get_personalized_news(user_id, message)
            response_text = await self._format_news_response(news, message)

            return {
                "response": response_text,
                "data": {
                    "news": news,
                    "count": len(news)
                }
            }

        elif "scrape" in message or "update" in message or "refresh" in message:
            # Trigger manual scraping
            await self.scrape_finance_news()
            return {
                "response": f"✅ Finance news scraping completed! Found {len(self.news_articles)} articles.",
                "data": {"total_articles": len(self.news_articles)}
            }

        else:
            # General info
            last_scrape_str = self.last_scrape.strftime("%Y-%m-%d %H:%M") if self.last_scrape else "Never"
            return {
                "response": f"I currently have {len(self.news_articles)} finance news articles. "
                           f"Last updated: {last_scrape_str}. Ask me about market trends, specific sectors, or tell me to refresh!",
                "data": {
                    "total_articles": len(self.news_articles),
                    "last_scrape": last_scrape_str
                }
            }

    def should_scrape(self) -> bool:
        """Check if 24 hours have passed since last scrape"""
        if not self.last_scrape:
            return True

        time_since_scrape = datetime.now() - self.last_scrape
        return time_since_scrape >= timedelta(hours=24)

    async def scrape_finance_news(self):
        """
        Scrape Yahoo Finance for:
        1. Market news
        2. Sector-specific news
        3. Economic indicators
        """
        print("📊 BountyHunter2: Starting finance news scraping...")

        # Get user transaction categories for targeted scraping
        categories = await self._get_user_transaction_categories()

        # Map categories to finance sectors
        sector_map = {
            "food_dining": ["restaurants", "consumer", "retail"],
            "groceries": ["retail", "consumer"],
            "shopping": ["retail", "e-commerce", "consumer"],
            "transportation": ["automotive", "energy", "oil"],
            "entertainment": ["media", "entertainment", "tech"],
            "health_fitness": ["healthcare", "biotech"],
            "technology": ["tech", "software", "semiconductor"]
        }

        # Collect relevant sectors
        relevant_sectors = set()
        for category in categories:
            if category in sector_map:
                relevant_sectors.update(sector_map[category])

        if not relevant_sectors:
            relevant_sectors = ["general", "economy", "markets"]

        # Scrape each sector
        tasks = [
            self.scrape_yahoo_finance_sector(sector)
            for sector in relevant_sectors
        ]

        # Also scrape general market news
        tasks.append(self.scrape_yahoo_finance_general())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Scraping task {i} failed: {result}")

        # Remove duplicates
        self._deduplicate_news()

        # Keep only last 30 days of news
        self._clean_old_news()

        self._save_news()
        self.last_scrape = datetime.now()
        self._save_last_scrape()

        print(f"✅ Finance news scraping complete! Total articles: {len(self.news_articles)}")

    async def scrape_yahoo_finance_general(self):
        """Scrape general Yahoo Finance homepage"""
        print("📰 Scraping Yahoo Finance general news...")

        try:
            url = "https://finance.yahoo.com/"

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find news articles
                article_elements = soup.find_all(['article', 'li', 'div'], class_=re.compile(r'article|story|news', re.I))

                for element in article_elements[:30]:  # Limit to 30
                    try:
                        # Extract headline
                        headline_elem = element.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|headline', re.I))
                        if not headline_elem:
                            continue

                        headline = headline_elem.get_text(strip=True)

                        # Extract link
                        link_elem = element.find('a', href=True)
                        link = link_elem['href'] if link_elem else None
                        if link and not link.startswith('http'):
                            link = f"https://finance.yahoo.com{link}"

                        # Extract summary
                        summary_elem = element.find(['p', 'div'], class_=re.compile(r'summary|desc', re.I))
                        summary = summary_elem.get_text(strip=True) if summary_elem else ""

                        # Extract time
                        time_elem = element.find(['time', 'span'], class_=re.compile(r'time|date', re.I))
                        published_time = time_elem.get_text(strip=True) if time_elem else "Unknown"

                        if headline:
                            article = {
                                "id": f"yahoo_{hash(headline)}",
                                "source": "yahoo_finance",
                                "category": "general",
                                "headline": headline,
                                "summary": summary,
                                "url": link,
                                "published_time": published_time,
                                "scraped_date": datetime.now().isoformat()
                            }

                            self.news_articles.append(article)

                    except Exception as e:
                        continue

                print(f"✅ Yahoo Finance general news scraping complete")

        except Exception as e:
            print(f"❌ Yahoo Finance scraping error: {e}")

    async def scrape_yahoo_finance_sector(self, sector: str):
        """Scrape Yahoo Finance for specific sector"""
        print(f"📊 Scraping Yahoo Finance for sector: {sector}...")

        try:
            # Yahoo Finance sector URLs
            sector_urls = {
                "tech": "https://finance.yahoo.com/topic/technology",
                "healthcare": "https://finance.yahoo.com/topic/healthcare",
                "retail": "https://finance.yahoo.com/topic/retail",
                "energy": "https://finance.yahoo.com/topic/energy",
                "markets": "https://finance.yahoo.com/markets",
                "economy": "https://finance.yahoo.com/topic/economic-news"
            }

            url = sector_urls.get(sector, f"https://finance.yahoo.com/topic/{sector}")

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = await client.get(url, headers=headers)

                # If 404, skip
                if response.status_code == 404:
                    print(f"⚠️ Sector {sector} not found, skipping")
                    return

                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find articles (similar to general scraping)
                article_elements = soup.find_all(['article', 'li', 'div'], class_=re.compile(r'article|story|news', re.I))

                for element in article_elements[:20]:  # Limit to 20 per sector
                    try:
                        headline_elem = element.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|headline', re.I))
                        if not headline_elem:
                            continue

                        headline = headline_elem.get_text(strip=True)

                        link_elem = element.find('a', href=True)
                        link = link_elem['href'] if link_elem else None
                        if link and not link.startswith('http'):
                            link = f"https://finance.yahoo.com{link}"

                        summary_elem = element.find(['p', 'div'], class_=re.compile(r'summary|desc', re.I))
                        summary = summary_elem.get_text(strip=True) if summary_elem else ""

                        if headline:
                            article = {
                                "id": f"yahoo_{sector}_{hash(headline)}",
                                "source": "yahoo_finance",
                                "category": sector,
                                "headline": headline,
                                "summary": summary,
                                "url": link,
                                "scraped_date": datetime.now().isoformat()
                            }

                            self.news_articles.append(article)

                    except Exception as e:
                        continue

                print(f"✅ Yahoo Finance {sector} scraping complete")

        except Exception as e:
            print(f"❌ Yahoo Finance {sector} scraping error: {e}")

    async def _get_user_transaction_categories(self) -> List[str]:
        """Get user's transaction categories from vector DB"""
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            from vector_db import VectorDB

            vector_db = VectorDB()

            # Get category stats
            categories = vector_db.get_category_stats()

            # Extract category names
            return [cat["category"] for cat in categories]

        except Exception as e:
            print(f"⚠️ Error getting transaction categories: {e}")
            return []

    async def _get_personalized_news(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Get personalized news based on user's transaction history"""
        # Get user's top categories
        categories = await self._get_user_transaction_categories()

        # Search news matching categories or query
        relevant_news = []

        query_lower = query.lower()

        for article in self.news_articles:
            headline = article.get("headline", "").lower()
            summary = article.get("summary", "").lower()
            category = article.get("category", "").lower()

            # Match by query or user's transaction categories
            if (query_lower in headline or
                query_lower in summary or
                any(cat.lower() in headline or cat.lower() in summary for cat in categories) or
                category in [c.lower() for c in categories]):
                relevant_news.append(article)

        # Sort by date (newest first)
        relevant_news.sort(key=lambda x: x.get("scraped_date", ""), reverse=True)

        return relevant_news[:10]  # Return top 10

    async def _format_news_response(self, news: List[Dict], query: str) -> str:
        """Format news into a nice response using LLM"""
        if not news:
            return f"I couldn't find any finance news matching '{query}'. The market is always changing - let me refresh my data!"

        # Use LLM to format response naturally
        news_summary = "\n".join([
            f"- {article['headline']} ({article.get('category', 'general')})"
            for article in news[:5]
        ])

        prompt = f"""The user asked about: "{query}"

I found these finance news articles:
{news_summary}

Generate a helpful response that:
1. Summarizes the key market trends
2. Highlights 3-5 most relevant articles
3. Explains how this might impact personal finances

Keep it concise, informative, and actionable!"""

        context = {
            "user_query": query,
            "article_count": len(news)
        }

        response = await self.generate_response(prompt, context, temperature=0.7, max_tokens=600)

        return response

    def _deduplicate_news(self):
        """Remove duplicate news articles"""
        seen = set()
        unique_articles = []

        for article in self.news_articles:
            article_id = article.get("id")
            if article_id and article_id not in seen:
                seen.add(article_id)
                unique_articles.append(article)

        self.news_articles = unique_articles

    def _clean_old_news(self):
        """Remove news older than 30 days"""
        cutoff_date = datetime.now() - timedelta(days=30)

        filtered_articles = []

        for article in self.news_articles:
            try:
                scraped_date = datetime.fromisoformat(article.get("scraped_date", ""))
                if scraped_date >= cutoff_date:
                    filtered_articles.append(article)
            except:
                # Keep if can't parse date
                filtered_articles.append(article)

        self.news_articles = filtered_articles
