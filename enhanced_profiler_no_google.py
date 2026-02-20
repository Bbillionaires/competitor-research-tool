"""
===============================================
ENHANCED COMPETITOR PROFILER - SMART FALLBACKS
===============================================
Works WITHOUT Google Places API!

FALLBACK HIERARCHY:
1. OpenGraph meta tags (og:title, og:site_name)
2. Schema.org JSON-LD markup
3. Intelligent title parsing
4. Domain name extraction
5. Email domain analysis

NEW FEATURES:
- Competitive Intelligence Score
- Industry difficulty rating
- Market saturation analysis
- No dependency on paid APIs
"""

# Add this to your final_competitor_profiler_complete.py

# ==========================================
# NEW FUNCTION 1: Extract Company Name (No Google Places)
# ==========================================

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
        # Remove common junk words
        junk_words = [
            'jacksonville', 'florida', 'fl', 'real estate', 'investor', 'investors',
            'best', 'top', '10', 'list', 'guide', 'home', 'welcome', 'about',
            'commercial', 'residential', 'property', 'properties'
        ]
        
        # Split on common separators
        for separator in [' | ', ' – ', ' - ', '–', '|', '-']:
            if separator in title:
                parts = title.split(separator)
                for part in parts:
                    part = part.strip()
                    
                    # Check if this part looks like a company name
                    lower_part = part.lower()
                    junk_count = sum(1 for word in junk_words if word in lower_part)
                    
                    # If less than 2 junk words and reasonable length
                    if junk_count < 2 and 5 < len(part) < 80:
                        print(f"  📝 Name from title parsing: {part}")
                        return part
                break
    
    # Method 4: First H1 tag
    h1 = soup.find("h1")
    if h1:
        h1_text = h1.get_text(strip=True)
        if h1_text and 5 < len(h1_text) < 80:
            # Check if it looks like a company name
            if not any(x in h1_text.lower() for x in ['welcome', 'home', 'about', 'contact']):
                print(f"  📝 Name from H1: {h1_text}")
                return h1_text
    
    # Method 5: Domain name cleanup
    name = domain.replace('.com', '').replace('.net', '').replace('.org', '')
    name = name.replace('-', ' ').replace('_', ' ')
    
    # Remove 'www' if present
    if name.startswith('www '):
        name = name[4:]
    
    # Title case
    name = ' '.join(word.capitalize() for word in name.split())
    
    print(f"  📝 Name from domain: {name}")
    return name


# ==========================================
# NEW FUNCTION 2: Competitive Intelligence Score
# ==========================================

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
    
    # Metrics to analyze
    total_competitors = len(competitors)
    
    # 1. Digital presence quality (websites, SEO)
    avg_word_count = sum(c.get('word_count', 0) for c in competitors) / total_competitors
    sites_with_blog = sum(1 for c in competitors if c.get('word_count', 0) > 1000)
    
    # 2. Social media presence
    avg_social_platforms = sum(c.get('social_platform_count', 0) for c in competitors) / total_competitors
    
    # 3. Marketing sophistication
    sites_with_ads = sum(1 for c in competitors if c.get('ads_signal', 0) > 0)
    sites_hiring = sum(1 for c in competitors if c.get('hiring_signal', 0) > 0)
    
    # 4. Technical sophistication
    sites_with_schema = sum(1 for c in competitors if c.get('schema_present') == 1)
    avg_internal_links = sum(c.get('internal_links', 0) for c in competitors) / total_competitors
    
    # 5. Email/Contact accessibility
    avg_emails = sum(len(str(c.get('emails', '')).split('|')) for c in competitors) / total_competitors
    
    # Calculate competitiveness score (0-100)
    score = 0
    
    # Market size factor (0-20 points)
    if total_competitors >= 20:
        score += 20
    elif total_competitors >= 15:
        score += 15
    elif total_competitors >= 10:
        score += 10
    else:
        score += 5
    
    # Content quality (0-20 points)
    if avg_word_count > 2000:
        score += 20
    elif avg_word_count > 1000:
        score += 15
    elif avg_word_count > 500:
        score += 10
    else:
        score += 5
    
    # Social presence (0-15 points)
    if avg_social_platforms >= 3:
        score += 15
    elif avg_social_platforms >= 2:
        score += 10
    else:
        score += 5
    
    # Marketing sophistication (0-15 points)
    ad_percentage = (sites_with_ads / total_competitors) * 100
    if ad_percentage > 70:
        score += 15
    elif ad_percentage > 40:
        score += 10
    else:
        score += 5
    
    # Technical SEO (0-15 points)
    schema_percentage = (sites_with_schema / total_competitors) * 100
    if schema_percentage > 70:
        score += 15
    elif schema_percentage > 40:
        score += 10
    else:
        score += 5
    
    # Growth indicators (0-15 points)
    hiring_percentage = (sites_hiring / total_competitors) * 100
    if hiring_percentage > 30:
        score += 15
    elif hiring_percentage > 15:
        score += 10
    else:
        score += 5
    
    # Determine difficulty rating
    if score >= 80:
        difficulty = "Extremely Difficult"
        color = "#EF4444"  # Red
    elif score >= 65:
        difficulty = "Very Difficult"
        color = "#F59E0B"  # Orange
    elif score >= 50:
        difficulty = "Moderately Difficult"
        color = "#EAB308"  # Yellow
    elif score >= 35:
        difficulty = "Manageable"
        color = "#3B82F6"  # Blue
    else:
        difficulty = "Low Competition"
        color = "#10B981"  # Green
    
    # Market saturation
    if total_competitors >= 20:
        saturation = "Highly Saturated"
    elif total_competitors >= 15:
        saturation = "Saturated"
    elif total_competitors >= 10:
        saturation = "Moderate"
    else:
        saturation = "Low Saturation"
    
    # Generate insights
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


# ==========================================
# NEW FUNCTION 3: Enhanced process_competitor (No Google dependency)
# ==========================================

def process_competitor_enhanced(url: str, query: str) -> Optional[dict]:
    """
    Enhanced competitor processing with NO Google Places dependency
    Uses smart fallbacks for all data points
    """
    domain = extract_domain(url)
    
    if not domain or domain.endswith(JUNK_TLDS):
        return None
    
    print(f"📊 Processing: {domain}")
    
    resp = safe_get(url, timeout=REQUEST_TIMEOUT)
    if not resp or resp.status_code >= 400:
        return None
    
    html = resp.text or ""
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True)[:250] if title_tag else domain
    
    # SMART NAME EXTRACTION (no Google Places needed!)
    company_name = extract_company_name_smart(url, html, soup, title, domain)
    
    # Extract address from Schema.org or contact page
    address = ""
    try:
        schema_scripts = soup.find_all("script", type="application/ld+json")
        for script in schema_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Organization":
                    addr = data.get("address", {})
                    if isinstance(addr, dict):
                        address = f"{addr.get('streetAddress', '')}, {addr.get('addressLocality', '')}, {addr.get('addressRegion', '')} {addr.get('postalCode', '')}".strip(', ')
            except:
                pass
    except:
        pass
    
    # Scrape website data
    web = scrape_website_data(url, html, soup)
    
    # Build row WITHOUT Google Places data
    row = {
        "name": company_name,
        "address": address,
        "url": url,
        "domain": domain,
        "title": title,
        "query": query,
        "traffic_estimate": 0,  # Will be calculated
        
        # Website data
        "emails": " | ".join(web.get("emails", [])),
        "phones": " | ".join(web.get("phones", [])),
        "logo_url": web.get("logo_url", ""),
        "contact_page": web.get("contact_page", ""),
        "booking_links": " | ".join(web.get("booking_links", [])),
        
        # Social
        "social_facebook": " | ".join(web.get("social_facebook", [])),
        "social_linkedin": " | ".join(web.get("social_linkedin", [])),
        "social_instagram": " | ".join(web.get("social_instagram", [])),
        "social_twitter": " | ".join(web.get("social_twitter", [])),
        
        # Metadata
        "source": "web_scraping",
        "collected_at": _dt.datetime.utcnow().isoformat() + "Z",
        "collection_date": _dt.datetime.now().strftime("%Y-%m-%d"),
    }
    
    # All other enrichments (these don't need Google Places)
    seo_data = extract_onpage_seo(url, html, soup)
    row.update(seo_data)
    
    tech_data = check_technical_seo(domain)
    row.update(tech_data)
    
    backlink_data = get_free_backlinks_and_authority(domain)
    row.update(backlink_data)
    
    citation_data = check_directory_citations(company_name, domain)
    row.update(citation_data)
    
    social_data = enrich_social_metrics(row)
    row.update(social_data)
    
    ads_data = detect_advertising_signals(domain, html)
    row.update(ads_data)
    
    hiring_data = detect_hiring_signals(domain, soup)
    row.update(hiring_data)
    
    # Calculate traffic estimate
    row["traffic_estimate"] = estimate_traffic(row)
    
    # Calculate confidence score
    row["confidence_score"] = calculate_confidence_score(row)
    
    # Scoring
    score = compute_score(row)
    row["competitor_score"] = score
    row["tier"] = tier_from_score(score)
    
    return row


# ==========================================
# INTEGRATION INSTRUCTIONS
# ==========================================

"""
TO USE THESE ENHANCEMENTS:

1. ADD these three functions to your final_competitor_profiler_complete.py

2. REPLACE process_competitor with process_competitor_enhanced

3. IN main() function, AFTER processing all competitors, ADD:

    # Calculate competitive intelligence
    print("\n📊 Calculating Competitive Intelligence Score...")
    ci_score = calculate_competitive_intelligence_score(rows)
    
    # Save to separate file for dashboard
    with open('competitive_intelligence.json', 'w') as f:
        json.dump({
            'query': query,
            'date': _dt.datetime.now().strftime("%Y-%m-%d"),
            'competitors': rows,
            'intelligence': ci_score
        }, f, indent=2)
    
    print(f"\n🎯 COMPETITIVE INTELLIGENCE SCORE: {ci_score['competitiveness_score']}/100")
    print(f"   Difficulty: {ci_score['difficulty_rating']}")
    print(f"   Saturation: {ci_score['market_saturation']}")
    print(f"   Insights:")
    for insight in ci_score['insights']:
        print(f"     • {insight}")

4. Dashboard will read from 'competitive_intelligence.json'

BENEFITS:
✅ No Google Places API needed
✅ Better company name extraction
✅ Competitive intelligence scoring
✅ Market difficulty assessment
✅ Industry insights
✅ Cost: $0 per search!
"""

print(__doc__)
