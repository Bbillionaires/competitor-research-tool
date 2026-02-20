"""
LEAD GENERATION INTELLIGENCE SYSTEM
Tier-based mentions + Potential client scraping

Part 1: Competitor Mentions (Tiered)
- Free: 5 mentions per company
- Pro: 20 mentions per company  
- Business: 50 mentions per company
- Enterprise: Unlimited

Part 2: Potential Client Finder
Scrapes platforms for people actively looking for services:
- Reddit (legal advice, local subreddits)
- Quora (questions about lawyers/services)
- Facebook Groups (if accessible)
- Local forums
- Review sites (people complaining)

Returns: Name, Platform, Post URL, Date, Intent Score
"""

import csv
import requests
import time
import re
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

# Tier limits
TIER_MENTION_LIMITS = {
    'free': 5,
    'pro': 20,
    'business': 50,
    'enterprise': 999
}

def detect_intent_score(text):
    """
    Score how likely this person is to become a customer
    Scale: 0-10 (10 = highest intent)
    """
    text_lower = text.lower()
    score = 0
    
    # High intent keywords (ready to buy)
    high_intent = ['need', 'looking for', 'recommend', 'hire', 'consultation', 
                   'asap', 'urgent', 'help me', 'anyone know']
    score += sum(3 for keyword in high_intent if keyword in text_lower)
    
    # Location mentioned (local intent)
    if any(city in text_lower for city in ['miami', 'jacksonville', 'tampa', 'orlando']):
        score += 2
    
    # Question format (seeking information)
    if text_lower.startswith(('how', 'what', 'where', 'who', 'when', 'can', 'should')):
        score += 1
    
    # Negative signals (lower intent)
    if any(word in text_lower for word in ['just curious', 'theoretical', 'hypothetical']):
        score -= 2
    
    return min(10, max(0, score))


def scrape_reddit_potential_clients(niche, location, max_results=20):
    """
    Find potential clients on Reddit
    
    Searches:
    - r/legaladvice
    - r/[city] (local subreddit)
    - Related subreddits
    """
    
    if not GOOGLE_CSE_API_KEY:
        return []
    
    potential_clients = []
    
    # Search queries for potential clients
    search_queries = [
        f'site:reddit.com "looking for {niche}" {location}',
        f'site:reddit.com "need {niche}" {location}',
        f'site:reddit.com "recommend {niche}" {location}',
        f'site:reddit.com/r/legaladvice {niche}',
    ]
    
    for query in search_queries[:3]:  # Top 3 to save API calls
        try:
            params = {
                'key': GOOGLE_CSE_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': query,
                'num': 5,
                'dateRestrict': 'm3'  # Last 3 months
            }
            
            response = requests.get('https://www.googleapis.com/customsearch/v1',
                                  params=params, timeout=10)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                url = item.get('link', '')
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                
                # Calculate intent score
                intent = detect_intent_score(title + ' ' + snippet)
                
                # Only include medium-high intent (5+)
                if intent >= 5:
                    potential_clients.append({
                        'platform': 'Reddit',
                        'url': url,
                        'title': title,
                        'snippet': snippet,
                        'intent_score': intent,
                        'date': 'recent',
                        'type': 'potential_client'
                    })
            
            time.sleep(0.5)
            
        except Exception as e:
            continue
    
    return potential_clients[:max_results]


def scrape_quora_potential_clients(niche, location, max_results=20):
    """Find people asking questions on Quora"""
    
    if not GOOGLE_CSE_API_KEY:
        return []
    
    potential_clients = []
    
    queries = [
        f'site:quora.com "how to find {niche}" {location}',
        f'site:quora.com "best {niche}" {location}',
        f'site:quora.com "should I hire" {niche}',
    ]
    
    for query in queries[:2]:
        try:
            params = {
                'key': GOOGLE_CSE_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': query,
                'num': 5
            }
            
            response = requests.get('https://www.googleapis.com/customsearch/v1',
                                  params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    intent = detect_intent_score(title + ' ' + snippet)
                    
                    if intent >= 4:  # Medium intent
                        potential_clients.append({
                            'platform': 'Quora',
                            'url': item.get('link', ''),
                            'title': title,
                            'snippet': snippet,
                            'intent_score': intent,
                            'date': 'recent',
                            'type': 'potential_client'
                        })
            
            time.sleep(0.5)
            
        except:
            continue
    
    return potential_clients[:max_results]


def scrape_review_sites_unhappy_customers(niche, location, max_results=10):
    """
    Find unhappy customers of competitors
    These are HOT LEADS ready to switch!
    """
    
    if not GOOGLE_CSE_API_KEY:
        return []
    
    hot_leads = []
    
    queries = [
        f'site:yelp.com {niche} {location} "1 star"',
        f'site:yelp.com {niche} {location} "terrible"',
        f'site:bbb.org {niche} {location} "complaint"',
    ]
    
    for query in queries[:2]:
        try:
            params = {
                'key': GOOGLE_CSE_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': query,
                'num': 5
            }
            
            response = requests.get('https://www.googleapis.com/customsearch/v1',
                                  params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    hot_leads.append({
                        'platform': 'Review Site',
                        'url': item.get('link', ''),
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'intent_score': 9,  # Very high - they're unhappy!
                        'date': 'recent',
                        'type': 'unhappy_customer'
                    })
            
            time.sleep(0.5)
            
        except:
            continue
    
    return hot_leads[:max_results]


def find_competitor_mentions_tiered(company_name, niche, tier='free'):
    """
    Find mentions of competitors
    Number of results based on tier
    """
    
    limit = TIER_MENTION_LIMITS.get(tier, 5)
    
    if not GOOGLE_CSE_API_KEY:
        return []
    
    mentions = []
    
    # Search for mentions
    query = f'"{company_name}" OR {company_name} {niche}'
    
    try:
        params = {
            'key': GOOGLE_CSE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': query,
            'num': min(10, limit)
        }
        
        response = requests.get('https://www.googleapis.com/customsearch/v1',
                              params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                url = item.get('link', '')
                
                # Skip their own site
                if company_name.lower().replace(' ', '') in url.lower():
                    continue
                
                mentions.append({
                    'platform': detect_platform(url),
                    'url': url,
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'type': 'mention'
                })
    
    except:
        pass
    
    return mentions[:limit]


def detect_platform(url):
    """Detect what platform a URL is from"""
    url_lower = url.lower()
    
    if 'reddit.com' in url_lower:
        return 'Reddit'
    elif 'quora.com' in url_lower:
        return 'Quora'
    elif 'yelp.com' in url_lower:
        return 'Yelp'
    elif 'facebook.com' in url_lower:
        return 'Facebook'
    elif 'linkedin.com' in url_lower:
        return 'LinkedIn'
    elif 'bbb.org' in url_lower:
        return 'BBB'
    else:
        return 'Website'


def generate_lead_intelligence(tier='pro'):
    """
    Main function: Generate lead intelligence
    """
    
    print("=" * 70)
    print("🎯 LEAD GENERATION INTELLIGENCE SYSTEM")
    print("=" * 70)
    print()
    print(f"Tier: {tier.upper()}")
    print(f"Mentions per company: {TIER_MENTION_LIMITS.get(tier, 5)}")
    print()
    print("Finding:")
    print("  1️⃣  Competitor mentions (conversations about them)")
    print("  2️⃣  Potential clients (people actively looking)")
    print("  3️⃣  Unhappy customers (ready to switch)")
    print()
    
    if not GOOGLE_CSE_API_KEY:
        print("❌ Google CSE API key required!")
        return
    
    # Read CSV
    csv_file = 'competitors_final_profile.csv'
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} competitors...")
    print()
    
    # Also find potential clients for the niche
    niche = 'law firms'
    location = 'jacksonville fl'
    
    print("=" * 70)
    print("🔍 FINDING POTENTIAL CLIENTS (NICHE-WIDE)")
    print("=" * 70)
    print()
    
    # Scrape potential clients
    print("Scraping Reddit for potential clients...")
    reddit_clients = scrape_reddit_potential_clients(niche, location, max_results=20)
    print(f"  ✅ Found {len(reddit_clients)} Reddit leads")
    
    print("Scraping Quora for potential clients...")
    quora_clients = scrape_quora_potential_clients(niche, location, max_results=20)
    print(f"  ✅ Found {len(quora_clients)} Quora leads")
    
    print("Finding unhappy customers...")
    unhappy = scrape_review_sites_unhappy_customers(niche, location, max_results=10)
    print(f"  ✅ Found {len(unhappy)} unhappy customers")
    
    all_potential_clients = reddit_clients + quora_clients + unhappy
    
    # Sort by intent score
    all_potential_clients.sort(key=lambda x: x['intent_score'], reverse=True)
    
    print()
    print("=" * 70)
    print("🎯 TOP 10 HOTTEST LEADS:")
    print("=" * 70)
    print()
    
    for i, lead in enumerate(all_potential_clients[:10], 1):
        print(f"{i}. [{lead['platform']}] Intent: {lead['intent_score']}/10")
        print(f"   {lead['title'][:60]}...")
        print(f"   {lead['url']}")
        print()
    
    # Save potential clients to separate CSV
    if all_potential_clients:
        with open('potential_clients.csv', 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['platform', 'url', 'title', 'snippet', 'intent_score', 'date', 'type']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_potential_clients)
        
        print(f"✅ Saved {len(all_potential_clients)} potential clients to: potential_clients.csv")
    
    print()
    print("=" * 70)
    print("📊 PROCESSING COMPETITOR MENTIONS...")
    print("=" * 70)
    print()
    
    # Process each competitor
    for i, row in enumerate(rows, 1):
        name = row.get('name', 'Unknown')[:35]
        
        print(f"[{i}/{len(rows)}] {name}")
        
        # Find mentions
        mentions = find_competitor_mentions_tiered(name, niche, tier=tier)
        
        if mentions:
            mention_list = []
            for m in mentions:
                mention_str = f"[{m['platform']}] {m['title'][:50]}... → {m['url']}"
                mention_list.append(mention_str)
            
            row['tiered_mentions'] = ' || '.join(mention_list)
            row['tiered_mentions_count'] = len(mention_list)
            print(f"  ✅ Found {len(mention_list)} mentions")
        else:
            row['tiered_mentions'] = 'none found'
            row['tiered_mentions_count'] = 0
            print(f"  ℹ️  No mentions found")
        
        time.sleep(1)
    
    # Save competitors CSV
    fieldnames = list(rows[0].keys())
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print()
    print("=" * 70)
    print("✅ LEAD GENERATION COMPLETE!")
    print("=" * 70)
    print()
    print("📊 FILES CREATED:")
    print()
    print("1️⃣  competitors_final_profile.csv (updated)")
    print("    New columns:")
    print("      • tiered_mentions (based on your tier)")
    print("      • tiered_mentions_count")
    print()
    print("2️⃣  potential_clients.csv (NEW!)")
    print(f"    {len(all_potential_clients)} leads ready to contact")
    print("    Columns: platform, url, title, snippet, intent_score, date, type")
    print()
    print("=" * 70)
    print("💰 LEAD VALUE BREAKDOWN:")
    print("=" * 70)
    print()
    
    # Calculate lead value
    high_intent = sum(1 for l in all_potential_clients if l['intent_score'] >= 8)
    medium_intent = sum(1 for l in all_potential_clients if 5 <= l['intent_score'] < 8)
    
    print(f"🔥 High Intent (8-10): {high_intent} leads")
    print(f"   These are HOT - ready to buy NOW")
    print(f"   Estimated value: ${high_intent * 500} - ${high_intent * 2000}")
    print()
    print(f"🟡 Medium Intent (5-7): {medium_intent} leads")
    print(f"   These need nurturing")
    print(f"   Estimated value: ${medium_intent * 200} - ${medium_intent * 800}")
    print()
    print(f"💰 Total potential value: ${(high_intent * 500) + (medium_intent * 200)} - ${(high_intent * 2000) + (medium_intent * 800)}")
    print()
    print("=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Open potential_clients.csv")
    print("2. Sort by intent_score (highest first)")
    print("3. Click URLs and engage:")
    print("   • Answer their questions")
    print("   • Provide value first")
    print("   • Build trust")
    print("   • Subtle mention of your service")
    print()
    print("4. Track conversions:")
    print("   • Leads contacted: ___")
    print("   • Responses: ___")
    print("   • Consultations booked: ___")
    print("   • Clients won: ___")
    print()
    print("📊 Run master_profiler_v2.py to see mentions in Excel")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    # Get tier from command line or default to pro
    tier = sys.argv[1] if len(sys.argv) > 1 else 'pro'
    
    if tier not in TIER_MENTION_LIMITS:
        print(f"Invalid tier. Choose from: {list(TIER_MENTION_LIMITS.keys())}")
        sys.exit(1)
    
    try:
        generate_lead_intelligence(tier=tier)
    except FileNotFoundError:
        print("❌ competitors_final_profile.csv not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
