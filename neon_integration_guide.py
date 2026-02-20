"""
===============================================
NEON INTEGRATION GUIDE
===============================================
How to add database caching to your existing profiler
WITHOUT modifying your current code
"""

# ==========================================
# OPTION 1: WRAPPER SCRIPT (RECOMMENDED)
# ==========================================
# Create a new file: run_profiler_with_cache.py
# This wraps your existing profiler with database caching

import subprocess
import csv
from neon_database_manager import NeonDB

def run_profiler_with_caching():
    """
    Wrapper that adds database caching to your existing profiler
    WITHOUT modifying final_competitor_profiler_complete.py
    """
    
    print("🚀 Starting Competitor Profiler with Database Caching")
    print("=" * 60)
    
    # Initialize database
    db = NeonDB()
    
    # Get search query from user
    query = input("\n🔍 Enter search query: ").strip()
    max_results = input("📊 Max # of results (default 20): ").strip() or "20"
    
    # Check if we have cached data
    print(f"\n🔍 Checking cache for '{query}'...")
    cached_competitors = db.get_cached_competitors(query, max_age_days=7)
    
    if cached_competitors:
        print(f"✅ Found {len(cached_competitors)} cached competitors!")
        print("💾 Using cached data (no API calls needed)")
        
        # Save cached data to CSV
        output_file = 'competitors_final_profile.csv'
        
        if len(cached_competitors) > 0:
            # Get all unique keys
            all_keys = set()
            for comp in cached_competitors:
                all_keys.update(comp.keys())
            
            # Define column order
            priority_columns = [
                'name', 'address', 'domain', 'url', 'title', 'query',
                'phones', 'emails', 'traffic_estimate', 'directory_count',
                'score'
            ]
            remaining = sorted([k for k in all_keys if k not in priority_columns])
            headers = [h for h in priority_columns if h in all_keys] + remaining
            
            # Write CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(cached_competitors)
            
            print(f"✅ Saved to {output_file}")
            print(f"\n💰 API SAVINGS: 100% (used cache instead of fresh search)")
    
    else:
        print("❌ No cached data found - running fresh search...")
        print("🔄 This will use API credits\n")
        
        # Run the original profiler
        result = subprocess.run(
            ['python', 'final_competitor_profiler_complete.py'],
            input=f"{query}\n{max_results}\n",
            text=True,
            capture_output=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            # Load the results
            try:
                with open('competitors_final_profile.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    competitors = list(reader)
                
                if competitors:
                    # Save to database for future caching
                    print(f"\n💾 Saving {len(competitors)} competitors to database...")
                    db.save_competitor_data(query, competitors)
                    print("✅ Data cached for future use!")
                    print("💡 Next search for this query will be instant (up to 7 days)")
            
            except FileNotFoundError:
                print("⚠️  No results file found")
        else:
            print("❌ Profiler failed:", result.stderr)
    
    # Show API usage stats
    print("\n" + "=" * 60)
    print("📊 API USAGE STATISTICS (Last 30 Days)")
    print("=" * 60)
    
    stats = db.get_api_usage_stats(days=30)
    
    if stats.get('by_api'):
        for api in stats['by_api']:
            print(f"   • {api['api_name']}: {api['total_calls']} calls")
    else:
        print("   No API usage tracked yet")
    
    db.close()
    print("\n✅ Done!\n")


# ==========================================
# OPTION 2: DIRECT INTEGRATION
# ==========================================
# Add these lines to your existing profiler

"""
Add to the TOP of final_competitor_profiler_complete.py:

from neon_database_manager import NeonDB

# Initialize database at the start of main()
db = NeonDB()


Add BEFORE running searches:

# Check cache first
cached = db.get_cached_competitors(query, max_age_days=7)
if cached:
    print(f"✅ Using {len(cached)} cached competitors")
    rows = cached
    # Skip to CSV writing section
else:
    print("🔄 Running fresh search...")
    # Continue with normal search logic


Add AFTER saving CSV:

# Save to database
if rows:
    db.save_competitor_data(query, rows)
    print("💾 Results cached for future use")


Add tracking for API calls:

# After each API call (Google CSE, Places, etc.):
db.track_api_call('google_cse', endpoint='/search', query=query)
db.track_api_call('google_places', endpoint='/details', query=domain)
"""


# ==========================================
# OPTION 3: MINIMAL INTEGRATION (3 LINES)
# ==========================================
# Just add these 3 lines to your profiler:

"""
1. At the top (after imports):
   from neon_database_manager import NeonDB
   db = NeonDB()

2. Before CSV writing (in main() function):
   db.save_competitor_data(query, rows)

3. At the end:
   db.close()

That's it! Your data is now automatically cached.
"""


# ==========================================
# USAGE INSTRUCTIONS
# ==========================================

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "=" * 60)
    print("CHOOSE YOUR INTEGRATION METHOD:")
    print("=" * 60)
    print("\n1️⃣  WRAPPER (No code changes)")
    print("   • Create: run_profiler_with_cache.py")
    print("   • Copy the 'OPTION 1' code above")
    print("   • Run: python run_profiler_with_cache.py")
    print("   • Benefits: Zero changes to existing code")
    print()
    print("2️⃣  DIRECT (Full integration)")
    print("   • Modify: final_competitor_profiler_complete.py")
    print("   • Add code from 'OPTION 2' above")
    print("   • Benefits: Better control, track API usage")
    print()
    print("3️⃣  MINIMAL (3 lines)")
    print("   • Modify: final_competitor_profiler_complete.py")
    print("   • Add 3 lines from 'OPTION 3' above")
    print("   • Benefits: Simplest integration")
    print("\n" + "=" * 60)
    print()
    
    choice = input("Choose option (1/2/3) or 'demo' to run wrapper: ").strip()
    
    if choice == '1' or choice.lower() == 'demo':
        print("\n🚀 Running wrapper demo...\n")
        run_profiler_with_caching()
    elif choice == '2':
        print("\n📝 DIRECT INTEGRATION STEPS:")
        print("1. Open final_competitor_profiler_complete.py")
        print("2. Copy code from OPTION 2 section above")
        print("3. Add to appropriate locations in your file")
        print("4. Test with: python final_competitor_profiler_complete.py")
    elif choice == '3':
        print("\n📝 MINIMAL INTEGRATION STEPS:")
        print("1. Open final_competitor_profiler_complete.py")
        print("2. Add these 3 lines:")
        print()
        print("   from neon_database_manager import NeonDB")
        print("   db = NeonDB()")
        print("   db.save_competitor_data(query, rows)  # before CSV writing")
        print()
        print("3. Save and test!")
    else:
        print("Invalid choice. Run again and choose 1, 2, or 3.")


# ==========================================
# TESTING YOUR INTEGRATION
# ==========================================

"""
After integration, test with:

1. First search (will use API):
   🔍 Search: "real estate jacksonville fl"
   ✅ Should save to database
   💰 Uses API credits

2. Second search (should use cache):
   🔍 Search: "real estate jacksonville fl" (same query)
   ✅ Should load from cache
   💰 NO API credits used!
   ⚡ Instant results

3. Check stats:
   python -c "from neon_database_manager import NeonDB; db = NeonDB(); print(db.get_database_stats())"
"""
