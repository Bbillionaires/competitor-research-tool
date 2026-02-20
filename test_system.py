#!/usr/bin/env python3
"""
System Test Script - Verify All Integrations
Tests: Neon DB, Google APIs, Stripe, and Phase 1 Enhancements
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Load environment variables
load_dotenv()

def test_neon_connection():
    """Test Neon database connection"""
    print("\n🗄️  Testing Neon Database Connection...")
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("   ❌ DATABASE_URL not found in .env")
            return False
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"   ✅ Connected to Neon PostgreSQL")
        print(f"   📊 Version: {version[0][:50]}...")
        
        # Test if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"   ✅ Found {len(tables)} existing table(s)")
        else:
            print("   ⚠️  No tables yet (will be created on first run)")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_google_apis():
    """Test Google API keys"""
    print("\n🔍 Testing Google APIs...")
    
    # Test CSE API
    cse_key = os.getenv('GOOGLE_CSE_API_KEY')
    cse_id = os.getenv('GOOGLE_CSE_ID')
    if cse_key and cse_id:
        try:
            url = f"https://www.googleapis.com/customsearch/v1?key={cse_key}&cx={cse_id}&q=test"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                print("   ✅ Google CSE API working")
            else:
                print(f"   ❌ Google CSE API error: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Google CSE API error: {str(e)[:50]}")
    else:
        print("   ❌ Google CSE API keys missing")
    
    # Test Places API
    places_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if places_key:
        try:
            url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=test&inputtype=textquery&key={places_key}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                print("   ✅ Google Places API working")
            else:
                print(f"   ❌ Google Places API error: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Google Places API error: {str(e)[:50]}")
    else:
        print("   ❌ Google Places API key missing")
    
    # Test PageSpeed API
    pagespeed_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
    if pagespeed_key:
        try:
            url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&key={pagespeed_key}"
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                print("   ✅ Google PageSpeed API working")
            else:
                print(f"   ⚠️  Google PageSpeed API: {resp.status_code} (may need to enable in console)")
        except Exception as e:
            print(f"   ❌ Google PageSpeed API error: {str(e)[:50]}")
    else:
        print("   ⚠️  Google PageSpeed API key missing (Phase 1 feature)")

def test_stripe():
    """Test Stripe configuration"""
    print("\n💳 Testing Stripe Configuration...")
    
    secret_key = os.getenv('STRIPE_SECRET_KEY')
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if secret_key:
        if secret_key.startswith('sk_live_'):
            print("   ✅ Stripe SECRET key found (LIVE mode)")
        elif secret_key.startswith('sk_test_'):
            print("   ⚠️  Stripe SECRET key found (TEST mode)")
        else:
            print("   ❌ Invalid Stripe SECRET key format")
    else:
        print("   ❌ Stripe SECRET key missing")
    
    if publishable_key:
        if publishable_key.startswith('pk_live_'):
            print("   ✅ Stripe PUBLISHABLE key found (LIVE mode)")
        elif publishable_key.startswith('pk_test_'):
            print("   ⚠️  Stripe PUBLISHABLE key found (TEST mode)")
        else:
            print("   ❌ Invalid Stripe PUBLISHABLE key format")
    else:
        print("   ⚠️  Stripe PUBLISHABLE key missing (needed for frontend)")
    
    if webhook_secret:
        print("   ✅ Stripe WEBHOOK secret found")
    else:
        print("   ⚠️  Stripe WEBHOOK secret missing (needed for subscriptions)")
    
    # Check Price IDs
    pro_price = os.getenv('STRIPE_PRICE_ID_PRO')
    business_price = os.getenv('STRIPE_PRICE_ID_BUSINESS')
    enterprise_price = os.getenv('STRIPE_PRICE_ID_ENTERPRISE')
    
    if pro_price and pro_price.startswith('price_'):
        print("   ✅ Pro Price ID configured correctly")
    elif pro_price and pro_price.startswith('prod_'):
        print("   ❌ Pro Price ID is PRODUCT ID (need price_xxx not prod_xxx)")
    else:
        print("   ⚠️  Pro Price ID missing")
    
    if business_price and business_price.startswith('price_'):
        print("   ✅ Business Price ID configured correctly")
    else:
        print("   ⚠️  Business Price ID missing")
    
    if enterprise_price and enterprise_price.startswith('price_'):
        print("   ✅ Enterprise Price ID configured correctly")
    elif enterprise_price and enterprise_price.startswith('prod_'):
        print("   ❌ Enterprise Price ID is PRODUCT ID (need price_xxx not prod_xxx)")
    else:
        print("   ⚠️  Enterprise Price ID missing")

def test_optional_apis():
    """Test optional API integrations"""
    print("\n🔧 Testing Optional APIs...")
    
    apis = {
        'Hunter.io': os.getenv('HUNTER_API_KEY'),
        'DeepSeek AI': os.getenv('DEEPSEEK_API_KEY'),
        'OpenPageRank': os.getenv('OPENPAGERANK_API_KEY'),
        'Brave Search': os.getenv('BRAVE_SEARCH_API_KEY'),
        'SerpApi': os.getenv('SERPAPI_KEY'),
        'ScraperAPI': os.getenv('SCRAPERAPI_KEY'),
        'RapidAPI': os.getenv('RAPIDAPI_KEY'),
        'Apify': os.getenv('APIFY_API_TOKEN'),
    }
    
    for name, key in apis.items():
        if key:
            print(f"   ✅ {name} configured")
        else:
            print(f"   ⚠️  {name} not configured (optional)")

def summary_report():
    """Generate summary report"""
    print("\n" + "="*60)
    print("📋 SYSTEM STATUS SUMMARY")
    print("="*60)
    
    critical_missing = []
    
    if not os.getenv('DATABASE_URL'):
        critical_missing.append("DATABASE_URL (Neon)")
    if not os.getenv('GOOGLE_CSE_API_KEY'):
        critical_missing.append("GOOGLE_CSE_API_KEY")
    if not os.getenv('GOOGLE_PLACES_API_KEY'):
        critical_missing.append("GOOGLE_PLACES_API_KEY")
    
    if critical_missing:
        print("\n❌ CRITICAL ITEMS MISSING:")
        for item in critical_missing:
            print(f"   • {item}")
        print("\n⚠️  System cannot run without these!")
    else:
        print("\n✅ All critical components configured!")
    
    warnings = []
    if not os.getenv('GOOGLE_PAGESPEED_API_KEY'):
        warnings.append("GOOGLE_PAGESPEED_API_KEY (Phase 1 SEO features)")
    if not os.getenv('STRIPE_PUBLISHABLE_KEY'):
        warnings.append("STRIPE_PUBLISHABLE_KEY (payment frontend)")
    
    pro_price = os.getenv('STRIPE_PRICE_ID_PRO')
    if pro_price and pro_price.startswith('prod_'):
        warnings.append("Stripe Price IDs (using product IDs instead)")
    
    if warnings:
        print("\n⚠️  RECOMMENDED ADDITIONS:")
        for item in warnings:
            print(f"   • {item}")
    
    print("\n" + "="*60)
    print("🚀 Next Steps:")
    print("="*60)
    if not critical_missing:
        print("1. Run: python final_competitor_profiler_complete.py")
        print("2. Test search query: 'real estate investor jacksonville fl'")
        print("3. Check CSV output for JWB and proper column order")
        print("4. Upload CSV to dark space dashboard")
    else:
        print("1. Add missing items to .env file")
        print("2. Run this test script again")
        print("3. Proceed when all ✅ show green")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n🧪 COMPETITOR PROFILER - SYSTEM TEST")
    print("="*60)
    
    # Run all tests
    test_neon_connection()
    test_google_apis()
    test_stripe()
    test_optional_apis()
    
    # Generate summary
    summary_report()
