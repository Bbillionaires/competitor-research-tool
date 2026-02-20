"""
===============================================
AUTO-PATCHER FOR COMPETITIVE INTELLIGENCE
===============================================

This script will automatically apply all enhancements to your
final_competitor_profiler_complete.py file.

WHAT IT DOES:
1. Backs up your original file
2. Adds extract_company_name_smart() function
3. Adds calculate_competitive_intelligence_score() function
4. Modifies process_competitor() to use smart name extraction
5. Adds CI score calculation to main()
6. Saves as final_competitor_profiler_ENHANCED.py

USAGE:
  python auto_patcher.py

Your original file remains untouched!
"""

import os
import shutil
from datetime import datetime

def backup_original(filename):
    """Create a backup of the original file"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"✅ Backed up original to: {backup_name}")
        return True
    return False

def read_file(filename):
    """Read the current profiler file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found!")
        print(f"   Make sure you're in the correct directory.")
        return None

def apply_patches(content):
    """Apply all patches to the content"""
    
    # ==========================================
    # PATCH 1: Add extract_company_name_smart() function
    # ==========================================
    
    new_function_1 = '''

def extract_company_name_smart(url: str, html: str, soup: BeautifulSoup, title: str, domain: str) -> str:
    """
    Extract company name using multiple fallback methods
    NO GOOGLE PLACES REQUIRED!
    """
    
    # Method 1: OpenGraph site name
    og_site = soup.find("meta", attrs={"property": "og:site_name"})
    if og_site and og_site.get("content"):
        name = og_site.get("content").strip()
        if name and len(name) < 100:
            print(f"  📝 Name from OpenGraph: {name}")
            return name
    
    # Method 2: Schema.org Organization
    try:
        schema_scripts = soup.find_all("script", type="application/ld+json")
        for script in schema_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") == "Organization":
                        name = data.get("name", "")
                        if name and len(name) < 100:
                            print(f"  📝 Name from Schema.org: {name}")
                            return name
                elif isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "Organization":
                            name = item.get("name", "")
                            if name and len(name) < 100:
                                print(f"  📝 Name from Schema.org: {name}")
                                return name
            except:
                pass
    except:
        pass
    
    # Method 3: Parse title intelligently
    if title:
        junk_words = [
            'jacksonville', 'florida', 'fl', 'real estate', 'investor', 'investors',
            'best', 'top', '10', 'list', 'guide', 'home', 'welcome', 'about',
            'commercial', 'residential', 'property', 'properties'
        ]
        
        for separator in [' | ', ' – ', ' - ', '–', '|', '-']:
            if separator in title:
                parts = title.split(separator)
                for part in parts:
                    part = part.strip()
                    lower_part = part.lower()
                    junk_count = sum(1 for word in junk_words if word in lower_part)
                    
                    if junk_count < 2 and 5 < len(part) < 80:
                        print(f"  📝 Name from title parsing: {part}")
                        return part
                break
    
    # Method 4: First H1 tag
    h1 = soup.find("h1")
    if h1:
        h1_text = h1.get_text(strip=True)
        if h1_text and 5 < len(h1_text) < 80:
            if not any(x in h1_text.lower() for x in ['welcome', 'home', 'about', 'contact']):
                print(f"  📝 Name from H1: {h1_text}")
                return h1_text
    
    # Method 5: Domain name cleanup
    name = domain.replace('.com', '').replace('.net', '').replace('.org', '')
    name = name.replace('-', ' ').replace('_', ' ')
    
    if name.startswith('www '):
        name = name[4:]
    
    name = ' '.join(word.capitalize() for word in name.split())
    
    print(f"  📝 Name from domain: {name}")
    return name


def calculate_competitive_intelligence_score(competitors: list) -> dict:
    """
    Calculate industry competitiveness metrics
    Returns difficulty score, saturation level, and market insights
    """
    
    if not competitors:
        return {
            "competitiveness_score": 0,
            "difficulty_rating": "Unknown",
            "market_saturation": "Unknown",
            "insights": []
        }
    
    total_competitors = len(competitors)
    
    avg_word_count = sum(c.get('word_count', 0) for c in competitors) / total_competitors
    sites_with_blog = sum(1 for c in competitors if c.get('word_count', 0) > 1000)
    avg_social_platforms = sum(c.get('social_platform_count', 0) for c in competitors) / total_competitors
    sites_with_ads = sum(1 for c in competitors if c.get('ads_signal', 0) > 0)
    sites_hiring = sum(1 for c in competitors if c.get('hiring_signal', 0) > 0)
    sites_with_schema = sum(1 for c in competitors if c.get('schema_present') == 1)
    avg_internal_links = sum(c.get('internal_links', 0) for c in competitors) / total_competitors
    avg_emails = sum(len(str(c.get('emails', '')).split('|')) for c in competitors) / total_competitors
    
    score = 0
    
    # Market size (0-20)
    if total_competitors >= 20:
        score += 20
    elif total_competitors >= 15:
        score += 15
    elif total_competitors >= 10:
        score += 10
    else:
        score += 5
    
    # Content quality (0-20)
    if avg_word_count > 2000:
        score += 20
    elif avg_word_count > 1000:
        score += 15
    elif avg_word_count > 500:
        score += 10
    else:
        score += 5
    
    # Social presence (0-15)
    if avg_social_platforms >= 3:
        score += 15
    elif avg_social_platforms >= 2:
        score += 10
    else:
        score += 5
    
    # Marketing sophistication (0-15)
    ad_percentage = (sites_with_ads / total_competitors) * 100
    if ad_percentage > 70:
        score += 15
    elif ad_percentage > 40:
        score += 10
    else:
        score += 5
    
    # Technical SEO (0-15)
    schema_percentage = (sites_with_schema / total_competitors) * 100
    if schema_percentage > 70:
        score += 15
    elif schema_percentage > 40:
        score += 10
    else:
        score += 5
    
    # Growth indicators (0-15)
    hiring_percentage = (sites_hiring / total_competitors) * 100
    if hiring_percentage > 30:
        score += 15
    elif hiring_percentage > 15:
        score += 10
    else:
        score += 5
    
    if score >= 80:
        difficulty = "Extremely Difficult"
        color = "#EF4444"
    elif score >= 65:
        difficulty = "Very Difficult"
        color = "#F59E0B"
    elif score >= 50:
        difficulty = "Moderately Difficult"
        color = "#EAB308"
    elif score >= 35:
        difficulty = "Manageable"
        color = "#3B82F6"
    else:
        difficulty = "Low Competition"
        color = "#10B981"
    
    if total_competitors >= 20:
        saturation = "Highly Saturated"
    elif total_competitors >= 15:
        saturation = "Saturated"
    elif total_competitors >= 10:
        saturation = "Moderate"
    else:
        saturation = "Low Saturation"
    
    insights = []
    
    if avg_word_count > 1500:
        insights.append("Competitors invest heavily in content marketing")
    
    if avg_social_platforms >= 2.5:
        insights.append("Strong social media presence across industry")
    
    if ad_percentage > 50:
        insights.append(f"{int(ad_percentage)}% of competitors use paid advertising")
    
    if hiring_percentage > 20:
        insights.append("Growth-oriented market with active hiring")
    
    if schema_percentage > 60:
        insights.append("Competitors have advanced technical SEO")
    
    if avg_emails < 1:
        insights.append("⚠️ Low contact accessibility - opportunity for better service")
    
    if sites_with_blog > (total_competitors * 0.7):
        insights.append("Content-driven market - blog/resources critical")
    
    return {
        "competitiveness_score": int(score),
        "difficulty_rating": difficulty,
        "difficulty_color": color,
        "market_saturation": saturation,
        "insights": insights,
        "metrics": {
            "total_competitors": total_competitors,
            "avg_word_count": int(avg_word_count),
            "avg_social_platforms": round(avg_social_platforms, 1),
            "sites_with_ads_pct": int(ad_percentage),
            "sites_hiring_pct": int(hiring_percentage),
            "sites_with_schema_pct": int(schema_percentage),
            "avg_emails_per_site": round(avg_emails, 1),
        }
    }
'''
    
    # Find where to insert new functions (after calculate_confidence_score)
    marker1 = 'def calculate_confidence_score(row: dict) -> float:'
    pos1 = content.find(marker1)
    
    if pos1 == -1:
        print("⚠️  Warning: Couldn't find calculate_confidence_score function")
        return content
    
    # Find the end of that function
    next_function_start = content.find('\n\ndef ', pos1 + 100)
    if next_function_start == -1:
        next_function_start = content.find('\n# ---', pos1 + 100)
    
    if next_function_start != -1:
        content = content[:next_function_start] + new_function_1 + content[next_function_start:]
        print("✅ Added extract_company_name_smart() function")
        print("✅ Added calculate_competitive_intelligence_score() function")
    
    # ==========================================
    # PATCH 2: Modify process_competitor to use smart name extraction
    # ==========================================
    
    old_name_line = '        "name": g.get("g_name", "") or title,'
    new_name_lines = '''    # Extract company name using smart fallback method (NO Google Places needed!)
    company_name = extract_company_name_smart(url, html, soup, title, domain)
    
    # Build base row
    row = {
        "name": company_name,'''
    
    if old_name_line in content:
        # Find the context around it
        pos2 = content.find(old_name_line)
        # Replace from "row = {" to the name line
        start_row = content.rfind('    row = {', pos2 - 100, pos2)
        if start_row != -1:
            end_name = content.find('\n', pos2) + 1
            content = content[:start_row] + new_name_lines + content[end_name:]
            print("✅ Modified process_competitor() to use smart name extraction")
    else:
        print("⚠️  Warning: Couldn't find name assignment in process_competitor")
    
    # ==========================================
    # PATCH 3: Add CI score calculation at end of main()
    # ==========================================
    
    ci_code = '''
    
    # ==========================================
    # CALCULATE COMPETITIVE INTELLIGENCE SCORE
    # ==========================================
    print(f"\\n{'='*70}")
    print("📊 CALCULATING COMPETITIVE INTELLIGENCE SCORE")
    print(f"{'='*70}")
    
    ci_score = calculate_competitive_intelligence_score(rows)
    
    # Save to JSON for dashboard
    ci_output = {
        'query': query,
        'date': _dt.datetime.now().strftime("%Y-%m-%d"),
        'competitors': rows,
        'intelligence': ci_score
    }
    
    with open('competitive_intelligence.json', 'w', encoding='utf-8') as f:
        json.dump(ci_output, f, indent=2, default=str)
    
    print(f"✅ Saved competitive intelligence to competitive_intelligence.json")
    
    # Display CI Score
    print(f"\\n🎯 COMPETITIVE INTELLIGENCE SCORE: {ci_score['competitiveness_score']}/100")
    print(f"   Difficulty: {ci_score['difficulty_rating']}")
    print(f"   Saturation: {ci_score['market_saturation']}")
    print(f"\\n💡 Market Insights:")
    for insight in ci_score['insights']:
        print(f"     • {insight}")
    print(f"\\n{'='*70}")
    
'''
    
    # Find where to insert (before the Tips section)
    marker3 = '    print("\\n💡 Tips:")'
    pos3 = content.find(marker3)
    
    if pos3 != -1:
        content = content[:pos3] + ci_code + content[pos3:]
        print("✅ Added CI score calculation to main()")
    else:
        print("⚠️  Warning: Couldn't find Tips section")
    
    return content

def save_enhanced_file(content, output_filename):
    """Save the enhanced file"""
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Saved enhanced file to: {output_filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 AUTO-PATCHER FOR COMPETITIVE INTELLIGENCE")
    print("=" * 70)
    print()
    
    input_file = "final_competitor_profiler_complete.py"
    output_file = "final_competitor_profiler_ENHANCED.py"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Make sure you're in the correct folder.")
        return
    
    print(f"📂 Found: {input_file}")
    print()
    
    # Create backup
    backup_original(input_file)
    print()
    
    # Read current file
    print("📖 Reading current file...")
    content = read_file(input_file)
    if not content:
        return
    
    print(f"✅ Read {len(content)} characters")
    print()
    
    # Apply all patches
    print("🔧 Applying enhancements...")
    print()
    enhanced_content = apply_patches(content)
    print()
    
    # Save enhanced file
    print("💾 Saving enhanced file...")
    if save_enhanced_file(enhanced_content, output_file):
        print()
        print("=" * 70)
        print("✨ SUCCESS! ✨")
        print("=" * 70)
        print()
        print(f"📄 Original file: {input_file} (backed up)")
        print(f"✅ Enhanced file: {output_file}")
        print()
        print("🎯 NEXT STEPS:")
        print("  1. Test the enhanced file:")
        print(f"     python {output_file}")
        print()
        print("  2. If it works, rename it:")
        print(f"     mv {output_file} {input_file}")
        print()
        print("  3. Open the dashboard:")
        print("     competitive_intelligence_dashboard.html")
        print()
        print("=" * 70)
    else:
        print()
        print("❌ Failed to save enhanced file")

if __name__ == "__main__":
    main()
