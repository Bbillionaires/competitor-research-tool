"""
lead_scraper.py

100% FREE lead generation from Reddit and LinkedIn
NO PAID APIS - Uses only free methods

Methods:
- Reddit: RSS feeds + JSON API (no auth needed)
- LinkedIn: Google CSE, Brave Search, DuckDuckGo
"""

import os
import re
import json
import time
import argparse
from datetime import datetime
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

# Import free Reddit scraper
from reddit_rss_scraper import generate_reddit_leads_free

# ===========================
# Configuration
# ===========================

# Free APIs (optional - script works without them)
GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY', '')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', '')
BRAVE_SEARCH_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY', '')
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')

# ===========================
# FREE LinkedIn Methods
# ===========================

def search_linkedin_duckduckgo(keyword: str, limit: int = 20) -> List[Dict]:
    """DuckDuckGo - 100% free, unlimited"""
    from bs4 import BeautifulSoup
    
    leads = []
    
    try:
        url = f"https://html.duckduckgo.com/html/?q=site:linkedin.com+{keyword.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for result in soup.find_all('div', class_='result')[:limit]:
            title_elem = result.find('a', class_='result__a')
            snippet_elem = result.find('a', class_='result__snippet')
            
            if title_elem:
                leads.append({
                    'platform': 'linkedin',
                    'author': 'LinkedIn User',
                    'title': title_elem.get_text(strip=True),
                    'content': snippet_elem.get_text(strip=True) if snippet_elem else '',
                    'url': title_elem.get('href', ''),
                    'keywords_matched': keyword,
                    'created_at': datetime.now().isoformat(),
                    'priority': 'medium',
                    'source': 'duckduckgo'
                })
    except Exception as e:
        print(f"⚠️  DuckDuckGo error: {str(e)}")
    
    return leads


def search_linkedin_brave(keyword: str, limit: int = 20) -> List[Dict]:
    """Brave Search - 2000 free/month"""
    if not BRAVE_SEARCH_API_KEY:
        return []
    
    leads = []
    
    try:
        headers = {'X-Subscription-Token': BRAVE_SEARCH_API_KEY}
        params = {
            'q': f'site:linkedin.com "{keyword}"',
            'count': limit
        }
        
        response = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers=headers,
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            for result in data.get('web', {}).get('results', []):
                leads.append({
                    'platform': 'linkedin',
                    'author': 'LinkedIn User',
                    'title': result.get('title', ''),
                    'content': result.get('description', ''),
                    'url': result.get('url', ''),
                    'keywords_matched': keyword,
                    'created_at': datetime.now().isoformat(),
                    'priority': 'medium',
                    'source': 'brave'
                })
    except Exception as e:
        print(f"⚠️  Brave Search error: {str(e)}")
    
    return leads


def search_linkedin_google_cse(keyword: str, limit: int = 10) -> List[Dict]:
    """Google CSE - use existing quota"""
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_ID:
        return []
    
    leads = []
    
    try:
        from urllib.parse import urlencode
        
        params = {
            'key': GOOGLE_CSE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': f'site:linkedin.com "{keyword}"',
            'num': min(10, limit)
        }
        
        url = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data.get('items', []):
                leads.append({
                    'platform': 'linkedin',
                    'author': 'LinkedIn User',
                    'title': item.get('title', ''),
                    'content': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'keywords_matched': keyword,
                    'created_at': datetime.now().isoformat(),
                    'priority': 'medium',
                    'source': 'google_cse'
                })
    except Exception as e:
        print(f"⚠️  Google CSE error: {str(e)}")
    
    return leads


def generate_linkedin_leads_free(keywords: List[str], limit: int = 50) -> List[Dict]:
    """
    Generate LinkedIn leads using only free methods
    """
    print("\n💼 LinkedIn Lead Generation (100% FREE)")
    print("=" * 60)
    
    all_leads = []
    
    for keyword in keywords:
        # Method 1: DuckDuckGo (unlimited free)
        print(f"\n🦆 Searching DuckDuckGo for: {keyword}")
        ddg_leads = search_linkedin_duckduckgo(keyword, limit // len(keywords))
        all_leads.extend(ddg_leads)
        print(f"  ✅ Found {len(ddg_leads)} leads")
        time.sleep(2)
        
        # Method 2: Brave Search (if API key available)
        if BRAVE_SEARCH_API_KEY:
            print(f"🦁 Searching Brave for: {keyword}")
            brave_leads = search_linkedin_brave(keyword, limit // len(keywords))
            all_leads.extend(brave_leads)
            print(f"  ✅ Found {len(brave_leads)} leads")
            time.sleep(2)
        
        # Method 3: Google CSE (if available)
        if GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID:
            print(f"🔍 Searching Google CSE for: {keyword}")
            google_leads = search_linkedin_google_cse(keyword, limit // len(keywords))
            all_leads.extend(google_leads)
            print(f"  ✅ Found {len(google_leads)} leads")
            time.sleep(2)
    
    # Remove duplicates
    seen_urls = set()
    unique_leads = []
    for lead in all_leads:
        if lead['url'] not in seen_urls:
            seen_urls.add(lead['url'])
            unique_leads.append(lead)
    
    print(f"\n💼 Total LinkedIn leads: {len(unique_leads)}")
    
    return unique_leads


# ===========================
# Master Lead Generator
# ===========================

def generate_all_leads(
    keywords: List[str],
    platforms: List[str] = ['reddit', 'linkedin'],
    limit_per_platform: int = 50,
    output_file: str = 'leads_generated.json'
) -> List[Dict]:
    """
    Generate leads from all platforms using 100% free methods
    """
    print("=" * 70)
    print("🚀 FREE LEAD GENERATION - NO PAID APIS")
    print("=" * 70)
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Platforms: {', '.join(platforms)}")
    print("=" * 70)
    
    all_leads = []
    
    # Reddit (100% free, no API needed)
    if 'reddit' in platforms:
        print("\n" + "=" * 70)
        reddit_leads = generate_reddit_leads_free(
            keywords=keywords,
            limit_per_subreddit=limit_per_platform // 6,  # Divide by number of subreddits
            use_rss=True,
            use_json=True
        )
        all_leads.extend(reddit_leads)
    
    # LinkedIn (free methods only)
    if 'linkedin' in platforms:
        print("\n" + "=" * 70)
        linkedin_leads = generate_linkedin_leads_free(keywords, limit_per_platform)
        all_leads.extend(linkedin_leads)
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    all_leads.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_leads, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    print(f"Total leads: {len(all_leads)}")
    print(f"High priority: {sum(1 for l in all_leads if l.get('priority') == 'high')}")
    print(f"Medium priority: {sum(1 for l in all_leads if l.get('priority') == 'medium')}")
    print(f"Low priority: {sum(1 for l in all_leads if l.get('priority') == 'low')}")
    print(f"With emails: {sum(1 for l in all_leads if l.get('emails_found'))}")
    print(f"With phones: {sum(1 for l in all_leads if l.get('phones_found'))}")
    print(f"💾 Saved to: {output_file}")
    print("=" * 70)
    
    return all_leads


# ===========================
# CLI
# ===========================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FREE lead generation')
    parser.add_argument('--keywords', type=str, required=True)
    parser.add_argument('--platforms', type=str, default='["reddit", "linkedin"]')
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--output', type=str, default='leads_generated.json')
    
    args = parser.parse_args()
    
    keywords = json.loads(args.keywords)
    platforms = json.loads(args.platforms)
    
    leads = generate_all_leads(
        keywords=keywords,
        platforms=platforms,
        limit_per_platform=args.limit,
        output_file=args.output
    )
    
    # Show sample
    print("\n🔥 Sample High-Priority Leads:")
    for lead in [l for l in leads if l.get('priority') == 'high'][:3]:
        print(f"\n  Platform: {lead['platform']}")
        print(f"  {lead.get('title', lead.get('content', '')[:60])}...")
        print(f"  URL: {lead['url']}")
        if lead.get('emails_found'):
            print(f"  📧 {', '.join(lead['emails_found'])}")


# ===========================
# Configuration
# ===========================

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'LeadScraper/1.0')

# ProxyCurl for LinkedIn (free tier: 10 credits/month)
PROXYCURL_API_KEY = os.getenv('PROXYCURL_API_KEY', '')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ===========================
# Reddit Lead Scraper
# ===========================

class RedditLeadScraper:
    def __init__(self):
        self.access_token = None
        self.authenticate()
    
    def authenticate(self):
        """Get Reddit OAuth token"""
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            print("⚠️  Reddit credentials not set. Skipping Reddit scraping.")
            return
        
        auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
        data = {'grant_type': 'client_credentials'}
        headers = {'User-Agent': REDDIT_USER_AGENT}
        
        try:
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                print("✅ Reddit authenticated")
            else:
                print(f"⚠️  Reddit auth failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Reddit auth error: {str(e)}")
    
    def search_posts(self, keywords: List[str], subreddits: List[str] = None, limit: int = 100) -> List[Dict]:
        """
        Search Reddit for posts containing keywords
        
        Args:
            keywords: List of keywords to search for
            subreddits: List of subreddits to search (None = all)
            limit: Max number of results
        
        Returns:
            List of lead dictionaries
        """
        if not self.access_token:
            return []
        
        leads = []
        headers = {
            'Authorization': f'bearer {self.access_token}',
            'User-Agent': REDDIT_USER_AGENT
        }
        
        # Default subreddits for legal services
        if not subreddits:
            subreddits = [
                'legaladvice',
                'personalinjury',
                'AskLawyers',
                'needadvice',
                'insurance',
                'caraccidents'
            ]
        
        for keyword in keywords:
            for subreddit in subreddits:
                try:
                    # Search subreddit
                    url = f'https://oauth.reddit.com/r/{subreddit}/search'
                    params = {
                        'q': keyword,
                        'restrict_sr': 1,
                        'sort': 'new',
                        'limit': limit // (len(keywords) * len(subreddits)),
                        't': 'month'  # Last month
                    }
                    
                    response = requests.get(url, headers=headers, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for post in data.get('data', {}).get('children', []):
                            post_data = post.get('data', {})
                            
                            # Extract relevant info
                            lead = {
                                'platform': 'reddit',
                                'author': post_data.get('author', 'deleted'),
                                'content': post_data.get('title', '') + ' ' + post_data.get('selftext', ''),
                                'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                                'subreddit': subreddit,
                                'keywords_matched': keyword,
                                'created_at': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                                'upvotes': post_data.get('ups', 0),
                                'num_comments': post_data.get('num_comments', 0)
                            }
                            
                            # Calculate priority based on engagement
                            priority = self._calculate_priority(lead)
                            lead['priority'] = priority
                            
                            leads.append(lead)
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"⚠️  Error scraping r/{subreddit}: {str(e)}")
                    continue
        
        return leads
    
    def _calculate_priority(self, lead: Dict) -> str:
        """Calculate lead priority based on engagement and keywords"""
        content_lower = lead['content'].lower()
        
        # High priority indicators
        high_priority_phrases = [
            'need lawyer', 'looking for attorney', 'asap', 'urgent',
            'injured', 'accident happened', 'consultation'
        ]
        
        if any(phrase in content_lower for phrase in high_priority_phrases):
            return 'high'
        
        # Medium priority: good engagement
        if lead.get('upvotes', 0) > 5 or lead.get('num_comments', 0) > 3:
            return 'medium'
        
        return 'low'

# ===========================
# LinkedIn Lead Scraper
# ===========================

class LinkedInLeadScraper:
    def __init__(self):
        self.api_key = PROXYCURL_API_KEY
    
    def search_posts(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """
        Search LinkedIn for posts/profiles using ProxyCurl API
        Free tier: 10 credits/month
        
        Alternative free method: Use Google Custom Search with site:linkedin.com
        """
        if not self.api_key:
            print("⚠️  ProxyCurl API key not set. Using Google search fallback...")
            return self._search_via_google(keywords, limit)
        
        leads = []
        
        for keyword in keywords:
            try:
                # ProxyCurl Person Search endpoint
                url = "https://nubela.co/proxycurl/api/linkedin/company/employees/search"
                params = {
                    'keyword': keyword,
                    'enrich_profiles': 'skip'
                }
                headers = {'Authorization': f'Bearer {self.api_key}'}
                
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for profile in data.get('employees', [])[:limit // len(keywords)]:
                        lead = {
                            'platform': 'linkedin',
                            'author': profile.get('name', 'Unknown'),
                            'content': f"Profile: {profile.get('headline', '')}",
                            'url': profile.get('profile_url', ''),
                            'keywords_matched': keyword,
                            'created_at': datetime.now().isoformat(),
                            'priority': 'medium'
                        }
                        leads.append(lead)
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️  ProxyCurl error: {str(e)}")
                continue
        
        return leads
    
    def _search_via_google(self, keywords: List[str], limit: int) -> List[Dict]:
        """
        Free fallback: Use Google Custom Search to find LinkedIn posts
        Requires GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID
        """
        from final_competitor_profiler_complete import google_cse_search
        
        leads = []
        
        for keyword in keywords:
            query = f'site:linkedin.com/posts OR site:linkedin.com/pulse "{keyword}"'
            
            try:
                urls = google_cse_search(query, max_results=limit // len(keywords))
                
                for url in urls:
                    lead = {
                        'platform': 'linkedin',
                        'author': 'LinkedIn User',
                        'content': f"Post found about: {keyword}",
                        'url': url,
                        'keywords_matched': keyword,
                        'created_at': datetime.now().isoformat(),
                        'priority': 'medium'
                    }
                    leads.append(lead)
            
            except Exception as e:
                print(f"⚠️  Google search error: {str(e)}")
                continue
        
        return leads

# ===========================
# Email Extraction from Content
# ===========================

def extract_emails_from_leads(leads: List[Dict]) -> List[Dict]:
    """Extract email addresses from lead content"""
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    for lead in leads:
        content = lead.get('content', '')
        emails = email_pattern.findall(content)
        if emails:
            lead['emails_found'] = list(set(emails))
            lead['priority'] = 'high'  # Boost priority if email found
    
    return leads

# ===========================
# Lead Enrichment with AI
# ===========================

def enrich_leads_with_ai(leads: List[Dict]) -> List[Dict]:
    """
    Use DeepSeek to analyze lead quality and extract intent
    """
    if not os.getenv('DEEPSEEK_API_KEY'):
        return leads
    
    for lead in leads:
        try:
            # Analyze intent
            prompt = f"""Analyze this potential client inquiry and determine:
1. Intent level (high/medium/low)
2. Type of legal service needed
3. Urgency (immediate/soon/not_urgent)

Content: {lead['content'][:500]}

Respond in JSON format: {{"intent": "high", "service_type": "personal injury", "urgency": "immediate"}}"""
            
            # Call DeepSeek API
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                try:
                    analysis = json.loads(result)
                    lead.update({
                        'ai_intent': analysis.get('intent', 'unknown'),
                        'ai_service_type': analysis.get('service_type', 'unknown'),
                        'ai_urgency': analysis.get('urgency', 'unknown')
                    })
                except:
                    pass
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"⚠️  AI enrichment error: {str(e)}")
            continue
    
    return leads

# ===========================
# Main Lead Generation Function
# ===========================

def generate_leads(
    keywords: List[str],
    platforms: List[str] = ['reddit', 'linkedin'],
    limit_per_platform: int = 50,
    output_file: str = 'leads_generated.json'
) -> List[Dict]:
    """
    Main function to generate leads from multiple platforms
    """
    print("=" * 60)
    print("🔍 LEAD GENERATION STARTED")
    print("=" * 60)
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Platforms: {', '.join(platforms)}")
    print("=" * 60)
    
    all_leads = []
    
    # Reddit scraping
    if 'reddit' in platforms:
        print("\n📱 Scraping Reddit...")
        reddit_scraper = RedditLeadScraper()
        reddit_leads = reddit_scraper.search_posts(keywords, limit=limit_per_platform)
        print(f"✅ Found {len(reddit_leads)} Reddit leads")
        all_leads.extend(reddit_leads)
    
    # LinkedIn scraping
    if 'linkedin' in platforms:
        print("\n💼 Scraping LinkedIn...")
        linkedin_scraper = LinkedInLeadScraper()
        linkedin_leads = linkedin_scraper.search_posts(keywords, limit=limit_per_platform)
        print(f"✅ Found {len(linkedin_leads)} LinkedIn leads")
        all_leads.extend(linkedin_leads)
    
    # Extract emails
    print("\n📧 Extracting contact information...")
    all_leads = extract_emails_from_leads(all_leads)
    
    # AI enrichment
    if os.getenv('DEEPSEEK_API_KEY'):
        print("\n🤖 Enriching leads with AI analysis...")
        all_leads = enrich_leads_with_ai(all_leads)
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    all_leads.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_leads, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ LEAD GENERATION COMPLETE")
    print(f"📊 Total leads found: {len(all_leads)}")
    print(f"🔥 High priority: {sum(1 for l in all_leads if l.get('priority') == 'high')}")
    print(f"⚡ Medium priority: {sum(1 for l in all_leads if l.get('priority') == 'medium')}")
    print(f"💾 Results saved to: {output_file}")
    print("=" * 60)
    
    return all_leads

# ===========================
# CLI Interface
# ===========================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate leads from LinkedIn and Reddit')
    parser.add_argument('--keywords', type=str, required=True, help='JSON array of keywords')
    parser.add_argument('--platforms', type=str, default='["reddit", "linkedin"]', help='Platforms to scrape')
    parser.add_argument('--limit', type=int, default=50, help='Limit per platform')
    parser.add_argument('--output', type=str, default='leads_generated.json', help='Output file')
    
    args = parser.parse_args()
    
    keywords = json.loads(args.keywords)
    platforms = json.loads(args.platforms)
    
    leads = generate_leads(
        keywords=keywords,
        platforms=platforms,
        limit_per_platform=args.limit,
        output_file=args.output
    )
    
    # Print sample leads
    print("\n📋 Sample Leads:")
    for lead in leads[:3]:
        print(f"\n  Platform: {lead['platform']}")
        print(f"  Author: {lead['author']}")
        print(f"  Content: {lead['content'][:100]}...")
        print(f"  Priority: {lead['priority']}")
        print(f"  URL: {lead['url']}")
