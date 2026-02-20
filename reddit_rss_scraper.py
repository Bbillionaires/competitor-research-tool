"""
reddit_rss_scraper.py

100% FREE Reddit lead scraping using RSS feeds + search
NO API KEYS NEEDED - Uses public Reddit RSS/JSON endpoints

Features:
- RSS feed scraping (unlimited)
- Reddit JSON API (no auth needed)
- Email extraction from posts
- Keyword filtering
- Priority scoring
"""

import re
import time
import json
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

# ===========================
# Reddit RSS Feed Scraper (100% Free)
# ===========================

class RedditRSSLeadScraper:
    """
    Scrape Reddit using public RSS feeds - NO API KEY NEEDED!
    
    Reddit RSS endpoints:
    - Subreddit: https://www.reddit.com/r/{subreddit}/.rss
    - Search: https://www.reddit.com/r/{subreddit}/search.rss?q={query}
    - User: https://www.reddit.com/user/{username}/.rss
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    
    def scrape_subreddit_rss(self, subreddit: str, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        Scrape subreddit RSS feed for posts matching keywords
        """
        leads = []
        
        try:
            # Get RSS feed
            url = f"https://www.reddit.com/r/{subreddit}/.rss?limit=100"
            
            print(f"📡 Fetching r/{subreddit} RSS feed...")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:limit]:
                title = entry.get('title', '')
                content = entry.get('summary', '')
                full_text = f"{title} {content}".lower()
                
                # Check if any keyword matches
                matched_keywords = [kw for kw in keywords if kw.lower() in full_text]
                
                if matched_keywords:
                    # Extract emails and phones
                    emails = self.email_pattern.findall(content)
                    phones = self.phone_pattern.findall(content)
                    
                    lead = {
                        'platform': 'reddit',
                        'subreddit': subreddit,
                        'author': entry.get('author', 'deleted'),
                        'title': title,
                        'content': content[:500],
                        'url': entry.get('link', ''),
                        'keywords_matched': ', '.join(matched_keywords),
                        'emails_found': list(set(emails)) if emails else [],
                        'phones_found': list(set(phones)) if phones else [],
                        'created_at': entry.get('published', ''),
                        'upvotes': 0,  # RSS doesn't include this
                        'num_comments': 0
                    }
                    
                    # Calculate priority
                    lead['priority'] = self._calculate_priority(lead)
                    
                    leads.append(lead)
            
            print(f"  ✅ Found {len(leads)} matching posts in r/{subreddit}")
            
        except Exception as e:
            print(f"  ⚠️  Error scraping r/{subreddit}: {str(e)}")
        
        return leads
    
    def search_reddit_rss(self, subreddit: str, query: str, limit: int = 100) -> List[Dict]:
        """
        Search specific subreddit using RSS
        More targeted than just scanning feed
        """
        leads = []
        
        try:
            # Reddit search RSS endpoint
            url = f"https://www.reddit.com/r/{subreddit}/search.rss?q={quote_plus(query)}&restrict_sr=1&limit=100&sort=new"
            
            print(f"🔍 Searching r/{subreddit} for '{query}'...")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:limit]:
                title = entry.get('title', '')
                content = entry.get('summary', '')
                
                # Extract contact info
                emails = self.email_pattern.findall(content)
                phones = self.phone_pattern.findall(content)
                
                lead = {
                    'platform': 'reddit',
                    'subreddit': subreddit,
                    'author': entry.get('author', 'deleted'),
                    'title': title,
                    'content': content[:500],
                    'url': entry.get('link', ''),
                    'keywords_matched': query,
                    'emails_found': list(set(emails)) if emails else [],
                    'phones_found': list(set(phones)) if phones else [],
                    'created_at': entry.get('published', ''),
                    'upvotes': 0,
                    'num_comments': 0
                }
                
                lead['priority'] = self._calculate_priority(lead)
                leads.append(lead)
            
            print(f"  ✅ Found {len(leads)} results")
            
        except Exception as e:
            print(f"  ⚠️  Error searching r/{subreddit}: {str(e)}")
        
        return leads
    
    def _calculate_priority(self, lead: Dict) -> str:
        """Calculate lead priority based on signals"""
        content_lower = lead['content'].lower()
        
        # High priority signals
        high_priority = [
            'need lawyer', 'need attorney', 'looking for lawyer',
            'asap', 'urgent', 'help please', 'what should i do',
            'just happened', 'accident', 'injured', 'injury'
        ]
        
        # Boost if contact info found
        if lead['emails_found'] or lead['phones_found']:
            return 'high'
        
        if any(phrase in content_lower for phrase in high_priority):
            return 'high'
        
        # Medium priority
        medium_priority = ['advice', 'recommend', 'suggestions', 'anyone know']
        if any(phrase in content_lower for phrase in medium_priority):
            return 'medium'
        
        return 'low'


# ===========================
# Reddit JSON API Scraper (No Auth Needed!)
# ===========================

class RedditJSONScraper:
    """
    Reddit's JSON API is public - no authentication needed!
    Just add .json to any Reddit URL
    
    Examples:
    - https://www.reddit.com/r/legaladvice/.json
    - https://www.reddit.com/r/legaladvice/search.json?q=injury
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    
    def scrape_subreddit_json(self, subreddit: str, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        Scrape using Reddit's public JSON API
        More data than RSS (includes upvotes, comments, etc.)
        """
        leads = []
        
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for post in data['data']['children'][:limit]:
                    post_data = post['data']
                    
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    full_text = f"{title} {selftext}".lower()
                    
                    # Check keyword match
                    matched_keywords = [kw for kw in keywords if kw.lower() in full_text]
                    
                    if matched_keywords:
                        # Extract contact info
                        combined_text = f"{title} {selftext}"
                        emails = self.email_pattern.findall(combined_text)
                        phones = self.phone_pattern.findall(combined_text)
                        
                        lead = {
                            'platform': 'reddit',
                            'subreddit': subreddit,
                            'author': post_data.get('author', 'deleted'),
                            'title': title,
                            'content': selftext[:500],
                            'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                            'keywords_matched': ', '.join(matched_keywords),
                            'emails_found': list(set(emails)) if emails else [],
                            'phones_found': list(set(phones)) if phones else [],
                            'created_at': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                            'upvotes': post_data.get('ups', 0),
                            'num_comments': post_data.get('num_comments', 0)
                        }
                        
                        lead['priority'] = self._calculate_priority(lead)
                        leads.append(lead)
            
            time.sleep(2)  # Be nice to Reddit
            
        except Exception as e:
            print(f"⚠️  JSON scraping error: {str(e)}")
        
        return leads
    
    def search_json(self, subreddit: str, query: str, limit: int = 100) -> List[Dict]:
        """Search using JSON API"""
        leads = []
        
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json?q={quote_plus(query)}&restrict_sr=1&sort=new&limit=100"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for post in data['data']['children'][:limit]:
                    post_data = post['data']
                    
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    combined_text = f"{title} {selftext}"
                    
                    # Extract contact info
                    emails = self.email_pattern.findall(combined_text)
                    phones = self.phone_pattern.findall(combined_text)
                    
                    lead = {
                        'platform': 'reddit',
                        'subreddit': subreddit,
                        'author': post_data.get('author', 'deleted'),
                        'title': title,
                        'content': selftext[:500],
                        'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                        'keywords_matched': query,
                        'emails_found': list(set(emails)) if emails else [],
                        'phones_found': list(set(phones)) if phones else [],
                        'created_at': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                        'upvotes': post_data.get('ups', 0),
                        'num_comments': post_data.get('num_comments', 0)
                    }
                    
                    lead['priority'] = self._calculate_priority(lead)
                    leads.append(lead)
        
        except Exception as e:
            print(f"⚠️  Search error: {str(e)}")
        
        return leads
    
    def _calculate_priority(self, lead: Dict) -> str:
        """Enhanced priority with engagement metrics"""
        content_lower = lead['content'].lower()
        
        # Contact info found = highest priority
        if lead['emails_found'] or lead['phones_found']:
            return 'high'
        
        # High engagement + keywords
        if lead['upvotes'] > 10 or lead['num_comments'] > 5:
            high_priority = ['need', 'looking for', 'asap', 'urgent', 'help']
            if any(phrase in content_lower for phrase in high_priority):
                return 'high'
        
        # Urgent language
        urgent_phrases = ['just happened', 'today', 'yesterday', 'this morning', 'accident']
        if any(phrase in content_lower for phrase in urgent_phrases):
            return 'high'
        
        # Medium engagement
        if lead['upvotes'] > 3 or lead['num_comments'] > 2:
            return 'medium'
        
        return 'low'


# ===========================
# Master Lead Generator (100% Free)
# ===========================

def generate_reddit_leads_free(
    keywords: List[str],
    subreddits: List[str] = None,
    limit_per_subreddit: int = 50,
    use_rss: bool = True,
    use_json: bool = True
) -> List[Dict]:
    """
    Generate leads from Reddit using 100% free methods
    NO API KEYS NEEDED!
    
    Args:
        keywords: List of search terms
        subreddits: Subreddits to search (defaults to legal-related)
        limit_per_subreddit: Max results per subreddit
        use_rss: Use RSS feed scraping
        use_json: Use JSON API scraping
    """
    
    if not subreddits:
        # Default subreddits for legal services
        subreddits = [
            'legaladvice',
            'personalinjury', 
            'AskLawyers',
            'insurance',
            'caraccidents',
            'needadvice'
        ]
    
    print("=" * 70)
    print("🚀 REDDIT LEAD GENERATION (100% FREE - NO API KEYS)")
    print("=" * 70)
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Subreddits: {', '.join(subreddits)}")
    print(f"Methods: RSS={use_rss}, JSON={use_json}")
    print("=" * 70)
    
    all_leads = []
    
    # Method 1: RSS Feed Scraping
    if use_rss:
        print("\n📡 RSS FEED SCRAPING")
        print("-" * 70)
        
        rss_scraper = RedditRSSLeadScraper()
        
        for subreddit in subreddits:
            for keyword in keywords:
                # Try search RSS first (more targeted)
                search_leads = rss_scraper.search_reddit_rss(subreddit, keyword, limit_per_subreddit)
                all_leads.extend(search_leads)
                
                time.sleep(1)  # Be polite
        
        print(f"\n✅ RSS Total: {len([l for l in all_leads if 'rss' in str(l)])} leads")
    
    # Method 2: JSON API Scraping
    if use_json:
        print("\n🔧 JSON API SCRAPING")
        print("-" * 70)
        
        json_scraper = RedditJSONScraper()
        
        for subreddit in subreddits:
            for keyword in keywords:
                json_leads = json_scraper.search_json(subreddit, keyword, limit_per_subreddit)
                all_leads.extend(json_leads)
                
                time.sleep(2)  # Be extra polite with JSON
        
        print(f"\n✅ JSON Total: {len(all_leads)} total leads")
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_leads = []
    
    for lead in all_leads:
        if lead['url'] not in seen_urls:
            seen_urls.add(lead['url'])
            unique_leads.append(lead)
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    unique_leads.sort(key=lambda x: (
        priority_order.get(x['priority'], 3),
        -x.get('upvotes', 0)
    ))
    
    # Statistics
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total unique leads: {len(unique_leads)}")
    print(f"High priority: {sum(1 for l in unique_leads if l['priority'] == 'high')}")
    print(f"Medium priority: {sum(1 for l in unique_leads if l['priority'] == 'medium')}")
    print(f"Low priority: {sum(1 for l in unique_leads if l['priority'] == 'low')}")
    print(f"With emails: {sum(1 for l in unique_leads if l['emails_found'])}")
    print(f"With phones: {sum(1 for l in unique_leads if l['phones_found'])}")
    print("=" * 70)
    
    return unique_leads


# ===========================
# Example Usage
# ===========================

if __name__ == '__main__':
    # Legal services example
    keywords = [
        'injury attorney',
        'car accident lawyer',
        'personal injury',
        'need lawyer',
        'looking for attorney'
    ]
    
    leads = generate_reddit_leads_free(
        keywords=keywords,
        limit_per_subreddit=25,
        use_rss=True,
        use_json=True
    )
    
    # Show top 5 high-priority leads
    print("\n🔥 TOP HIGH-PRIORITY LEADS:")
    print("-" * 70)
    
    high_priority = [l for l in leads if l['priority'] == 'high'][:5]
    
    for i, lead in enumerate(high_priority, 1):
        print(f"\n{i}. r/{lead['subreddit']} - {lead['title'][:60]}...")
        print(f"   Author: {lead['author']}")
        print(f"   URL: {lead['url']}")
        print(f"   Keywords: {lead['keywords_matched']}")
        if lead['emails_found']:
            print(f"   📧 Emails: {', '.join(lead['emails_found'])}")
        if lead['phones_found']:
            print(f"   📞 Phones: {', '.join(lead['phones_found'])}")
        print(f"   Engagement: {lead['upvotes']} upvotes, {lead['num_comments']} comments")
    
    # Save to JSON
    output_file = 'reddit_leads_free.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {output_file}")
