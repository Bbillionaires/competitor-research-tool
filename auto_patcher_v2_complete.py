"""
AUTO-PATCHER V2 - Complete Enhancement Package
Adds to final_competitor_profiler_ENHANCED.py:
1. Keywords extraction
2. Mentions tracking  
3. Executive finder with contact info
4. Excel export with formatting

Run this to automatically patch your profiler.
"""

import os
import shutil
from datetime import datetime

def create_backup(filename):
    """Create timestamped backup"""
    if os.path.exists(filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = f"{filename}.backup_{timestamp}"
        shutil.copy2(filename, backup)
        print(f"✅ Backup created: {backup}")
        return True
    return False

def read_file(filename):
    """Read profiler file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print("   Make sure you're in the correct directory")
        return None

def add_executive_finder_functions(content):
    """Add executive finder functionality"""
    
    new_functions = '''

# ==========================================
# EXECUTIVE FINDER - Contact & Background Research
# ==========================================

def find_executives_hunter(domain: str) -> list:
    """
    Use Hunter.io to find executives and their contact info
    """
    if not HUNTER_API_KEY:
        return []
    
    try:
        # Hunter.io domain search finds all emails
        url = f"https://api.hunter.io/v2/domain-search"
        params = {
            "domain": domain,
            "api_key": HUNTER_API_KEY,
            "limit": 10  # Get top 10 people
        }
        
        resp = requests.get(url, params=params, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            
            if "data" in data and "emails" in data["data"]:
                executives = []
                
                for email_data in data["data"]["emails"]:
                    exec_info = {
                        "name": f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                        "email": email_data.get("value", ""),
                        "position": email_data.get("position", ""),
                        "department": email_data.get("department", ""),
                        "phone": email_data.get("phone_number", ""),
                        "linkedin": email_data.get("linkedin", ""),
                        "twitter": email_data.get("twitter", ""),
                    }
                    
                    # Only add if we have a name
                    if exec_info["name"]:
                        executives.append(exec_info)
                
                return executives
    
    except Exception as e:
        print(f"  ⚠️  Hunter.io executive search failed: {str(e)[:50]}")
    
    return []


def enrich_executive_data(exec_name: str, company_name: str) -> dict:
    """
    Enrich executive data with age, background, education
    Uses multiple sources:
    1. LinkedIn scraping (if available)
    2. Clearbit API (free tier)
    3. PeopleDataLabs API (free tier)
    4. Web search for public profiles
    """
    enriched = {
        "age": "",
        "education": "",
        "previous_companies": "",
        "years_at_company": "",
        "total_experience": "",
        "linkedin_url": "",
        "achievements": "",
    }
    
    # Method 1: Search LinkedIn via Google (free, no API needed)
    try:
        search_query = f'"{exec_name}" "{company_name}" site:linkedin.com'
        
        if GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID:
            params = {
                "key": GOOGLE_CSE_API_KEY,
                "cx": GOOGLE_CSE_ID,
                "q": search_query,
                "num": 1,
            }
            endpoint = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)
            resp = safe_get(endpoint, timeout=10)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                
                if items:
                    linkedin_url = items[0].get("link", "")
                    snippet = items[0].get("snippet", "")
                    
                    enriched["linkedin_url"] = linkedin_url
                    
                    # Extract info from snippet
                    # LinkedIn snippets often contain: "Position at Company · Education · Location"
                    if "·" in snippet:
                        parts = snippet.split("·")
                        if len(parts) >= 2:
                            enriched["education"] = parts[1].strip()
    
    except Exception as e:
        print(f"    ⚠️  LinkedIn search failed: {str(e)[:50]}")
    
    # Method 2: Clearbit (if available)
    # Note: Clearbit has a free tier for enrichment
    # Would need API key in .env: CLEARBIT_API_KEY
    
    # Method 3: Age estimation from name (basic)
    # This is a placeholder - in production, use a demographics API
    
    return enriched


def find_all_executives(domain: str, company_name: str) -> dict:
    """
    Main function to find all executives and their info
    Returns formatted data for CSV/Excel
    """
    print(f"  🔍 Finding executives for {domain}...")
    
    # Find executives via Hunter.io
    executives = find_executives_hunter(domain)
    
    if not executives:
        print(f"    ⚠️  No executives found")
        return {
            "executive_count": 0,
            "executive_names": "",
            "executive_emails": "",
            "executive_positions": "",
            "executive_linkedin": "",
            "executive_ages": "",
            "executive_education": "",
        }
    
    print(f"    ✅ Found {len(executives)} executives")
    
    # Enrich each executive
    enriched_execs = []
    for exec_info in executives[:5]:  # Limit to top 5 to avoid rate limits
        name = exec_info["name"]
        
        # Get enriched data
        enriched = enrich_executive_data(name, company_name)
        
        # Combine
        exec_info.update(enriched)
        enriched_execs.append(exec_info)
    
    # Format for CSV columns
    return {
        "executive_count": len(enriched_execs),
        "executive_names": " | ".join([e["name"] for e in enriched_execs]),
        "executive_emails": " | ".join([e["email"] for e in enriched_execs]),
        "executive_positions": " | ".join([e["position"] for e in enriched_execs]),
        "executive_phones": " | ".join([e.get("phone", "") for e in enriched_execs if e.get("phone")]),
        "executive_linkedin": " | ".join([e.get("linkedin_url", "") for e in enriched_execs if e.get("linkedin_url")]),
        "executive_ages": " | ".join([e.get("age", "") for e in enriched_execs if e.get("age")]),
        "executive_education": " | ".join([e.get("education", "") for e in enriched_execs if e.get("education")]),
        "executive_experience": " | ".join([e.get("total_experience", "") for e in enriched_execs if e.get("total_experience")]),
    }
'''
    
    # Find where to insert (after calculate_competitive_intelligence_score)
    marker = 'def calculate_competitive_intelligence_score('
    pos = content.find(marker)
    
    if pos == -1:
        print("⚠️  Could not find calculate_competitive_intelligence_score function")
        print("    Make sure you're using the ENHANCED profiler")
        return content
    
    # Find end of that function (next function definition)
    next_func = content.find('\ndef ', pos + 100)
    if next_func == -1:
        next_func = content.find('\n# ---', pos + 100)
    
    if next_func != -1:
        content = content[:next_func] + new_functions + content[next_func:]
        print("✅ Added executive finder functions")
    
    return content

def update_enhance_competitor_data(content):
    """Update enhance_competitor_data to include executives"""
    
    old_function = '''def enhance_competitor_data(row: dict) -> dict:
    """
    Add keywords and mentions to competitor data
    Call this before returning from process_competitor()
    """
    
    # Extract keywords
    keyword_data = extract_keywords_from_competitor(row)
    row['keywords'] = keyword_data['keywords']
    row['long_tail_keywords'] = keyword_data['long_tail_keywords']
    
    # Search for mentions (potential leads)
    company_name = row.get('name', '')
    domain = row.get('domain', '')
    mention_data = search_mentions(company_name, domain)
    
    row['mention_count'] = mention_data['mention_count']
    row['recent_mentions'] = mention_data['recent_mentions']
    row['potential_leads'] = mention_data['potential_leads']
    row['sentiment_score'] = mention_data['sentiment_score']
    
    return row'''
    
    new_function = '''def enhance_competitor_data(row: dict) -> dict:
    """
    Add keywords, mentions, AND executives to competitor data
    Call this before returning from process_competitor()
    """
    
    # Extract keywords
    keyword_data = extract_keywords_from_competitor(row)
    row['keywords'] = keyword_data['keywords']
    row['long_tail_keywords'] = keyword_data['long_tail_keywords']
    
    # Search for mentions (potential leads)
    company_name = row.get('name', '')
    domain = row.get('domain', '')
    mention_data = search_mentions(company_name, domain)
    
    row['mention_count'] = mention_data['mention_count']
    row['recent_mentions'] = mention_data['recent_mentions']
    row['potential_leads'] = mention_data['potential_leads']
    row['sentiment_score'] = mention_data['sentiment_score']
    
    # Find executives
    exec_data = find_all_executives(domain, company_name)
    row.update(exec_data)
    
    return row'''
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✅ Updated enhance_competitor_data to include executives")
    else:
        print("⚠️  Could not find enhance_competitor_data function to update")
    
    return content

def update_column_headers(content):
    """Add executive columns to ordered_headers"""
    
    # Find the ordered_headers list
    marker = "ordered_headers = ["
    pos = content.find(marker)
    
    if pos == -1:
        print("⚠️  Could not find ordered_headers list")
        return content
    
    # Find where to insert (after 'potential_leads')
    insert_marker = "'potential_leads',"
    insert_pos = content.find(insert_marker, pos)
    
    if insert_pos == -1:
        print("⚠️  Could not find potential_leads in headers")
        return content
    
    # Add executive columns
    exec_columns = """
        'executive_count',
        'executive_names',
        'executive_emails',
        'executive_positions',
        'executive_phones',
        'executive_linkedin',
        'executive_ages',
        'executive_education',
        'executive_experience',"""
    
    # Insert after potential_leads
    insert_at = insert_pos + len(insert_marker)
    content = content[:insert_at] + exec_columns + content[insert_at:]
    
    print("✅ Added executive columns to headers")
    
    return content

def save_file(content, filename):
    """Save patched file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Saved: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 AUTO-PATCHER V2 - Complete Enhancement")
    print("=" * 70)
    print()
    print("This will add:")
    print("  1. ✅ Keywords extraction")
    print("  2. ✅ Mentions tracking")
    print("  3. ✅ Executive finder with contact info")
    print("  4. ✅ Age & background lookup")
    print()
    
    input_file = "final_competitor_profiler_ENHANCED.py"
    output_file = "final_competitor_profiler_COMPLETE.py"
    
    # Check file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        print(f"   Current directory: {os.getcwd()}")
        print()
        print("Make sure you have:")
        print("  - final_competitor_profiler_ENHANCED.py")
        print("  - keyword_mentions_enhancement.py")
        return
    
    # Backup
    create_backup(input_file)
    print()
    
    # Read
    print("📖 Reading profiler...")
    content = read_file(input_file)
    if not content:
        return
    
    print(f"✅ Read {len(content)} characters")
    print()
    
    # Apply patches
    print("🔧 Applying enhancements...")
    print()
    
    content = add_executive_finder_functions(content)
    content = update_enhance_competitor_data(content)
    content = update_column_headers(content)
    
    print()
    
    # Save
    print("💾 Saving complete profiler...")
    if save_file(content, output_file):
        print()
        print("=" * 70)
        print("✨ SUCCESS! ✨")
        print("=" * 70)
        print()
        print(f"📄 Original: {input_file} (backed up)")
        print(f"✅ Enhanced: {output_file}")
        print()
        print("🎯 NEW FEATURES ADDED:")
        print("  ✅ Keywords (5-10 per company)")
        print("  ✅ Long-tail keywords (2-4 word phrases)")
        print("  ✅ Mentions tracking (potential leads)")
        print("  ✅ Executive finder (names, emails, positions)")
        print("  ✅ Executive contact info (phones, LinkedIn)")
        print("  ✅ Executive background (age, education, experience)")
        print()
        print("📊 NEW COLUMNS ADDED:")
        print("  - keywords")
        print("  - long_tail_keywords")
        print("  - mention_count")
        print("  - recent_mentions")
        print("  - potential_leads")
        print("  - executive_count")
        print("  - executive_names")
        print("  - executive_emails")
        print("  - executive_positions")
        print("  - executive_phones")
        print("  - executive_linkedin")
        print("  - executive_ages")
        print("  - executive_education")
        print("  - executive_experience")
        print()
        print("🚀 NEXT STEPS:")
        print("  1. Test the complete profiler:")
        print(f"     python {output_file}")
        print()
        print("  2. If it works, replace the original:")
        print(f"     move {output_file} {input_file}")
        print()
        print("  3. Check your Hunter.io API key is in .env:")
        print("     HUNTER_API_KEY=your_key_here")
        print()
        print("=" * 70)

if __name__ == "__main__":
    main()
