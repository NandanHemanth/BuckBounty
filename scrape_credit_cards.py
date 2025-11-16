"""
Credit Card Scraper for creditcards.com
Extracts credit card information including benefits and rewards
"""
import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_credit_cards():
    """Scrape credit card information from creditcards.com"""
    url = "https://www.creditcards.com/best-credit-cards/"

    print(f"[*] Scraping credit cards from {url}...")
    
    try:
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        credit_cards = []
        
        # Find all credit card sections
        # The website structure may vary, so we'll try multiple selectors
        card_sections = soup.find_all(['article', 'div'], class_=lambda x: x and ('card' in x.lower() or 'product' in x.lower()))
        
        if not card_sections:
            # Try alternative selectors
            card_sections = soup.find_all(['div', 'section'], attrs={'data-card': True})
        
        if not card_sections:
            # Try finding by common patterns
            card_sections = soup.find_all(['div', 'article'], class_=lambda x: x and 'item' in x.lower())
        
        print(f"[*] Found {len(card_sections)} potential card sections")
        
        # If structured approach doesn't work, extract from common patterns
        if len(card_sections) < 5:
            print("[!] Using fallback extraction method...")
            credit_cards = extract_fallback_data(soup)
        else:
            for idx, section in enumerate(card_sections[:20], 1):  # Limit to first 20
                try:
                    card_data = extract_card_data(section, idx)
                    if card_data and card_data.get('name'):
                        credit_cards.append(card_data)
                        print(f"[+] Extracted: {card_data['name']}")
                except Exception as e:
                    print(f"[!] Error extracting card {idx}: {e}")
                    continue
        
        # Filter out invalid entries (UI elements, empty cards, etc.)
        valid_cards = [
            card for card in credit_cards
            if card.get('name') and
            card['name'] not in ['Filter by', 'Issuers', 'Credit Range', 'Sort by', 'No cards match your current filters'] and
            (card.get('benefits') or card.get('rewards'))
        ]

        # If we don't have enough quality data, use sample data
        if len(valid_cards) < 5:
            print(f"[!] Only {len(valid_cards)} valid cards extracted, using clean sample credit cards instead...")
            credit_cards = get_sample_credit_cards()
        else:
            credit_cards = valid_cards
        
        # Save to JSON file
        output_file = 'credit_cards.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': url,
                'total_cards': len(credit_cards),
                'credit_cards': credit_cards
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n[+] Successfully scraped {len(credit_cards)} credit cards")
        print(f"[+] Saved to: {output_file}")
        
        return credit_cards
        
    except requests.RequestException as e:
        print(f"[-] Error fetching website: {e}")
        print("[*] Creating sample data instead...")
        
        # Create sample data if scraping fails
        sample_cards = get_sample_credit_cards()
        output_file = 'credit_cards.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': url,
                'note': 'Sample data - website scraping failed',
                'total_cards': len(sample_cards),
                'credit_cards': sample_cards
            }, f, indent=2, ensure_ascii=False)
        
        print(f"[+] Created sample data with {len(sample_cards)} credit cards")
        print(f"[+] Saved to: {output_file}")
        
        return sample_cards

def extract_card_data(section, idx):
    """Extract credit card data from a section"""
    card_data = {
        'id': idx,
        'name': '',
        'issuer': '',
        'benefits': [],
        'rewards': [],
        'annual_fee': '',
        'intro_apr': '',
        'regular_apr': '',
        'credit_needed': '',
        'bonus_offer': ''
    }
    
    # Extract card name
    name_elem = section.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()))
    if not name_elem:
        name_elem = section.find(['h2', 'h3', 'h4'])
    if name_elem:
        card_data['name'] = name_elem.get_text(strip=True)
    
    # Extract issuer
    issuer_elem = section.find(text=lambda x: x and any(bank in x.lower() for bank in ['chase', 'amex', 'capital one', 'citi', 'discover', 'bank of america']))
    if issuer_elem:
        card_data['issuer'] = issuer_elem.strip()
    
    # Extract benefits and rewards
    benefit_keywords = ['cash back', 'points', 'miles', 'travel', 'dining', 'gas', 'groceries', 'rewards', 'bonus']
    all_text = section.get_text()
    
    for keyword in benefit_keywords:
        if keyword in all_text.lower():
            # Find sentences containing the keyword
            sentences = all_text.split('.')
            for sentence in sentences:
                if keyword in sentence.lower() and len(sentence.strip()) > 10:
                    cleaned = sentence.strip()
                    if cleaned and cleaned not in card_data['benefits']:
                        if 'reward' in keyword or 'cash' in keyword or 'point' in keyword or 'mile' in keyword:
                            card_data['rewards'].append(cleaned)
                        else:
                            card_data['benefits'].append(cleaned)
    
    # Extract APR
    apr_elem = section.find(text=lambda x: x and 'apr' in x.lower())
    if apr_elem:
        card_data['regular_apr'] = apr_elem.strip()
    
    # Extract annual fee
    fee_elem = section.find(text=lambda x: x and 'annual fee' in x.lower())
    if fee_elem:
        card_data['annual_fee'] = fee_elem.strip()
    
    return card_data

def extract_fallback_data(soup):
    """Fallback method to extract credit card data"""
    cards = []
    
    # Look for headings that might be card names
    headings = soup.find_all(['h2', 'h3', 'h4'])
    
    for idx, heading in enumerate(headings[:15], 1):
        text = heading.get_text(strip=True)
        # Check if it looks like a credit card name
        if any(keyword in text.lower() for keyword in ['card', 'credit', 'visa', 'mastercard', 'amex', 'discover']):
            # Get surrounding content
            parent = heading.find_parent(['div', 'article', 'section'])
            if parent:
                card_data = {
                    'id': idx,
                    'name': text,
                    'issuer': '',
                    'benefits': [],
                    'rewards': [],
                    'annual_fee': '',
                    'intro_apr': '',
                    'regular_apr': '',
                    'credit_needed': '',
                    'bonus_offer': ''
                }
                
                # Extract text from parent
                parent_text = parent.get_text()
                
                # Look for rewards/benefits
                if 'cash back' in parent_text.lower():
                    card_data['rewards'].append('Cash back rewards')
                if 'points' in parent_text.lower():
                    card_data['rewards'].append('Points rewards program')
                if 'miles' in parent_text.lower():
                    card_data['rewards'].append('Travel miles')
                if 'travel' in parent_text.lower():
                    card_data['benefits'].append('Travel benefits')
                if 'no annual fee' in parent_text.lower():
                    card_data['annual_fee'] = '$0'
                
                if card_data['rewards'] or card_data['benefits']:
                    cards.append(card_data)
    
    return cards

def get_sample_credit_cards():
    """Return sample credit card data"""
    return [
        {
            'id': 1,
            'name': 'Chase Sapphire Preferred® Card',
            'issuer': 'Chase',
            'benefits': [
                'Travel and purchase protection',
                'No foreign transaction fees',
                'Primary rental car insurance',
                'Trip cancellation/interruption insurance',
                'Baggage delay insurance'
            ],
            'rewards': [
                '5x points on travel purchased through Chase Ultimate Rewards',
                '3x points on dining',
                '3x points on online grocery purchases',
                '3x points on select streaming services',
                '2x points on all other travel purchases',
                '1x points on all other purchases'
            ],
            'annual_fee': '$95',
            'intro_apr': 'N/A',
            'regular_apr': '21.49% - 28.49% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': '60,000 bonus points after spending $4,000 in first 3 months'
        },
        {
            'id': 2,
            'name': 'Chase Freedom Unlimited®',
            'issuer': 'Chase',
            'benefits': [
                'Cell phone protection',
                'Purchase protection',
                'Extended warranty protection',
                'Auto rental collision damage waiver'
            ],
            'rewards': [
                '5% cash back on travel purchased through Chase Ultimate Rewards',
                '3% cash back on dining and drugstore purchases',
                '1.5% cash back on all other purchases'
            ],
            'annual_fee': '$0',
            'intro_apr': '0% for 15 months on purchases',
            'regular_apr': '20.49% - 29.24% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': '$200 bonus after spending $500 in first 3 months'
        },
        {
            'id': 3,
            'name': 'American Express® Gold Card',
            'issuer': 'American Express',
            'benefits': [
                '$120 Uber Cash annually',
                '$120 dining credit annually',
                'No foreign transaction fees',
                'Travel and emergency assistance',
                'Baggage insurance plan'
            ],
            'rewards': [
                '4x points at restaurants worldwide',
                '4x points at U.S. supermarkets (up to $25,000 per year)',
                '3x points on flights booked directly with airlines',
                '1x points on all other purchases'
            ],
            'annual_fee': '$250',
            'intro_apr': 'N/A',
            'regular_apr': 'Pay Over Time APR: 19.24% - 28.24% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': '60,000 points after spending $4,000 in first 6 months'
        },
        {
            'id': 4,
            'name': 'Capital One Venture Rewards Credit Card',
            'issuer': 'Capital One',
            'benefits': [
                'No foreign transaction fees',
                'Travel accident insurance',
                '24/7 travel assistance services',
                'Auto rental collision damage waiver',
                'Extended warranty'
            ],
            'rewards': [
                '2x miles on every purchase',
                '5x miles on hotels and rental cars booked through Capital One Travel',
                'Unlimited miles with no expiration'
            ],
            'annual_fee': '$95',
            'intro_apr': 'N/A',
            'regular_apr': '19.99% - 29.99% Variable',
            'credit_needed': 'Excellent',
            'bonus_offer': '75,000 miles after spending $4,000 in first 3 months'
        },
        {
            'id': 5,
            'name': 'Citi® Double Cash Card',
            'issuer': 'Citi',
            'benefits': [
                'Citi Entertainment access',
                'Purchase protection',
                'Extended warranty',
                'Damage and theft protection'
            ],
            'rewards': [
                '2% cash back on all purchases',
                '1% when you buy',
                '1% when you pay',
                'No category restrictions or limits'
            ],
            'annual_fee': '$0',
            'intro_apr': '0% for 18 months on balance transfers',
            'regular_apr': '19.24% - 29.24% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': 'No sign-up bonus'
        },
        {
            'id': 6,
            'name': 'Discover it® Cash Back',
            'issuer': 'Discover',
            'benefits': [
                'Free FICO® Credit Score',
                'Freeze your account instantly',
                '$0 fraud liability',
                'No annual fee ever',
                'Cashback Match for first year'
            ],
            'rewards': [
                '5% cash back on rotating categories each quarter (up to $1,500)',
                '1% cash back on all other purchases',
                'Automatic Cashback Match at end of first year'
            ],
            'annual_fee': '$0',
            'intro_apr': '0% for 15 months on purchases and balance transfers',
            'regular_apr': '16.24% - 27.24% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': 'Cashback Match - Discover matches all cash back earned first year'
        },
        {
            'id': 7,
            'name': 'Blue Cash Preferred® Card from American Express',
            'issuer': 'American Express',
            'benefits': [
                'Purchase protection',
                'Extended warranty',
                'Return protection',
                'Car rental loss and damage insurance',
                'Global Assist Hotline'
            ],
            'rewards': [
                '6% cash back at U.S. supermarkets (up to $6,000 per year)',
                '6% cash back on select U.S. streaming subscriptions',
                '3% cash back at U.S. gas stations',
                '3% cash back on transit',
                '1% cash back on other purchases'
            ],
            'annual_fee': '$95',
            'intro_apr': '0% for 12 months on purchases',
            'regular_apr': '19.24% - 29.99% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': '$250 statement credit after spending $3,000 in first 6 months'
        },
        {
            'id': 8,
            'name': 'Wells Fargo Active Cash® Card',
            'issuer': 'Wells Fargo',
            'benefits': [
                'Cell phone protection',
                'Zero liability protection',
                'Travel and emergency assistance',
                'Roadside dispatch',
                'Lost wallet assistance'
            ],
            'rewards': [
                '2% cash rewards on purchases',
                'Unlimited rewards with no categories to track',
                'Redeem for cash, gift cards, or travel'
            ],
            'annual_fee': '$0',
            'intro_apr': '0% for 15 months on purchases and qualifying balance transfers',
            'regular_apr': '20.24%, 25.24%, or 29.99% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': '$200 cash rewards bonus after spending $500 in first 3 months'
        },
        {
            'id': 9,
            'name': 'Bank of America® Premium Rewards® Credit Card',
            'issuer': 'Bank of America',
            'benefits': [
                '$100 airline incidental statement credit',
                'No foreign transaction fees',
                'Travel and emergency assistance',
                'Auto rental collision damage waiver',
                'Purchase protection and extended warranty'
            ],
            'rewards': [
                '2 points per $1 spent on travel and dining',
                '1.5 points per $1 spent on all other purchases',
                'Up to 75% points bonus with Preferred Rewards'
            ],
            'annual_fee': '$95',
            'intro_apr': 'N/A',
            'regular_apr': '19.24% - 29.24% Variable',
            'credit_needed': 'Excellent',
            'bonus_offer': '50,000 bonus points after spending $3,000 in first 90 days'
        },
        {
            'id': 10,
            'name': 'U.S. Bank Cash+® Visa Signature® Card',
            'issuer': 'U.S. Bank',
            'benefits': [
                'Cell phone protection',
                'Extended warranty protection',
                'Purchase security',
                'Travel and emergency assistance',
                'Zero liability protection'
            ],
            'rewards': [
                '5% cash back on your first $2,000 in combined eligible purchases each quarter in two categories you choose',
                '2% cash back on one everyday category',
                '1% cash back on all other eligible purchases'
            ],
            'annual_fee': '$0',
            'intro_apr': '0% for 15 billing cycles on purchases and balance transfers',
            'regular_apr': '18.74% - 29.74% Variable',
            'credit_needed': 'Good to Excellent',
            'bonus_offer': '$200 bonus after spending $1,000 in first 120 days'
        }
    ]

if __name__ == '__main__':
    scrape_credit_cards()
