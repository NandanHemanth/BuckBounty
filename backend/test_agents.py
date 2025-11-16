"""
Test script to run BountyHunter1 and BountyHunter2 agents
Generates JSON files and pushes data to vector DB
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from agents.bounty_hunter_1 import BountyHunter1
from agents.bounty_hunter_2 import BountyHunter2
from dotenv import load_dotenv

load_dotenv()


async def test_bounty_hunter_1():
    """Test BountyHunter1 - Coupon scraping"""
    print("\n" + "="*60)
    print("🎯 TESTING BOUNTYHUNTER1 - COUPON SCRAPER")
    print("="*60 + "\n")

    bh1 = BountyHunter1()

    print(f"📦 Initial coupons loaded: {len(bh1.coupons)}")

    # Run scraping
    print("\n🔍 Starting coupon scraping from all sources...")
    print("   - Gmail (UberEats, DoorDash)")
    print("   - Honey.com")
    print("   - Rakuten.com")
    print()

    await bh1.scrape_all_sources()

    print(f"\n✅ Scraping complete!")
    print(f"📊 Total coupons collected: {len(bh1.coupons)}")

    # Show sample coupons
    if bh1.coupons:
        print("\n📋 Sample coupons (first 5):")
        for i, coupon in enumerate(bh1.coupons[:5], 1):
            print(f"\n   {i}. {coupon['merchant']}")
            print(f"      Source: {coupon['source']}")
            if coupon.get('code'):
                print(f"      Code: {coupon['code']}")
            print(f"      Description: {coupon.get('description', 'N/A')[:60]}...")

    # Check JSON file
    if bh1.coupon_file.exists():
        print(f"\n💾 Coupons saved to: {bh1.coupon_file}")
        print(f"   File size: {bh1.coupon_file.stat().st_size / 1024:.2f} KB")

    return bh1


async def test_bounty_hunter_2():
    """Test BountyHunter2 - Finance news scraping"""
    print("\n" + "="*60)
    print("📊 TESTING BOUNTYHUNTER2 - FINANCE NEWS SCRAPER")
    print("="*60 + "\n")

    bh2 = BountyHunter2()

    print(f"📰 Initial news articles loaded: {len(bh2.news_articles)}")

    # Check if should scrape
    should_scrape = bh2.should_scrape()
    print(f"⏰ Should scrape (24h check): {should_scrape}")

    # Run scraping
    print("\n🔍 Starting finance news scraping from Yahoo Finance...")
    print("   - General market news")
    print("   - Sector-specific news")
    print("   - Economic indicators")
    print()

    await bh2.scrape_finance_news()

    print(f"\n✅ Scraping complete!")
    print(f"📊 Total news articles collected: {len(bh2.news_articles)}")

    # Show sample news
    if bh2.news_articles:
        print("\n📋 Sample news articles (first 5):")
        for i, article in enumerate(bh2.news_articles[:5], 1):
            print(f"\n   {i}. {article['headline'][:60]}...")
            print(f"      Category: {article['category']}")
            print(f"      Source: {article['source']}")
            if article.get('url'):
                print(f"      URL: {article['url'][:50]}...")

    # Check JSON file
    if bh2.news_file.exists():
        print(f"\n💾 News saved to: {bh2.news_file}")
        print(f"   File size: {bh2.news_file.stat().st_size / 1024:.2f} KB")

    # Check last scrape file
    if bh2.last_scrape_file.exists():
        print(f"\n⏰ Last scrape timestamp saved to: {bh2.last_scrape_file}")

    return bh2


async def test_vector_db_integration():
    """Test vector DB integration"""
    print("\n" + "="*60)
    print("💾 TESTING VECTOR DB INTEGRATION")
    print("="*60 + "\n")

    try:
        from vector_db import VectorDB

        vector_db = VectorDB()

        print(f"✅ Vector DB initialized")
        print(f"📊 Is initialized: {vector_db.is_initialized()}")

        # Get stats
        stats = vector_db.get_category_stats()
        print(f"\n📈 Transaction categories in vector DB: {len(stats)}")

        if stats:
            print("\n📋 Top 5 categories by transaction count:")
            sorted_stats = sorted(stats, key=lambda x: x['count'], reverse=True)
            for i, stat in enumerate(sorted_stats[:5], 1):
                print(f"   {i}. {stat['category']}: {stat['count']} transactions, ${stat['total_amount']:.2f}")

        print("\n✅ Vector DB is working correctly!")

    except Exception as e:
        print(f"❌ Error testing vector DB: {e}")


async def main():
    """Main test function"""
    print("\n" + "="*70)
    print(" "*20 + "🚀 AGENT TEST SUITE")
    print("="*70)

    try:
        # Test BountyHunter1
        bh1 = await test_bounty_hunter_1()

        # Wait a bit between tests
        await asyncio.sleep(2)

        # Test BountyHunter2
        bh2 = await test_bounty_hunter_2()

        # Wait a bit
        await asyncio.sleep(2)

        # Test Vector DB
        await test_vector_db_integration()

        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)

        print("\n📁 Generated files:")
        print(f"   - Coupons: {bh1.coupon_file}")
        print(f"   - Finance News: {bh2.news_file}")
        print(f"   - Last Scrape: {bh2.last_scrape_file}")

        print("\n💡 Next steps:")
        print("   1. Start the FastAPI server: python backend/main.py")
        print("   2. Start the Next.js frontend: npm run dev")
        print("   3. Click the MARK agent icon to open the chat interface")
        print("   4. Ask MARK about coupons, deals, or finance news!")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\nSetting up environment...")
    asyncio.run(main())
