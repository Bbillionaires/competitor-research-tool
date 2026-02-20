"""
KEYWORD TRACKING INTEGRATION
Add this to final_competitor_profiler_complete.py

This adds:
1. Keyword extraction from competitor content
2. Brand mention tracking
3. URLs of all mentions
4. Keyword density analysis
"""

# ============================================================================
# STEP 1: Add these imports at the top of your file
# ============================================================================
# LOCATION: Around line 10-30 (with other imports)

from collections import Counter
import re

# ============================================================================
# STEP 2: Add keyword extraction function
# ============================================================================
# LOCATION: Around line 400-500 (before process_competitor function)

def extract_keywords_from_html(html: str, top_n: int = 20) -> dict:
    """
    Extract top keywords from HTML content
    Returns single keywords, 2-word phrases, and 3-word phrases
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
    except:
        # Fallback if BeautifulSoup fails
        text = re.sub(r'<[^>]+>', ' ', html)
    
    # Clean and normalize
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Stop words
    stop_words = {
        'this', 'that', 'with', 'from', 'have', 'been', 'were', 'will',
        'your', 'about', 'more', 'other', 'into', 'would', 'could', 'should',
        'their', 'what', 'which', 'when', 'where', 'who', 'how', 'than',
        'these', 'those', 'some', 'such', 'only', 'very', 'just', 'even',
        'also', 'can', 'may', 'use', 'used', 'using', 'make', 'made',
        'get', 'got', 'all', 'any', 'each', 'every', 'both', 'either',
        'and', 'or', 'but', 'not', 'for', 'the', 'are', 'was', 'has'
    }
    
    # Extract words (4+ chars)
    words = [w for w in text.split() if len(w) >= 4 and w not in stop_words and not w.isdigit()]
    
    # Count single keywords
    word_counts = Counter(words)
    top_keywords = dict(word_counts.most_common(top_n))
    
    # Extract 2-word phrases
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    bigram_counts = Counter(bigrams)
    top_phrases = dict(bigram_counts.most_common(10))
    
    return {
        'keywords': list(top_keywords.keys()),
        'phrases': list(top_phrases.keys()),
        'keyword_counts': top_keywords
    }


def search_brand_mentions(brand_name: str, exclude_domain: str = None) -> dict:
    """
    Search for brand mentions using Brave Search API
    Returns categorized URLs where brand is mentioned
    """
    api_key = os.getenv('BRAVE_SEARCH_API_KEY')
    if not api_key:
        return {
            'social': [], 'news': [], 'reviews': [], 'forums': [],
            'total': 0
        }
    
    try:
        # Build query
        query = f'"{brand_name}"'
        if exclude_domain:
            query += f' -site:{exclude_domain}'
        
        url = 'https://api.search.brave.com/res/v1/web/search'
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': api_key
        }
        params = {
            'q': query,
            'count': 20,
            'text_decorations': False
        }
        
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        
        if resp.status_code != 200:
            return {'social': [], 'news': [], 'reviews': [], 'forums': [], 'total': 0}
        
        data = resp.json()
        results = data.get('web', {}).get('results', [])
        
        # Categorize mentions
        social = []
        news = []
        reviews = []
        forums = []
        
        social_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']
        news_domains = ['news.', '.news', 'cnn.com', 'bbc.', 'reuters.com']
        review_domains = ['yelp.com', 'trustpilot.com', 'bbb.org', 'reviews']
        forum_domains = ['reddit.com', 'quora.com', 'forum']
        
        for item in results:
            url_lower = item.get('url', '').lower()
            
            if any(d in url_lower for d in social_domains):
                social.append(item.get('url'))
            elif any(d in url_lower for d in news_domains):
                news.append(item.get('url'))
            elif any(d in url_lower for d in review_domains):
                reviews.append(item.get('url'))
            elif any(d in url_lower for d in forum_domains):
                forums.append(item.get('url'))
        
        return {
            'social': social[:5],
            'news': news[:5],
            'reviews': reviews[:5],
            'forums': forums[:5],
            'total': len(results)
        }
        
    except Exception as e:
        print(f"  ⚠️  Mention search error: {str(e)[:50]}")
        return {'social': [], 'news': [], 'reviews': [], 'forums': [], 'total': 0}


# ============================================================================
# STEP 3: Update process_competitor function
# ============================================================================
# LOCATION: Find the section where you create the 'row' dictionary
# Add these new fields to the row dictionary

"""
FIND THIS SECTION (around line 1000-1100):

    row = {
        "name": g.get("g_name", "") or title,
        "address": g.get("g_address", ""),
        "domain": domain,
        "url": url,
        # ... other fields ...
    }

ADD THESE NEW LINES BEFORE THE CLOSING }:
"""

# Extract keywords from content
keyword_data = {'keywords': [], 'phrases': [], 'keyword_counts': {}}
if html_content and len(html_content) > 500:
    try:
        keyword_data = extract_keywords_from_html(html_content, top_n=20)
    except Exception as e:
        print(f"  ⚠️  Keyword extraction error: {str(e)[:50]}")

# Search for brand mentions (only if Brave API available)
mention_data = {'social': [], 'news': [], 'reviews': [], 'forums': [], 'total': 0}
brand_name = g.get("g_name", "") or title
if brand_name and os.getenv('BRAVE_SEARCH_API_KEY'):
    try:
        mention_data = search_brand_mentions(brand_name, exclude_domain=domain)
    except Exception as e:
        print(f"  ⚠️  Mention search error: {str(e)[:50]}")

# Add to row dictionary (add these lines to your existing row dict):
row["top_keywords"] = ", ".join(keyword_data['keywords'][:20])  # Top 20 keywords
row["top_phrases"] = ", ".join(keyword_data['phrases'][:10])  # Top 10 2-word phrases
row["keyword_density_top5"] = ", ".join([f"{k}:{v}" for k, v in list(keyword_data['keyword_counts'].items())[:5]])  # Top 5 with counts

row["mention_count_social"] = len(mention_data['social'])
row["mention_count_news"] = len(mention_data['news'])
row["mention_count_reviews"] = len(mention_data['reviews'])
row["mention_count_forums"] = len(mention_data['forums'])
row["mention_count_total"] = mention_data['total']

row["mention_urls_social"] = "; ".join(mention_data['social'])  # URLs separated by semicolon
row["mention_urls_news"] = "; ".join(mention_data['news'])
row["mention_urls_reviews"] = "; ".join(mention_data['reviews'])
row["mention_urls_forums"] = "; ".join(mention_data['forums'])


# ============================================================================
# STEP 4: Update priority columns for CSV output
# ============================================================================
# LOCATION: Find where priority_columns is defined (around line 1240-1250)

# BEFORE:
"""
priority_columns = ['name', 'address', 'domain', 'url', 'title', 'query', 
                   'phones', 'emails', 'word_count', ...]
"""

# AFTER (add these new columns to the priority list):
"""
priority_columns = [
    'name', 'address', 'domain', 'url', 'title', 'query',
    'phones', 'emails',
    
    # KEYWORD TRACKING (NEW)
    'top_keywords', 'top_phrases', 'keyword_density_top5',
    
    # MENTION TRACKING (NEW)  
    'mention_count_total', 'mention_count_social', 'mention_count_news',
    'mention_count_reviews', 'mention_count_forums',
    'mention_urls_social', 'mention_urls_news', 'mention_urls_reviews',
    'mention_urls_forums',
    
    # EXISTING FIELDS
    'word_count', 'g_rating', 'g_reviews', 'traffic_estimate',
    # ... rest of your fields ...
]
"""

# ============================================================================
# COMPLETE EXAMPLE - What the row dictionary should look like
# ============================================================================

"""
row = {
    # Basic info
    "name": g.get("g_name", "") or title,
    "address": g.get("g_address", ""),
    "domain": domain,
    "url": url,
    "title": title,
    "query": query,
    
    # Contact
    "phones": ", ".join(phones),
    "emails": ", ".join(emails),
    
    # KEYWORD TRACKING (NEW) ✨
    "top_keywords": ", ".join(keyword_data['keywords'][:20]),
    "top_phrases": ", ".join(keyword_data['phrases'][:10]),
    "keyword_density_top5": ", ".join([f"{k}:{v}" for k, v in list(keyword_data['keyword_counts'].items())[:5]]),
    
    # MENTION TRACKING (NEW) ✨
    "mention_count_social": len(mention_data['social']),
    "mention_count_news": len(mention_data['news']),
    "mention_count_reviews": len(mention_data['reviews']),
    "mention_count_forums": len(mention_data['forums']),
    "mention_count_total": mention_data['total'],
    "mention_urls_social": "; ".join(mention_data['social']),
    "mention_urls_news": "; ".join(mention_data['news']),
    "mention_urls_reviews": "; ".join(mention_data['reviews']),
    "mention_urls_forums": "; ".join(mention_data['forums']),
    
    # ... rest of your existing fields ...
}
"""

# ============================================================================
# WHAT YOU GET IN YOUR CSV
# ============================================================================
"""
New columns added:

1. top_keywords - "real estate, investment, property, jacksonville, florida, ..."
2. top_phrases - "real estate investment, property management, ..."
3. keyword_density_top5 - "investment:45, property:38, real:32, estate:32, jacksonville:28"

4. mention_count_total - 127 (total mentions found across web)
5. mention_count_social - 23 (Facebook, Twitter, LinkedIn mentions)
6. mention_count_news - 5 (news articles mentioning them)
7. mention_count_reviews - 8 (Yelp, BBB, review sites)
8. mention_count_forums - 12 (Reddit, Quora mentions)

9. mention_urls_social - "https://facebook.com/...; https://linkedin.com/..."
10. mention_urls_news - "https://news.site/article; https://..."
11. mention_urls_reviews - "https://yelp.com/...; https://bbb.org/..."
12. mention_urls_forums - "https://reddit.com/...; https://..."

All URLs are clickable links you can visit to see the mentions!
"""
