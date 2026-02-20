"""
GOOGLE CSE PAGINATION FIXER
Fixes the profiler to correctly fetch 20, 30, or 50 results

The issue: Google CSE API returns max 10 results per call
The fix: Make multiple API calls with pagination

Run this to patch your profiler.
"""

import os
import re

def patch_profiler():
    """Add pagination support to Google CSE calls"""
    
    profiler = None
    for filename in ['final_competitor_profiler_COMPLETE.py', 'final_competitor_profiler_ENHANCED.py']:
        if os.path.exists(filename):
            profiler = filename
            break
    
    if not profiler:
        print("❌ No profiler found")
        return
    
    print(f"📝 Patching: {profiler}")
    print()
    
    with open(profiler, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f"{profiler}.backup_pagination", 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Backup created")
    
    # Find the Google CSE search function
    # Look for the pattern where we build the Google CSE URL
    
    # Pattern 1: Check if there's already pagination
    if 'start=' in content and 'for start_index in range' in content:
        print("✅ Pagination already implemented!")
        return
    
    # Pattern 2: Find where we make the Google API call
    # Common patterns:
    # - params = {"key": ..., "cx": ..., "q": query, "num": max_results}
    # - We need to add pagination here
    
    old_pattern = r'(params\s*=\s*{[^}]*"num":\s*max_results[^}]*})'
    
    if re.search(old_pattern, content):
        print("✅ Found Google CSE params")
        
        # Add pagination logic
        new_code = '''
    # Google CSE pagination - max 10 per request
    all_results = []
    results_per_page = 10
    num_pages = (max_results + results_per_page - 1) // results_per_page  # Ceiling division
    
    for page in range(num_pages):
        start_index = page * results_per_page + 1  # Google CSE is 1-indexed
        page_size = min(results_per_page, max_results - len(all_results))
        
        params = {
            "key": GOOGLE_CSE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": page_size,
            "start": start_index
        }
        
        print(f"  📄 Fetching page {page + 1}/{num_pages} (results {start_index}-{start_index + page_size - 1})")
        
        # Make API call
        endpoint = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)
        resp = safe_get(endpoint, timeout=10)
        
        if not resp or resp.status_code != 200:
            print(f"    ⚠️  Page {page + 1} failed")
            break
        
        data = resp.json()
        items = data.get("items", [])
        
        if not items:
            print(f"    ⚠️  No more results")
            break
        
        all_results.extend(items)
        print(f"    ✅ Got {len(items)} results (total: {len(all_results)})")
        
        if len(all_results) >= max_results:
            break
    
    items = all_results[:max_results]
    print(f"\\n  📊 Total results collected: {len(items)}")
'''
        
        # Find the old single API call and replace it
        # This is tricky - need to find the exact location
        
        print("⚠️  Manual patch required")
        print()
        print("=" * 70)
        print("MANUAL INSTRUCTIONS:")
        print("=" * 70)
        print()
        print("In your profiler, find the Google CSE API call section.")
        print("It looks something like this:")
        print()
        print("```python")
        print('params = {')
        print('    "key": GOOGLE_CSE_API_KEY,')
        print('    "cx": GOOGLE_CSE_ID,')
        print('    "q": query,')
        print('    "num": max_results')
        print('}')
        print('endpoint = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)')
        print('resp = safe_get(endpoint, timeout=10)')
        print('data = resp.json()')
        print('items = data.get("items", [])')
        print("```")
        print()
        print("REPLACE IT WITH:")
        print()
        print(new_code)
        print()
        print("=" * 70)
        
    else:
        print("⚠️  Could not find Google CSE params")
        print("   The profiler might use a different pattern")
        print()
        print("ALTERNATIVE: Check these settings in profiler:")
        print()
        print("1. Search for 'num=' in the file")
        print("2. Make sure it's using max_results, not a hardcoded value")
        print("3. Check if there's a [:5] or [:10] slice limiting results")
        print()
    
    # Additional check - look for result slicing
    slicing_patterns = [
        (r'items\[:5\]', 'items[:5]', 'items[:max_results]'),
        (r'results\[:5\]', 'results[:5]', 'results[:max_results]'),
        (r'competitors\[:5\]', 'competitors[:5]', 'competitors[:max_results]'),
    ]
    
    found_slice = False
    for pattern, old, new in slicing_patterns:
        if re.search(pattern, content):
            print(f"⚠️  Found hardcoded slice: {old}")
            print(f"   Should be: {new}")
            found_slice = True
    
    if found_slice:
        print()
        print("FIX: Search for [:5] and replace with [:max_results]")


if __name__ == "__main__":
    print("=" * 70)
    print("🔧 GOOGLE CSE PAGINATION FIXER")
    print("=" * 70)
    print()
    
    patch_profiler()
    
    print()
    print("=" * 70)
    print("QUICK FIX:")
    print("=" * 70)
    print()
    print("If you're only getting 5 results, check:")
    print()
    print("1. Is there [:5] somewhere limiting results?")
    print('   Search profiler for: "[:5]"')
    print('   Replace with: "[:max_results]"')
    print()
    print("2. Is Google CSE num parameter correct?")
    print('   Search for: "num": ')
    print('   Make sure it uses max_results, not 10 or 5')
    print()
    print("3. Does it make multiple API calls for 20+ results?")
    print("   Google CSE returns max 10 per call")
    print("   Need pagination for more")
    print()
    print("=" * 70)
