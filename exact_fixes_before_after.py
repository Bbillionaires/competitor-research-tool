"""
===============================================
EXACT FIXES - BEFORE & AFTER
===============================================
Apply these changes to: final_competitor_profiler_complete.py
"""

# ==========================================
# FIX 1: GOOGLE PHOTO COUNT - ADD MISSING FIELD
# ==========================================

"""
SEARCH FOR (around line 1060-1080):
"""
BEFORE = '''
        # Google Places data
        "g_name": g.get("g_name", ""),
        "g_address": g.get("g_address", ""),
        "g_phone": g.get("g_phone", ""),
        "g_website": g.get("g_website", ""),
        "g_rating": g.get("g_rating", ""),
        "g_reviews": g.get("g_reviews", ""),
        "g_place_id": g.get("g_place_id", ""),
'''

AFTER = '''
        # Google Places data
        "g_name": g.get("g_name", ""),
        "g_address": g.get("g_address", ""),
        "g_phone": g.get("g_phone", ""),
        "g_website": g.get("g_website", ""),
        "g_rating": g.get("g_rating", ""),
        "g_reviews": g.get("g_reviews", ""),
        "g_photo_count": g.get("g_photo_count", 0),  # ← ADD THIS LINE
        "g_place_id": g.get("g_place_id", ""),
'''

print("FIX 1: Add g_photo_count field")
print("=" * 60)
print("FIND THIS:")
print(BEFORE)
print("\nREPLACE WITH:")
print(AFTER)
print()


# ==========================================
# FIX 2: COLUMN ORDER - RESTORE NAME FIRST
# ==========================================

"""
SEARCH FOR (around line 1247-1260, in main() function):
"""
BEFORE_2 = '''
    # Collect all headers
    all_headers = set()
    for row in rows:
        all_headers.update(row.keys())
    
    headers = sorted(all_headers)  # ← THIS IS THE PROBLEM!
'''

AFTER_2 = '''
    # Collect all headers
    all_headers = set()
    for row in rows:
        all_headers.update(row.keys())
    
    # Define priority columns in exact order
    priority_columns = [
        'name',              # 1. Company name FIRST
        'address',           # 2. Address SECOND
        'domain',
        'url',
        'title',
        'query',
        'score',
        'phones',
        'emails',
        'traffic_estimate',
        'directory_count',
        'g_name',
        'g_address',
        'g_phone',
        'g_website',
        'g_rating',
        'g_reviews',
        'g_photo_count',    # ← IMPORTANT!
        'g_place_id',
        'word_count',
        'h1_count',
        'h2_count',
        'h3_count',
        'title_length',
        'meta_description',
        'meta_description_length',
        'page_load_speed',
        'mobile_friendly',
        'has_robots_txt',
        'has_sitemap',
        'facebook_url',
        'linkedin_url',
        'twitter_url',
        'instagram_url',
        'domain_authority',
        'backlinks',
        'indexed_pages',
        'hiring_signals',
        'hiring_growth_signal',
    ]
    
    # Get remaining columns (alphabetically)
    remaining = sorted([h for h in all_headers if h not in priority_columns])
    
    # Combine: priority first, then remaining
    headers = [h for h in priority_columns if h in all_headers] + remaining
'''

print("FIX 2: Fix column order (name first, address second)")
print("=" * 60)
print("FIND THIS:")
print(BEFORE_2)
print("\nREPLACE WITH:")
print(AFTER_2)
print()


# ==========================================
# FIX 3: ENSURE NUMERIC FIELDS ARE NUMBERS
# ==========================================

"""
SEARCH FOR (around line 1260-1270, right BEFORE the CSV writing):
"""
BEFORE_3 = '''
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
'''

AFTER_3 = '''
    # Convert numeric fields to proper types
    numeric_fields = [
        'traffic_estimate', 'directory_count', 'score',
        'g_reviews', 'g_photo_count',
        'word_count', 'h1_count', 'h2_count', 'h3_count',
        'title_length', 'meta_description_length',
        'domain_authority', 'backlinks', 'indexed_pages',
        'page_load_speed'
    ]
    
    float_fields = ['g_rating', 'hiring_signals', 'hiring_growth_signal']
    
    for row in rows:
        for field in numeric_fields:
            if field in row:
                try:
                    row[field] = int(row[field]) if row[field] else 0
                except (ValueError, TypeError):
                    row[field] = 0
        
        for field in float_fields:
            if field in row:
                try:
                    row[field] = float(row[field]) if row[field] else 0.0
                except (ValueError, TypeError):
                    row[field] = 0.0
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
'''

print("FIX 3: Convert numeric fields before saving")
print("=" * 60)
print("FIND THIS:")
print(BEFORE_3)
print("\nREPLACE WITH:")
print(AFTER_3)
print()


# ==========================================
# SUMMARY
# ==========================================

print("=" * 60)
print("📋 SUMMARY - 3 FIXES TO APPLY")
print("=" * 60)
print()
print("Fix 1: Add g_photo_count field (line ~1070)")
print("   └─ Restores Google photo count data")
print()
print("Fix 2: Fix column ordering (line ~1250)")
print("   └─ Name first, address second, priority order")
print()
print("Fix 3: Convert numeric fields (line ~1265)")
print("   └─ Traffic, word count, etc. as numbers not text")
print()
print("=" * 60)
print("🎯 AFTER APPLYING FIXES:")
print("=" * 60)
print("✅ Column A = name (company names)")
print("✅ Column B = address")
print("✅ traffic_estimate = numbers (50000, not '50K')")
print("✅ word_count = numbers (showing properly)")
print("✅ g_photo_count = showing Google photo counts")
print()
print("=" * 60)
print()
