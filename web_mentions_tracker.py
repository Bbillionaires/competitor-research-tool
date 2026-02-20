"""
WEB MENTIONS TRACKER
Finds where keywords and questions are being mentioned online:
- Reddit discussions
- Forum posts
- Social media mentions
- Review sites
- News articles
- Blog posts

Shows: What was said + WHERE (URL)

This is GOLD for:
1. Finding lead generation opportunities
2. Understanding customer pain points
3. Identifying content gaps
4. Monitoring brand mentions
"""

import csv
import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

def search_keyword_mentions(keyword, company_name, max_results=10):
    """
    Search for mentions of a keyword online
    Returns: List of mentions with URL, source, snippet
    """
    
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_ID:
        print("  ⚠️  Google CSE API keys not found in .env")
        return []
    
    mentions = []
    
    # Search queries to find mentions
    search_queries = [
        f'"{keyword}" reviews',  # Reviews
        f'"{keyword}" forum discussion',  # Forums
        f'"{keyword}" reddit',  # Reddit
        f'"{keyword}" "best"',  # Recommendations
        f'"{keyword}" question',  # Questions about it
    ]
    
    for query in search_queries[:2]:  # Limit to 2 queries to save API calls
        try:
            # Google Custom Search API
            params = {
                'key': GOOGLE_CSE_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': query,
                'num': 5  # 5 results per query
            }
            
            url = "https://www.googleapis.com/customsearch/v1"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                mention_url = item.get('link', '')
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                
                # Determine source type
                source_type = detect_source_type(mention_url)
                
                # Skip if it's the company's own site
                if company_name.lower().replace(' ', '') in mention_url.lower():
                    continue
                
                mentions.append({
                    'keyword': keyword,
                    'url': mention_url,
                    'source': source_type,
                    'title': title,
                    'snippet': snippet,
                    'date': 'recent'  # Would need separate API for exact dates
                })
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"    ⚠️  Search error: {str(e)[:50]}")
            continue
    
    return mentions[:max_results]


def detect_source_type(url):
    """Detect what type of site the mention is from"""
    url_lower = url.lower()
    
    if 'reddit.com' in url_lower:
        return 'Reddit'
    elif 'facebook.com' in url_lower:
        return 'Facebook'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter/X'
    elif 'linkedin.com' in url_lower:
        return 'LinkedIn'
    elif 'yelp.com' in url_lower:
        return 'Yelp Review'
    elif 'quora.com' in url_lower:
        return 'Quora'
    elif 'stackoverflow.com' in url_lower:
        return 'Stack Overflow'
    elif 'medium.com' in url_lower:
        return 'Medium'
    elif any(term in url_lower for term in ['forum', 'discussion', 'community']):
        return 'Forum'
    elif any(term in url_lower for term in ['blog', 'news', 'article']):
        return 'Blog/News'
    elif any(term in url_lower for term in ['review', 'rating']):
        return 'Review Site'
    else:
        return 'Website'


def search_question_mentions(question, company_name):
    """
    Search for where specific questions are being asked
    Great for finding content opportunities!
    """
    
    if not GOOGLE_CSE_API_KEY:
        return []
    
    # Clean question for search
    question_clean = question.replace('[in Title]', '').replace('[in Meta]', '').strip()
    
    # Search for this exact question
    query = f'"{question_clean}"'
    
    try:
        params = {
            'key': GOOGLE_CSE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': query,
            'num': 5
        }
        
        url = "https://www.googleapis.com/customsearch/v1"
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        items = data.get('items', [])
        
        mentions = []
        for item in items:
            mention_url = item.get('link', '')
            
            # Skip own site
            if company_name.lower().replace(' ', '') in mention_url.lower():
                continue
            
            mentions.append({
                'question': question_clean,
                'url': mention_url,
                'source': detect_source_type(mention_url),
                'title': item.get('title', ''),
                'snippet': item.get('snippet', '')
            })
        
        return mentions[:3]  # Top 3
        
    except Exception as e:
        return []


def track_all_mentions():
    """Main function to track all mentions"""
    
    print("=" * 70)
    print("🌐 WEB MENTIONS TRACKER")
    print("=" * 70)
    print()
    print("Finding mentions across:")
    print("  • Reddit discussions")
    print("  • Review sites (Yelp, Google Reviews)")
    print("  • Forums and Q&A sites")
    print("  • Social media")
    print("  • Blog posts and news")
    print()
    
    # Check API keys
    if not GOOGLE_CSE_API_KEY:
        print("❌ Google CSE API key not found!")
        print()
        print("To enable mentions tracking:")
        print("1. Add to .env file:")
        print("   GOOGLE_CSE_API_KEY=your_key")
        print("   GOOGLE_CSE_ID=your_cx_id")
        print()
        print("2. Get keys from: https://console.cloud.google.com")
        print()
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
        print(f"[{i}/{len(rows)}] {name}")
        
        # Get top 3 keywords
        keywords = row.get('keywords', '').split(',')[:3]
        keywords = [k.strip() for k in keywords if k.strip()]
        
        # Get questions
        questions = row.get('question_keywords_locations', '').split('||')[:2]
        questions = [q.strip() for q in questions if q.strip() and q != 'none found']
        
        all_mentions = []
        
        # Search for keyword mentions
        for keyword in keywords[:2]:  # Top 2 keywords to save API calls
            print(f"    Searching mentions of '{keyword}'...")
            mentions = search_keyword_mentions(keyword, name, max_results=3)
            all_mentions.extend(mentions)
            time.sleep(1)  # Rate limiting
        
        # Search for question mentions
        for question in questions[:1]:  # Top 1 question
            print(f"    Searching question mentions...")
            q_mentions = search_question_mentions(question, name)
            all_mentions.extend(q_mentions)
        
        # Format mentions for CSV
        if all_mentions:
            # Keyword mentions
            keyword_mention_list = []
            for m in all_mentions[:5]:  # Top 5
                if 'keyword' in m:
                    mention_str = f"{m['source']}: {m['snippet'][:50]}... | {m['url']}"
                    keyword_mention_list.append(mention_str)
            
            row['keyword_mentions_found'] = ' || '.join(keyword_mention_list) if keyword_mention_list else 'none found'
            row['keyword_mentions_count'] = len(keyword_mention_list)
            
            # Question mentions
            question_mention_list = []
            for m in all_mentions:
                if 'question' in m:
                    mention_str = f"{m['source']}: {m['title'][:50]} | {m['url']}"
                    question_mention_list.append(mention_str)
            
            row['question_mentions_found'] = ' || '.join(question_mention_list) if question_mention_list else 'none found'
            row['question_mentions_count'] = len(question_mention_list)
            
            print(f"    ✅ Found {len(all_mentions)} mentions")
        else:
            row['keyword_mentions_found'] = 'none found'
            row['keyword_mentions_count'] = 0
            row['question_mentions_found'] = 'none found'
            row['question_mentions_count'] = 0
            print(f"    ℹ️  No mentions found")
        
        print()
    
    # Save
    fieldnames = list(rows[0].keys())
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print("=" * 70)
    print("✅ MENTIONS TRACKING COMPLETE!")
    print("=" * 70)
    print()
    print("📊 NEW COLUMNS ADDED:")
    print()
    print("1️⃣  keyword_mentions_found")
    print("    Shows WHERE keywords are being discussed")
    print("    Example: 'Reddit: Discussion about litigation... | url'")
    print()
    print("2️⃣  keyword_mentions_count")
    print("    Total number of mentions found")
    print()
    print("3️⃣  question_mentions_found")
    print("    Where questions are being asked")
    print("    Example: 'Quora: How to choose attorney | url'")
    print()
    print("4️⃣  question_mentions_count")
    print("    Total question mentions")
    print()
    print("=" * 70)
    print("💡 HOW TO USE THIS DATA:")
    print("=" * 70)
    print()
    print("🎯 Lead Generation:")
    print("  • Visit Reddit/forum threads where keywords mentioned")
    print("  • Answer questions and provide value")
    print("  • Include your link naturally")
    print()
    print("📝 Content Strategy:")
    print("  • See what questions people actually ask")
    print("  • Create content answering those questions")
    print("  • Target platforms where discussions happen")
    print()
    print("👀 Competitive Monitoring:")
    print("  • Track where competitors are mentioned")
    print("  • Find review sites to get listed on")
    print("  • Identify PR opportunities")
    print()
    print("📊 Next: Run master_profiler_v2.py to see in Excel")
    print("=" * 70)


if __name__ == "__main__":
    try:
        track_all_mentions()
    except FileNotFoundError:
        print("❌ competitors_final_profile.csv not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
