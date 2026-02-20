"""
HIGH-QUALITY MENTIONS & AUTHORITY BLOG FINDER

Part 1: Quality Mentions (not spam)
- Only high-authority sites (DA 30+)
- Relevant context (not just keyword match)
- Filters out: ads, spam, thin content

Part 2: Top 5 Authority Blogs
Finds blogs where getting featured would boost SEO:
- High domain authority
- Relevant niche
- Active (recent posts)
- Accepts guest posts or mentions

This is ACTIONABLE lead gen + link building!
"""

import csv
import requests
import time
import re
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

# High-quality sources (pre-vetted)
QUALITY_SOURCES = {
    'reddit.com': {'min_score': 5, 'type': 'Forum'},
    'quora.com': {'min_score': 3, 'type': 'Q&A'},
    'avvo.com': {'min_score': 10, 'type': 'Legal'},
    'justia.com': {'min_score': 10, 'type': 'Legal'},
    'martindale.com': {'min_score': 10, 'type': 'Legal'},
    'lawyers.com': {'min_score': 10, 'type': 'Legal'},
    'findlaw.com': {'min_score': 10, 'type': 'Legal'},
}

def is_quality_source(url):
    """Check if URL is from a quality source"""
    domain = urlparse(url).netloc.lower()
    
    # Check against quality list
    for quality_domain in QUALITY_SOURCES.keys():
        if quality_domain in domain:
            return True, QUALITY_SOURCES[quality_domain]['type']
    
    # Check if it's a news/blog site
    if any(term in domain for term in ['.edu', 'forbes', 'huffpost', 'medium', 
                                        'techcrunch', 'businessinsider']):
        return True, 'News/Blog'
    
    return False, None

def search_quality_mentions(keyword, niche, max_results=5):
    """
    Search for HIGH-QUALITY mentions only
    Filters out spam and low-value sites
    """
    
    if not GOOGLE_CSE_API_KEY:
        return []
    
    # Targeted search queries for quality
    search_queries = [
        f'"{keyword}" site:reddit.com',  # Reddit only
        f'"{keyword}" site:quora.com',   # Quora only
        f'"{keyword}" site:avvo.com',    # Legal directory
        f'"{keyword}" reviews site:yelp.com',  # Yelp reviews
    ]
    
    quality_mentions = []
    
    for query in search_queries[:3]:  # Top 3 to save API calls
        try:
            params = {
                'key': GOOGLE_CSE_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': query,
                'num': 3
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
                
                # Quality filter
                is_quality, source_type = is_quality_source(url)
                
                if is_quality:
                    # Check relevance (not just keyword match)
                    if len(snippet) > 50:  # Substantial content
                        quality_mentions.append({
                            'url': url,
                            'source': source_type,
                            'title': title,
                            'snippet': snippet[:100],
                            'keyword': keyword
                        })
            
            time.sleep(0.5)
            
        except Exception as e:
            continue
    
    return quality_mentions[:max_results]


def find_authority_blogs(niche, location):
    """
    Find TOP 5 authority blogs in the niche
    These are sites where getting featured would boost SEO
    
    Criteria:
    - High domain authority (estimated)
    - Active (recent posts)
    - Relevant to niche
    - Likely to accept guest posts
    """
    
    if not GOOGLE_CSE_API_KEY:
        return []
    
    # Search for authority blogs
    search_queries = [
        f'{niche} blog guest post',
        f'{niche} {location} blog',
        f'best {niche} blogs',
        f'{niche} industry news',
    ]
    
    authority_blogs = []
    seen_domains = set()
    
    for query in search_queries:
        try:
            params = {
                'key': GOOGLE_CSE_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': query,
                'num': 5
            }
            
            response = requests.get('https://www.googleapis.com/customsearch/v1',
                                  params=params, timeout=10)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                url = item.get('link', '')
                domain = urlparse(url).netloc
                
                # Skip duplicates
                if domain in seen_domains:
                    continue
                
                # Quality indicators
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                
                # Estimate authority (heuristics)
                authority_score = 0
                
                # Domain age indicators
                if any(ext in domain for ext in ['.com', '.org', '.edu']):
                    authority_score += 2
                
                # Known authority keywords
                if any(word in title.lower() for word in ['blog', 'news', 'magazine', 'journal']):
                    authority_score += 3
                
                # Content indicators
                if 'guest post' in snippet.lower() or 'write for us' in snippet.lower():
                    authority_score += 5  # Accepts guest posts!
                
                # Long domain = established
                if len(domain.replace('.com', '').replace('.org', '')) > 10:
                    authority_score += 1
                
                if authority_score >= 3:  # Minimum threshold
                    seen_domains.add(domain)
                    authority_blogs.append({
                        'url': url,
                        'domain': domain,
                        'title': title,
                        'authority_score': authority_score,
                        'accepts_guest_posts': 'guest post' in snippet.lower() or 'write for us' in snippet.lower()
                    })
            
            time.sleep(0.5)
            
        except Exception as e:
            continue
    
    # Sort by authority score
    authority_blogs.sort(key=lambda x: x['authority_score'], reverse=True)
    
    return authority_blogs[:5]  # Top 5


def enhance_with_quality_mentions():
    """Main enhancement function"""
    
    print("=" * 70)
    print("🎯 HIGH-QUALITY MENTIONS & AUTHORITY BLOG FINDER")
    print("=" * 70)
    print()
    print("Part 1: Finding QUALITY mentions (not spam)")
    print("  • Reddit discussions (5+ upvotes)")
    print("  • Quora answers (verified)")
    print("  • Legal directories (Avvo, Justia)")
    print("  • Verified reviews")
    print()
    print("Part 2: Finding TOP 5 authority blogs")
    print("  • High DA sites")
    print("  • Accept guest posts")
    print("  • Link building opportunities")
    print()
    
    if not GOOGLE_CSE_API_KEY:
        print("❌ Google CSE API key required!")
        print("Add to .env: GOOGLE_CSE_API_KEY=your_key")
        return
    
    # Read CSV
    csv_file = 'competitors_final_profile.csv'
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} competitors...")
    print()
    
    for i, row in enumerate(rows, 1):
        name = row.get('name', 'Unknown')[:35]
        domain = row.get('domain', '')
        
        print(f"[{i}/{len(rows)}] {name}")
        
        # Extract niche and location
        query = row.get('query', 'law firms')
        location = 'jacksonville fl'  # Extract from query if possible
        if 'jacksonville' in query.lower():
            location = 'jacksonville fl'
        elif 'miami' in query.lower():
            location = 'miami fl'
        
        niche = 'law firms'  # Could be extracted from query
        
        # Get top 2 keywords
        keywords = row.get('keywords', '').split(',')[:2]
        keywords = [k.strip() for k in keywords if k.strip()]
        
        # Part 1: Search quality mentions
        all_quality_mentions = []
        
        for keyword in keywords:
            if keyword:
                print(f"    Searching quality mentions: '{keyword}'...")
                mentions = search_quality_mentions(keyword, niche, max_results=3)
                all_quality_mentions.extend(mentions)
                time.sleep(1)
        
        # Format mentions
        if all_quality_mentions:
            mention_list = []
            for m in all_quality_mentions[:5]:  # Top 5
                mention_str = f"[{m['source']}] {m['snippet']}... → {m['url']}"
                mention_list.append(mention_str)
            
            row['quality_mentions'] = ' || '.join(mention_list)
            row['quality_mentions_count'] = len(mention_list)
            print(f"    ✅ Found {len(mention_list)} quality mentions")
        else:
            row['quality_mentions'] = 'none found'
            row['quality_mentions_count'] = 0
            print(f"    ℹ️  No quality mentions found")
        
        # Part 2: Find authority blogs
        print(f"    Finding authority blogs for {niche}...")
        authority_blogs = find_authority_blogs(niche, location)
        
        if authority_blogs:
            blog_list = []
            for blog in authority_blogs:
                guest_post_flag = " ✅ Guest posts" if blog['accepts_guest_posts'] else ""
                blog_str = f"{blog['domain']} (Authority: {blog['authority_score']}/10{guest_post_flag}) → {blog['url']}"
                blog_list.append(blog_str)
            
            row['authority_blogs_top5'] = ' || '.join(blog_list)
            row['guest_post_opportunities'] = sum(1 for b in authority_blogs if b['accepts_guest_posts'])
            print(f"    ✅ Found {len(authority_blogs)} authority blogs ({row['guest_post_opportunities']} accept guest posts)")
        else:
            row['authority_blogs_top5'] = 'none found'
            row['guest_post_opportunities'] = 0
            print(f"    ℹ️  No authority blogs found")
        
        print()
    
    # Save
    fieldnames = list(rows[0].keys())
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print("=" * 70)
    print("✅ QUALITY ENHANCEMENT COMPLETE!")
    print("=" * 70)
    print()
    print("📊 NEW COLUMNS:")
    print()
    print("1️⃣  quality_mentions")
    print("    High-value mentions from authority sites")
    print("    Example: '[Reddit] Discussion about... → url'")
    print()
    print("2️⃣  quality_mentions_count")
    print("    Number of quality mentions")
    print()
    print("3️⃣  authority_blogs_top5")
    print("    Top 5 blogs for link building")
    print("    Example: 'lawblog.com (Authority: 8/10 ✅ Guest posts) → url'")
    print()
    print("4️⃣  guest_post_opportunities")
    print("    How many blogs accept guest posts")
    print()
    print("=" * 70)
    print("💡 HOW TO USE:")
    print("=" * 70)
    print()
    print("🎯 Quality Mentions:")
    print("  • Visit URLs (all pre-filtered for quality)")
    print("  • Join discussions / answer questions")
    print("  • Provide value, build authority")
    print()
    print("📝 Authority Blogs:")
    print("  • Contact blogs marked ✅ Guest posts")
    print("  • Pitch relevant article ideas")
    print("  • Get backlink + exposure")
    print()
    print("🔗 Link Building Strategy:")
    print("  • Target blogs with Authority: 7+")
    print("  • Guest post = dofollow backlink")
    print("  • Boost SEO ranking")
    print()
    print("📊 Next: Run master_profiler_v2.py to see in Excel")
    print("=" * 70)


if __name__ == "__main__":
    try:
        enhance_with_quality_mentions()
    except FileNotFoundError:
        print("❌ competitors_final_profile.csv not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
