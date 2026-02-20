"""
AUTOMATIC PAGINATION FIXER
This ACTUALLY patches your profiler to support 20, 30, 50+ results

Just run it once: python pagination_auto_patcher.py
"""

import os
import re
from datetime import datetime

def find_profiler():
    """Find which profiler exists"""
    for name in ['final_competitor_profiler_COMPLETE.py', 'final_competitor_profiler_ENHANCED.py']:
        if os.path.exists(name):
            return name
    return None

def create_backup(filename):
    """Create backup with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = f"{filename}.backup_{timestamp}"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Backup: {backup}")
    return backup

def fix_hardcoded_slices(content):
    """Fix [:5] or [:10] hardcoded slices"""
    
    patterns = [
        (r'items\[:5\]', 'items[:max_results]'),
        (r'items\[:10\]', 'items[:max_results]'),
        (r'results\[:5\]', 'results[:max_results]'),
        (r'results\[:10\]', 'results[:max_results]'),
        (r'competitors\[:5\]', 'competitors[:max_results]'),
        (r'competitors\[:10\]', 'competitors[:max_results]'),
    ]
    
    fixes = []
    for old_pattern, new_value in patterns:
        if re.search(old_pattern, content):
            old_match = re.search(old_pattern, content).group(0)
            content = re.sub(old_pattern, new_value, content)
            fixes.append(f"{old_match} → {new_value}")
    
    return content, fixes

def add_google_cse_pagination(content):
    """Add pagination to Google CSE API calls"""
    
    # Find the Google CSE API call
    # Pattern: Building params dict with "num": something
    
    # Look for the specific pattern
    pattern = r'params\s*=\s*\{\s*[^}]*"key":\s*GOOGLE_CSE_API_KEY[^}]*"num":\s*(?:max_results|10|5)[^}]*\}'
    
    if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
        return content, False
    
    # Find the section that makes the API call
    # We need to replace the single call with pagination
    
    old_code_pattern = r'''(params\s*=\s*\{[^}]*"num":[^}]*\}[^}]*
\s*endpoint\s*=[^
]*
\s*resp\s*=[^
]*
\s*.*?data\s*=\s*resp\.json\(\)[^
]*
\s*items\s*=\s*data\.get\("items",\s*\[\]\))'''
    
    new_code = '''# Google CSE pagination - supports 20, 30, 50+ results
    all_results = []
    results_per_page = 10  # Google CSE max per request
    
    # Calculate how many API calls we need
    num_pages = (max_results + results_per_page - 1) // results_per_page
    
    for page in range(num_pages):
        start_index = page * results_per_page + 1  # 1-indexed
        page_size = min(results_per_page, max_results - len(all_results))
        
        params = {
            "key": GOOGLE_CSE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": page_size,
            "start": start_index  # Pagination!
        }
        
        endpoint = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)
        resp = safe_get(endpoint, timeout=10)
        
        if not resp or resp.status_code != 200:
            print(f"  ⚠️  Page {page + 1} failed")
            break
        
        data = resp.json()
        page_items = data.get("items", [])
        
        if not page_items:
            break
        
        all_results.extend(page_items)
        print(f"  📄 Page {page + 1}/{num_pages}: {len(page_items)} results (total: {len(all_results)})")
        
        if len(all_results) >= max_results:
            break
    
    items = all_results[:max_results]'''
    
    if re.search(old_code_pattern, content, re.MULTILINE | re.DOTALL):
        content = re.sub(old_code_pattern, new_code, content, flags=re.MULTILINE | re.DOTALL)
        return content, True
    
    return content, False

def main():
    print("=" * 70)
    print("🔧 AUTOMATIC PAGINATION FIXER")
    print("=" * 70)
    print()
    
    # Find profiler
    profiler = find_profiler()
    if not profiler:
        print("❌ No profiler found!")
        print("   Looking for: final_competitor_profiler_COMPLETE.py")
        print("             or final_competitor_profiler_ENHANCED.py")
        return
    
    print(f"📝 Found: {profiler}")
    print()
    
    # Backup
    print("📦 Creating backup...")
    create_backup(profiler)
    print()
    
    # Read
    print("📖 Reading file...")
    with open(profiler, 'r', encoding='utf-8') as f:
        content = f.read()
    print()
    
    # Fix 1: Hardcoded slices
    print("🔧 Fixing hardcoded result limits...")
    content, slice_fixes = fix_hardcoded_slices(content)
    
    if slice_fixes:
        for fix in slice_fixes:
            print(f"  ✅ {fix}")
    else:
        print("  ℹ️  No hardcoded slices found")
    print()
    
    # Fix 2: Add pagination
    print("🔧 Adding Google CSE pagination...")
    content, pagination_added = add_google_cse_pagination(content)
    
    if pagination_added:
        print("  ✅ Pagination added!")
        print("     Now supports 20, 30, 50+ results")
    else:
        print("  ⚠️  Could not auto-patch pagination")
        print("     (Profiler might have different structure)")
    print()
    
    # Save
    print("💾 Saving changes...")
    with open(profiler, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Saved: {profiler}")
    print()
    
    # Summary
    print("=" * 70)
    print("✨ PATCHING COMPLETE!")
    print("=" * 70)
    print()
    
    if slice_fixes or pagination_added:
        print("✅ Changes made:")
        if slice_fixes:
            print(f"  • Fixed {len(slice_fixes)} hardcoded limit(s)")
        if pagination_added:
            print("  • Added Google CSE pagination")
        print()
        print("🎯 What this means:")
        print("  • Now supports 20, 30, 50+ results")
        print("  • Makes multiple API calls automatically")
        print("  • No more 5 or 10 result limit!")
        print()
        print("🚀 Test it:")
        print(f"  python {profiler}")
        print("  Enter query: law firms miami fl")
        print("  Enter max: 20")
        print("  → Should get 20 results!")
    else:
        print("⚠️  No changes made")
        print()
        print("Manual check needed:")
        print(f"  1. Open {profiler}")
        print('  2. Search for: "[:5]" or "[:10]"')
        print("  3. Search for: Google CSE API call")
        print("  4. Make sure it uses pagination")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
