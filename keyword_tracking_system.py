"""
KEYWORD TRACKING & MENTION MONITORING SYSTEM
Replaces Google Alerts with better alternatives + extracts competitor keywords

Features:
1. Extract keywords from competitor websites
2. Track where competitors are mentioned
3. Monitor specific keywords across the web
4. Get URLs of all mentions
5. Track keyword rankings
"""

import os
import requests
import re
from collections import Counter
from urllib.parse import quote_plus
from dotenv import load_dotenv
import time

load_dotenv()

# ============================================================================
# KEYWORD EXTRACTION - From Competitor Content
# ============================================================================

def extract_keywords_from_content(text: str, min_word_length: int = 4, top_n: int = 50) -> dict:
    """
    Extract top keywords from content with frequency and context
    Returns: {keyword: {count, urls, contexts}}
    """
    # Clean text
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Stop words to exclude
    stop_words = {
        'this', 'that', 'with', 'from', 'have', 'been', 'were', 'will',
        'your', 'about', 'more', 'other', 'into', 'would', 'could', 'should',
        'their', 'what', 'which', 'when', 'where', 'who', 'how', 'than',
        'these', 'those', 'some', 'such', 'only', 'very', 'just', 'even'
    }
    
    # Extract words
    words = text.split()
    words = [w for w in words if len(w) >= min_word_length and w not in stop_words]
    
    # Count frequency
    word_counts = Counter(words)
    
    # Get top keywords
    top_keywords = dict(word_counts.most_common(top_n))
    
    # Extract 2-word phrases (bigrams)
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    bigram_counts = Counter(bigrams)
    top_bigrams = dict(bigram_counts.most_common(20))
    
    # Extract 3-word phrases (trigrams)
    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
    trigram_counts = Counter(trigrams)
    top_trigrams = dict(trigram_counts.most_common(10))
    
    return {
        'single_keywords': top_keywords,
        'two_word_phrases': top_bigrams,
        'three_word_phrases': top_trigrams
    }


# ============================================================================
# GOOGLE ALERTS ALTERNATIVE - Free Mention Tracking
# ============================================================================

def setup_google_alerts_alternative():
    """
    Guide for setting up Google Alerts alternatives (all FREE)
    """
    return {
        'google_alerts': {
            'name': 'Google Alerts (Limited)',
            'url': 'https://www.google.com/alerts',
            'free': True,
            'limits': 'Basic mentions only, delayed notifications',
            'setup': '1. Visit link 2. Enter keyword 3. Choose frequency 4. Get email updates'
        },
        'talkwalker_alerts': {
            'name': 'Talkwalker Alerts (Best Free Alternative)',
            'url': 'https://www.talkwalker.com/alerts',
            'free': True,
            'limits': 'Unlimited alerts, real-time',
            'setup': '1. Visit link 2. Enter email & keyword 3. Get instant notifications',
            'features': ['Social media mentions', 'News mentions', 'Blog mentions']
        },
        'mention': {
            'name': 'Mention (Freemium)',
            'url': 'https://mention.com',
            'free': 'Limited (1 alert, 250 mentions/month)',
            'paid': '$29/month for unlimited',
            'features': ['Real-time alerts', 'Social listening', 'Competitor tracking']
        },
        'brandmentions': {
            'name': 'Brand24/BrandMentions',
            'url': 'https://brandmentions.com',
            'free': '14-day trial',
            'paid': '$99/month',
            'features': ['Sentiment analysis', 'Influencer identification', 'Backlink tracking']
        }
    }


# ============================================================================
# WEB SCRAPING - Find Keyword Mentions via APIs
# ============================================================================

def search_keyword_mentions_brave(keyword: str, max_results: int = 20) -> list:
    """
    Search for keyword mentions using Brave Search API (2000 free/month)
    Returns list of URLs where keyword appears
    """
    api_key = os.getenv('BRAVE_SEARCH_API_KEY')
    if not api_key:
        return []
    
    try:
        url = 'https://api.search.brave.com/res/v1/web/search'
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': api_key
        }
        params = {
            'q': keyword,
            'count': max_results,
            'text_decorations': False,
            'search_lang': 'en'
        }
        
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        
        if resp.status_code != 200:
            print(f"  ⚠️  Brave Search error: {resp.status_code}")
            return []
        
        data = resp.json()
        results = []
        
        for item in data.get('web', {}).get('results', []):
            results.append({
                'url': item.get('url'),
                'title': item.get('title'),
                'description': item.get('description'),
                'published': item.get('published', 'N/A')
            })
        
        return results
        
    except Exception as e:
        print(f"  ⚠️  Brave Search error: {str(e)[:50]}")
        return []


def search_keyword_mentions_serpapi(keyword: str, max_results: int = 20) -> list:
    """
    Search for keyword mentions using SerpApi (100 free/month)
    Returns list of URLs where keyword appears
    """
    api_key = os.getenv('SERPAPI_KEY')
    if not api_key:
        return []
    
    try:
        url = 'https://serpapi.com/search'
        params = {
            'q': keyword,
            'api_key': api_key,
            'num': max_results,
            'engine': 'google'
        }
        
        resp = requests.get(url, params=params, timeout=10)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        results = []
        
        for item in data.get('organic_results', []):
            results.append({
                'url': item.get('link'),
                'title': item.get('title'),
                'snippet': item.get('snippet'),
                'position': item.get('position')
            })
        
        return results
        
    except Exception as e:
        print(f"  ⚠️  SerpApi error: {str(e)[:50]}")
        return []


# ============================================================================
# KEYWORD TRACKING - Monitor Competitor Keywords
# ============================================================================

def track_competitor_keywords(competitor_url: str, keywords: list) -> dict:
    """
    Track specific keywords on competitor website
    Returns URLs where each keyword appears
    """
    results = {}
    
    for keyword in keywords:
        # Use site: operator to search within specific domain
        search_query = f"site:{competitor_url} {keyword}"
        
        # Try Brave first (2000 free/month)
        mentions = search_keyword_mentions_brave(search_query, max_results=10)
        
        if not mentions:
            # Fallback to SerpApi (100 free/month)
            mentions = search_keyword_mentions_serpapi(search_query, max_results=10)
        
        results[keyword] = {
            'total_mentions': len(mentions),
            'urls': [m['url'] for m in mentions],
            'titles': [m['title'] for m in mentions],
            'contexts': [m.get('description', m.get('snippet', '')) for m in mentions]
        }
        
        time.sleep(0.5)  # Rate limiting
    
    return results


# ============================================================================
# BRAND MENTION TRACKING - Find Where Brand is Mentioned
# ============================================================================

def find_brand_mentions(brand_name: str, exclude_domain: str = None) -> dict:
    """
    Find all web mentions of a brand (competitor intelligence)
    
    Args:
        brand_name: Name to search for
        exclude_domain: Exclude results from this domain (e.g., competitor's own site)
    
    Returns:
        Dictionary with mention URLs, contexts, and sources
    """
    # Build search query
    search_query = f'"{brand_name}"'
    if exclude_domain:
        search_query += f' -site:{exclude_domain}'
    
    # Search with Brave
    brave_results = search_keyword_mentions_brave(search_query, max_results=50)
    
    # Categorize mentions
    mentions = {
        'news_sites': [],
        'social_media': [],
        'review_sites': [],
        'forums': [],
        'blogs': [],
        'other': []
    }
    
    social_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com']
    news_domains = ['news.', 'cnn.com', 'bbc.com', 'reuters.com', 'bloomberg.com']
    review_domains = ['yelp.com', 'trustpilot.com', 'bbb.org', 'google.com/maps']
    forum_domains = ['reddit.com', 'quora.com', 'forum', 'community']
    
    for result in brave_results:
        url = result['url'].lower()
        
        if any(domain in url for domain in social_domains):
            mentions['social_media'].append(result)
        elif any(domain in url for domain in news_domains):
            mentions['news_sites'].append(result)
        elif any(domain in url for domain in review_domains):
            mentions['review_sites'].append(result)
        elif any(domain in url for domain in forum_domains):
            mentions['forums'].append(result)
        elif 'blog' in url:
            mentions['blogs'].append(result)
        else:
            mentions['other'].append(result)
    
    return mentions


# ============================================================================
# INTEGRATION WITH COMPETITOR PROFILER
# ============================================================================

def add_keyword_tracking_to_profiler(competitor_data: dict) -> dict:
    """
    Add keyword tracking data to existing competitor profile
    
    Args:
        competitor_data: Existing competitor data from profiler
    
    Returns:
        Enhanced data with keyword tracking
    """
    domain = competitor_data.get('domain', '')
    name = competitor_data.get('name', '')
    html_content = competitor_data.get('html_content', '')
    
    # Extract keywords from their content
    if html_content:
        keywords_data = extract_keywords_from_content(html_content)
        competitor_data['top_keywords'] = list(keywords_data['single_keywords'].keys())[:20]
        competitor_data['top_phrases'] = list(keywords_data['two_word_phrases'].keys())[:10]
        competitor_data['keyword_density'] = keywords_data['single_keywords']
    
    # Find where competitor is mentioned
    if name:
        mentions = find_brand_mentions(name, exclude_domain=domain)
        competitor_data['mention_count_social'] = len(mentions['social_media'])
        competitor_data['mention_count_news'] = len(mentions['news_sites'])
        competitor_data['mention_count_reviews'] = len(mentions['review_sites'])
        competitor_data['mention_count_forums'] = len(mentions['forums'])
        competitor_data['mention_urls_social'] = [m['url'] for m in mentions['social_media'][:5]]
        competitor_data['mention_urls_news'] = [m['url'] for m in mentions['news_sites'][:5]]
        competitor_data['mention_urls_reviews'] = [m['url'] for m in mentions['review_sites'][:5]]
    
    return competitor_data


# ============================================================================
# SETUP GUIDE
# ============================================================================

def print_setup_guide():
    """Print comprehensive setup guide for keyword tracking"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║            KEYWORD TRACKING & MENTION MONITORING - SETUP GUIDE           ║
╚══════════════════════════════════════════════════════════════════════════╝

📊 FREE GOOGLE ALERTS ALTERNATIVES:
══════════════════════════════════════════════════════════════════════════

1. TALKWALKER ALERTS (Best Free Option)
   URL: https://www.talkwalker.com/alerts
   Features: ✅ Unlimited alerts
            ✅ Real-time monitoring
            ✅ Social media + web mentions
            ✅ No registration required
   
2. GOOGLE ALERTS (Limited but Free)
   URL: https://www.google.com/alerts
   Features: ✅ Email notifications
            ⚠️  Limited to basic mentions
            ⚠️  Delayed updates
   
3. BRAND24 (14-Day Free Trial)
   URL: https://brand24.com
   Features: ✅ Sentiment analysis
            ✅ Influencer identification
            ✅ Social listening
            💰 $99/month after trial

══════════════════════════════════════════════════════════════════════════

🔧 API-BASED TRACKING (Already Integrated):
══════════════════════════════════════════════════════════════════════════

Your profiler now includes:
✅ Brave Search API - 2,000 searches/month (FREE)
✅ SerpApi - 100 searches/month (FREE)
✅ Automatic keyword extraction from competitor content
✅ Brand mention tracking across web

══════════════════════════════════════════════════════════════════════════

📈 NEW COLUMNS ADDED TO CSV:
══════════════════════════════════════════════════════════════════════════

• top_keywords: Top 20 keywords used by competitor
• top_phrases: Top 10 2-word phrases used by competitor
• keyword_density: Frequency of each keyword
• mention_count_social: Times mentioned on social media
• mention_count_news: Times mentioned in news articles
• mention_count_reviews: Times mentioned in review sites
• mention_count_forums: Times mentioned in forums/Reddit
• mention_urls_social: URLs of social media mentions (top 5)
• mention_urls_news: URLs of news mentions (top 5)
• mention_urls_reviews: URLs of review site mentions (top 5)

══════════════════════════════════════════════════════════════════════════

🎯 HOW TO USE:
══════════════════════════════════════════════════════════════════════════

1. Run your competitor profiler - keywords are extracted automatically
2. Check CSV for 'top_keywords' and 'mention_urls_*' columns
3. Set up Talkwalker Alerts for real-time monitoring:
   → Visit https://www.talkwalker.com/alerts
   → Enter competitor brand name
   → Choose "As it happens" for real-time alerts
   → Add email address
   → Repeat for each competitor

4. Monitor competitor keywords:
   → Use their top_keywords from CSV
   → Create alerts for each important keyword
   → Track when they publish new content about these topics

══════════════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    print_setup_guide()
