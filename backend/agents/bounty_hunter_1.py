"""
BountyHunter1 Agent - Coupon & Deal Hunter
Scrapes coupons from Gmail (UberEats, DoorDash), Honey, and Rakuten
Stores in JSON and pushes to vector DB
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


class BountyHunter1(BaseAgent):
    """
    BountyHunter1 Agent - Specialized in finding and managing coupon codes
    """

    def __init__(self):
        super().__init__(
            agent_name="BountyHunter1",
            agent_type="Coupon & Deal Hunter",
            capabilities=[
                "gmail_coupon_extraction",
                "honey_scraping",
                "rakuten_scraping",
                "coupon_storage",
                "vector_db_integration"
            ]
        )

        # Data directory
        self.data_dir = Path("./data/coupons")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Coupon storage file
        self.coupon_file = self.data_dir / "all_coupons.json"

        # Last scrape timestamp
        self.last_scrape = None

        # Initialize coupon storage
        self._load_coupons()

    def _load_coupons(self):
        """Load existing coupons from JSON file"""
        if self.coupon_file.exists():
            try:
                with open(self.coupon_file, 'r') as f:
                    self.coupons = json.load(f)
                print(f"📦 Loaded {len(self.coupons)} existing coupons")
            except Exception as e:
                print(f"⚠️ Error loading coupons: {e}")
                self.coupons = []
        else:
            self.coupons = []

    def _save_coupons(self):
        """Save coupons to JSON file"""
        try:
            with open(self.coupon_file, 'w') as f:
                json.dump(self.coupons, f, indent=2, default=str)
            print(f"💾 Saved {len(self.coupons)} coupons to {self.coupon_file}")
        except Exception as e:
            print(f"❌ Error saving coupons: {e}")

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process user requests related to coupons"""
        message = request.get("message", "").lower()
        user_id = request.get("user_id")

        # Determine intent
        if any(word in message for word in ["coupon", "deal", "discount", "promo"]):
            # Search for relevant coupons
            coupons = await self._search_coupons(message)
            response_text = await self._format_coupon_response(coupons, message)

            return {
                "response": response_text,
                "data": {
                    "coupons": coupons,
                    "count": len(coupons)
                }
            }

        elif "scrape" in message or "update" in message or "refresh" in message:
            # Trigger manual scraping
            await self.scrape_all_sources()
            return {
                "response": f"✅ Coupon scraping completed! Found {len(self.coupons)} total coupons.",
                "data": {"total_coupons": len(self.coupons)}
            }

        else:
            # General coupon info
            return {
                "response": f"I currently have {len(self.coupons)} coupons in my database. "
                           f"Ask me about specific stores, categories, or tell me to refresh the coupon database!",
                "data": {"total_coupons": len(self.coupons)}
            }

    async def scrape_all_sources(self):
        """
        Scrape all coupon sources:
        1. Gmail (UberEats, DoorDash)
        2. Honey.com
        3. Rakuten.com
        """
        print("🔍 BountyHunter1: Starting coupon scraping...")

        tasks = [
            self.scrape_gmail_coupons(),
            self.scrape_honey(),
            self.scrape_rakuten()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Scraping task {i} failed: {result}")

        self._save_coupons()
        self.last_scrape = datetime.now()

        print(f"✅ Scraping complete! Total coupons: {len(self.coupons)}")

        # TODO: Push to vector DB in background
        asyncio.create_task(self._push_to_vector_db())

    async def scrape_gmail_coupons(self):
        """
        Scrape Gmail for UberEats and DoorDash coupon codes
        NOTE: Requires Gmail API setup with OAuth2
        """
        print("📧 Scraping Gmail for coupons...")

        # Check if Gmail API credentials exist
        gmail_token_path = Path("./credentials/gmail_token.json")
        if not gmail_token_path.exists():
            print("⚠️ Gmail API not configured. Skipping Gmail scraping.")
            print("   To enable: Set up Gmail API credentials in ./credentials/gmail_token.json")
            return

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

            creds = None
            if gmail_token_path.exists():
                creds = Credentials.from_authorized_user_file(str(gmail_token_path), SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    print("⚠️ Gmail credentials need authorization")
                    return

            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds)

            # Search for UberEats and DoorDash emails
            queries = [
                'from:ubereats.com (promo OR coupon OR discount)',
                'from:doordash.com (promo OR coupon OR discount)'
            ]

            for query in queries:
                # Get messages from last 30 days
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=50
                ).execute()

                messages = results.get('messages', [])

                for msg in messages:
                    # Get full message
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()

                    # Extract coupon codes from message body
                    coupons = self._extract_coupons_from_email(message)
                    self.coupons.extend(coupons)

            print(f"✅ Gmail scraping complete")

        except ImportError:
            print("⚠️ Google API libraries not installed. Run: pip install google-auth google-auth-httplib2 google-api-python-client")
        except Exception as e:
            print(f"❌ Gmail scraping error: {e}")

    def _extract_coupons_from_email(self, message: Dict) -> List[Dict[str, Any]]:
        """Extract coupon codes from Gmail message"""
        coupons = []

        try:
            # Get email body
            payload = message['payload']
            headers = payload.get('headers', [])

            # Get sender
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

            # Determine merchant
            merchant = 'Unknown'
            if 'ubereats' in sender.lower():
                merchant = 'UberEats'
            elif 'doordash' in sender.lower():
                merchant = 'DoorDash'

            # Get body text
            body = self._get_email_body(payload)

            # Extract coupon codes (alphanumeric codes, usually 6-20 characters)
            code_patterns = [
                r'(?:code|promo|coupon)[\s:]*([A-Z0-9]{6,20})',
                r'use[\s:]+([A-Z0-9]{6,20})',
                r'\b([A-Z0-9]{6,20})\b(?=.*(?:off|discount|save))'
            ]

            for pattern in code_patterns:
                matches = re.findall(pattern, body, re.IGNORECASE)
                for code in matches:
                    coupon = {
                        "id": f"gmail_{merchant}_{code}_{datetime.now().timestamp()}",
                        "source": "gmail",
                        "merchant": merchant,
                        "code": code.upper(),
                        "description": subject,
                        "found_date": datetime.now().isoformat(),
                        "expiry_date": None,  # Could parse from email
                        "email_date": date,
                        "category": "food_delivery"
                    }

                    # Avoid duplicates
                    if not any(c["code"] == code.upper() and c["merchant"] == merchant for c in self.coupons):
                        coupons.append(coupon)

        except Exception as e:
            print(f"⚠️ Error extracting from email: {e}")

        return coupons

    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body text"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        import base64
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in payload and 'data' in payload['body']:
            import base64
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body

    async def scrape_honey(self):
        """Scrape Honey.com for popular coupons"""
        print("🍯 Scraping Honey.com...")

        try:
            url = "https://www.joinhoney.com/explore"

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find coupon cards (Note: This is a simplified scraper)
                # Actual selectors may need adjustment based on Honey's current HTML structure
                coupon_elements = soup.find_all(['div', 'article'], class_=re.compile(r'store|deal|coupon', re.I))

                for element in coupon_elements[:50]:  # Limit to 50
                    try:
                        # Extract merchant name
                        merchant_elem = element.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'store|merchant|title', re.I))
                        merchant = merchant_elem.get_text(strip=True) if merchant_elem else "Unknown"

                        # Extract deal description
                        desc_elem = element.find(['p', 'span'], class_=re.compile(r'desc|deal|offer', re.I))
                        description = desc_elem.get_text(strip=True) if desc_elem else ""

                        # Extract code if available
                        code_elem = element.find(['code', 'span'], class_=re.compile(r'code', re.I))
                        code = code_elem.get_text(strip=True) if code_elem else None

                        if merchant and (description or code):
                            coupon = {
                                "id": f"honey_{merchant}_{datetime.now().timestamp()}",
                                "source": "honey",
                                "merchant": merchant,
                                "code": code,
                                "description": description,
                                "found_date": datetime.now().isoformat(),
                                "url": url,
                                "category": "general"
                            }

                            # Avoid duplicates
                            if not any(c.get("merchant") == merchant and c.get("description") == description for c in self.coupons):
                                self.coupons.append(coupon)

                    except Exception as e:
                        continue

                print(f"✅ Honey scraping complete")

        except Exception as e:
            print(f"❌ Honey scraping error: {e}")

    async def scrape_rakuten(self):
        """Scrape Rakuten.com for cashback deals"""
        print("💰 Scraping Rakuten.com...")

        try:
            url = "https://www.rakuten.com/"

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find deal cards (simplified - may need adjustment)
                deal_elements = soup.find_all(['div', 'article'], class_=re.compile(r'store|deal|offer', re.I))

                for element in deal_elements[:50]:  # Limit to 50
                    try:
                        # Extract merchant
                        merchant_elem = element.find(['h2', 'h3', 'h4'], class_=re.compile(r'store|merchant', re.I))
                        merchant = merchant_elem.get_text(strip=True) if merchant_elem else "Unknown"

                        # Extract cashback rate
                        cashback_elem = element.find(['span', 'div'], class_=re.compile(r'cash|rate|percent', re.I))
                        cashback = cashback_elem.get_text(strip=True) if cashback_elem else ""

                        if merchant and cashback:
                            coupon = {
                                "id": f"rakuten_{merchant}_{datetime.now().timestamp()}",
                                "source": "rakuten",
                                "merchant": merchant,
                                "code": None,
                                "description": f"{cashback} cashback",
                                "found_date": datetime.now().isoformat(),
                                "url": url,
                                "category": "cashback"
                            }

                            # Avoid duplicates
                            if not any(c.get("merchant") == merchant and c.get("source") == "rakuten" for c in self.coupons):
                                self.coupons.append(coupon)

                    except Exception as e:
                        continue

                print(f"✅ Rakuten scraping complete")

        except Exception as e:
            print(f"❌ Rakuten scraping error: {e}")

    async def _search_coupons(self, query: str) -> List[Dict[str, Any]]:
        """Search coupons based on query"""
        query_lower = query.lower()

        relevant_coupons = []

        for coupon in self.coupons:
            merchant = coupon.get("merchant", "").lower()
            description = coupon.get("description", "").lower()
            category = coupon.get("category", "").lower()

            if (query_lower in merchant or
                query_lower in description or
                query_lower in category or
                any(word in merchant or word in description for word in query_lower.split())):
                relevant_coupons.append(coupon)

        # Sort by date (newest first)
        relevant_coupons.sort(key=lambda x: x.get("found_date", ""), reverse=True)

        return relevant_coupons[:10]  # Return top 10

    async def _format_coupon_response(self, coupons: List[Dict], query: str) -> str:
        """Format coupons into a nice response using LLM"""
        if not coupons:
            return f"I couldn't find any coupons matching '{query}'. Try asking about popular stores like UberEats, DoorDash, or check my full coupon database!"

        # Use LLM to format response naturally
        coupon_summary = "\n".join([
            f"- {c['merchant']}: {c.get('description', 'N/A')} {('(Code: ' + c['code'] + ')') if c.get('code') else ''}"
            for c in coupons[:5]
        ])

        prompt = f"""The user asked about: "{query}"

I found these coupons:
{coupon_summary}

Generate a friendly, helpful response that:
1. Mentions how many coupons were found
2. Lists the top 3-5 coupons with details
3. Suggests how they can save money

Keep it concise and enthusiastic!"""

        context = {
            "user_query": query,
            "coupon_count": len(coupons)
        }

        response = await self.generate_response(prompt, context, temperature=0.7, max_tokens=500)

        return response

    async def _push_to_vector_db(self):
        """Push coupons to vector DB for semantic search"""
        print("📤 Pushing coupons to vector DB...")

        try:
            # Import vector DB
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            from vector_db import VectorDB

            vector_db = VectorDB()

            # Create embeddings for each coupon
            for coupon in self.coupons:
                # Create searchable text
                text = f"{coupon['merchant']} - {coupon.get('description', '')} {coupon.get('code', '')}"

                # Add to vector DB with metadata
                vector_db.add_memory(
                    text=text,
                    metadata={
                        "type": "coupon",
                        "merchant": coupon['merchant'],
                        "code": coupon.get('code'),
                        "source": coupon['source'],
                        "date": coupon['found_date']
                    }
                )

            print(f"✅ Pushed {len(self.coupons)} coupons to vector DB")

        except Exception as e:
            print(f"❌ Error pushing to vector DB: {e}")
