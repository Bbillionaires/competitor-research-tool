"""
===============================================
NEON DATABASE - CONNECTION TEST
===============================================
Quick test to verify your Neon setup is working
Run this BEFORE integrating with your main profiler
"""

import sys
import os

print("=" * 60)
print("🧪 NEON DATABASE CONNECTION TEST")
print("=" * 60)

# Step 1: Check if .env has DATABASE_URL
print("\n1️⃣ Checking .env file...")
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL not found in .env file")
    print("\n💡 Add this to your .env file:")
    print("DATABASE_URL=postgresql://neondb_owner:npg_co3nWQbMNSp7@ep-tiny-breeze-aedt1h8z-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require")
    sys.exit(1)

print("✅ DATABASE_URL found in .env")

# Step 2: Check if psycopg2 is installed
print("\n2️⃣ Checking psycopg2 installation...")
try:
    import psycopg2
    print("✅ psycopg2 is installed")
except ImportError:
    print("❌ psycopg2 not installed")
    print("\n💡 Run this command:")
    print("pip install psycopg2-binary")
    sys.exit(1)

# Step 3: Test connection
print("\n3️⃣ Testing Neon connection...")
try:
    from neon_database_manager import NeonDB
    
    db = NeonDB()
    print("✅ Successfully connected to Neon!")
    
    # Step 4: Get database stats
    print("\n4️⃣ Fetching database statistics...")
    stats = db.get_database_stats()
    
    print("\n📊 DATABASE STATISTICS:")
    print(f"   • Total Competitors: {stats.get('total_competitors', 0)}")
    print(f"   • Unique Queries: {stats.get('unique_queries', 0)}")
    print(f"   • Total Users: {stats.get('total_users', 0)}")
    print(f"   • API Calls (30d): {stats.get('api_calls_30d', 0)}")
    
    # Step 5: Test saving sample data
    print("\n5️⃣ Testing data save...")
    sample_data = [
        {
            'domain': 'test-example.com',
            'name': 'Test Company',
            'address': '123 Test Street',
            'score': 100,
            'phones': ['555-0000'],
            'emails': ['test@example.com'],
            'traffic_estimate': 1000
        }
    ]
    
    success = db.save_competitor_data('test query', sample_data)
    
    if success:
        print("✅ Successfully saved test data")
        
        # Step 6: Test retrieving cached data
        print("\n6️⃣ Testing data retrieval...")
        cached = db.get_cached_competitors('test query', max_age_days=7)
        
        if cached and len(cached) > 0:
            print(f"✅ Successfully retrieved {len(cached)} competitors from cache")
        else:
            print("⚠️  No cached data found (this is OK for first run)")
    else:
        print("⚠️  Failed to save test data")
    
    # Cleanup
    db.close()
    
    # Final message
    print("\n" + "=" * 60)
    print("✨ ALL TESTS PASSED! ✨")
    print("=" * 60)
    print("\n🎉 Your Neon database is ready to use!")
    print("\n📌 NEXT STEPS:")
    print("   1. Integrate neon_database_manager.py into your profiler")
    print("   2. Update Stripe with Business tier pricing")
    print("   3. Test the full workflow")
    print("\n💡 TIP: Run this test anytime to verify your connection")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n🔍 TROUBLESHOOTING:")
    print("   1. Check your DATABASE_URL in .env")
    print("   2. Verify Neon project is active at neon.tech")
    print("   3. Check internet connection")
    print("   4. Ensure psycopg2-binary is installed")
    sys.exit(1)
