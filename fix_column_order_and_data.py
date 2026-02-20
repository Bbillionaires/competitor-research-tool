"""
===============================================
FIX: Column Order & Missing Data Issues
===============================================

PROBLEMS IDENTIFIED:
1. ❌ Name column not showing first anymore
2. ❌ Traffic not showing proper values
3. ❌ Word count and other data missing
4. ❌ Google photo count disappeared

ROOT CAUSE:
The column ordering got messed up during integration changes.
Some data fields are not being collected or saved properly.

SOLUTION:
Complete fix for final_competitor_profiler_complete.py
"""

# ==========================================
# FIX 1: COLUMN ORDER - RESTORE PROPER ORDER
# ==========================================
# LOCATION: Near the end of main() function, around line 1247-1260

# BEFORE (WRONG):
"""
headers = sorted(all_headers)  # This alphabetizes everything!
"""

# AFTER (CORRECT):
"""
# Define priority columns in exact order
priority_columns = [
    'name',              # 1. Company name FIRST
    'address',           # 2. Address SECOND
    'domain',            # 3. Domain
    'url',               # 4. Full URL
    'title',             # 5. Page title
    'query',             # 6. Search query used
    'score',             # 7. Relevance score
    
    # Contact info
    'phones',
    'emails',
    
    # Business metrics
    'traffic_estimate',
    'directory_count',
    
    # Google data
    'g_name',
    'g_address',
    'g_phone',
    'g_website',
    'g_rating',
    'g_reviews',
    'g_photo_count',     # THIS WAS MISSING!
    'g_place_id',
    
    # SEO metrics
    'word_count',
    'h1_count',
    'h2_count',
    'h3_count',
    'title_length',
    'meta_description',
    'meta_description_length',
    
    # Technical
    'page_load_speed',
    'mobile_friendly',
    'has_robots_txt',
    'has_sitemap',
    
    # Social
    'facebook_url',
    'linkedin_url',
    'twitter_url',
    'instagram_url',
    
    # Other metrics
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
"""


# ==========================================
# FIX 2: ENSURE TRAFFIC_ESTIMATE IS NUMERIC
# ==========================================
# LOCATION: In process_competitor() function, around line 1120

# FIND THIS LINE:
"""
row["traffic_estimate"] = estimate_traffic(row)
"""

# MAKE SURE IT COMES AFTER THIS LINE:
"""
row = {
    "name": g.get("g_name", "") or title,
    "address": g.get("g_address", ""),
    "domain": domain,
    "url": url,
    "title": title,
    "query": query,
    # ... other fields
}
"""

# ADD THIS RIGHT AFTER THE row DICTIONARY IS CREATED:
"""
# Calculate traffic estimate (numeric value)
row["traffic_estimate"] = estimate_traffic(row)

# Ensure it's an integer, not a string
if isinstance(row["traffic_estimate"], str):
    # Convert text estimates to numbers
    traffic_str = row["traffic_estimate"].lower()
    if 'k' in traffic_str:
        # "50K" -> 50000
        row["traffic_estimate"] = int(float(traffic_str.replace('k', '').strip()) * 1000)
    elif 'm' in traffic_str:
        # "1.5M" -> 1500000
        row["traffic_estimate"] = int(float(traffic_str.replace('m', '').strip()) * 1000000)
    elif traffic_str == 'n/a' or not traffic_str:
        row["traffic_estimate"] = 0
    else:
        try:
            row["traffic_estimate"] = int(traffic_str)
        except:
            row["traffic_estimate"] = 0
"""


# ==========================================
# FIX 3: ENSURE GOOGLE PHOTO COUNT IS SAVED
# ==========================================
# LOCATION: In process_competitor() function, where Google data is processed

# FIND THE SECTION WHERE GOOGLE PLACES DATA IS SAVED:
"""
# Google Places data
"g_name": g.get("g_name", ""),
"g_address": g.get("g_address", ""),
"g_phone": g.get("g_phone", ""),
"g_website": g.get("g_website", ""),
"g_rating": g.get("g_rating", ""),
"g_reviews": g.get("g_reviews", ""),
"g_place_id": g.get("g_place_id", ""),
"""

# ADD THIS LINE:
"""
# Google Places data
"g_name": g.get("g_name", ""),
"g_address": g.get("g_address", ""),
"g_phone": g.get("g_phone", ""),
"g_website": g.get("g_website", ""),
"g_rating": g.get("g_rating", ""),
"g_reviews": g.get("g_reviews", ""),
"g_photo_count": g.get("g_photo_count", 0),  # ADD THIS LINE!
"g_place_id": g.get("g_place_id", ""),
"""


# ==========================================
# FIX 4: ENSURE WORD COUNT IS COLLECTED
# ==========================================
# LOCATION: In process_competitor() function, scraping section

# FIND WHERE word_count IS SET:
"""
"word_count": len(soup.get_text().split()) if soup else 0,
"""

# MAKE SURE IT'S ACTUALLY BEING SAVED TO THE ROW:
"""
# Content analysis
row["word_count"] = len(soup.get_text().split()) if soup else 0
row["h1_count"] = len(soup.find_all('h1')) if soup else 0
row["h2_count"] = len(soup.find_all('h2')) if soup else 0
row["h3_count"] = len(soup.find_all('h3')) if soup else 0
"""


# ==========================================
# FIX 5: ENSURE ALL NUMERIC FIELDS ARE NUMBERS
# ==========================================
# LOCATION: Before writing to CSV, in main() function

# ADD THIS SECTION RIGHT BEFORE CSV WRITING:
"""
# Convert numeric fields to proper types
numeric_fields = [
    'traffic_estimate', 'directory_count', 'score',
    'g_rating', 'g_reviews', 'g_photo_count',
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
                if field in float_fields:
                    row[field] = float(row[field]) if row[field] else 0.0
                else:
                    row[field] = int(row[field]) if row[field] else 0
            except (ValueError, TypeError):
                row[field] = 0.0 if field in float_fields else 0
"""


# ==========================================
# COMPLETE FIXED SECTION FOR CSV WRITING
# ==========================================

"""
# ==========================================
# FINAL CSV WRITING SECTION - COPY THIS ENTIRE BLOCK
# ==========================================

def write_csv_with_proper_order(rows, output_file='competitors_final_profile.csv'):
    '''
    Write competitors to CSV with proper column order and data types
    '''
    if not rows:
        print("⚠️  No data to write")
        return
    
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
        
        # Contact
        'phones',
        'emails',
        
        # Metrics
        'traffic_estimate',
        'directory_count',
        
        # Google Places
        'g_name',
        'g_address',
        'g_phone',
        'g_website',
        'g_rating',
        'g_reviews',
        'g_photo_count',    # IMPORTANT!
        'g_place_id',
        
        # SEO
        'word_count',
        'h1_count',
        'h2_count',
        'h3_count',
        'title_length',
        'meta_description',
        'meta_description_length',
        
        # Technical
        'page_load_speed',
        'mobile_friendly',
        'has_robots_txt',
        'has_sitemap',
        
        # Social
        'facebook_url',
        'linkedin_url',
        'twitter_url',
        'instagram_url',
        
        # Other
        'domain_authority',
        'backlinks',
        'indexed_pages',
        'hiring_signals',
        'hiring_growth_signal',
    ]
    
    # Get remaining columns
    remaining = sorted([h for h in all_headers if h not in priority_columns])
    headers = [h for h in priority_columns if h in all_headers] + remaining
    
    # Convert numeric fields
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
    
    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Saved {len(rows)} competitors to {output_file}")
    print(f"📊 Columns: {len(headers)} data points per competitor")
    print(f"✅ Column order: name first, address second")


# USE THIS FUNCTION IN MAIN():
# Replace the CSV writing section with:
write_csv_with_proper_order(rows, output_file)
"""

print(__doc__)
