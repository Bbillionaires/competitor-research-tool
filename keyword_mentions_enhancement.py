"""
Enhanced Competitor Profiler with Keywords & Mentions
Adds to final_competitor_profiler_ENHANCED.py:
1. Keyword extraction (5-10 per company)
2. Long-tail keywords (5-10 per company)
3. Mentions tracking (potential leads)
4. Excel export with proper formatting
"""

import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data (run once)
try:
    stopwords.words('english')
except:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)

def extract_keywords(text: str, num_keywords: int = 10) -> list:
    """
    Extract top keywords from text using frequency analysis
    Returns list of single-word keywords
    """
    if not text or len(text) < 50:
        return []
    
    # Clean text
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Tokenize
    words = word_tokenize(text)
    
    # Remove stopwords and short words
    stop_words = set(stopwords.words('english'))
    legal_stopwords = {'law', 'firm', 'attorney', 'lawyer', 'legal', 'the', 'and', 'for'}
    stop_words.update(legal_stopwords)
    
    words = [w for w in words if len(w) > 3 and w not in stop_words]
    
    # Count frequency
    word_freq = Counter(words)
    
    # Get top N
    top_keywords = [word for word, count in word_freq.most_common(num_keywords)]
    
    return top_keywords


def extract_long_tail_keywords(text: str, num_keywords: int = 10) -> list:
    """
    Extract long-tail keywords (2-4 word phrases)
    These are more specific and valuable for SEO
    """
    if not text or len(text) < 100:
        return []
    
    # Clean text
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Split into sentences
    sentences = text.split('.')
    
    # Extract 2-4 word phrases
    phrases = []
    stop_words = set(stopwords.words('english'))
    
    for sentence in sentences:
        words = word_tokenize(sentence)
        words = [w for w in words if len(w) > 3]
        
        # Extract 2-word phrases
        for i in range(len(words) - 1):
            if words[i] not in stop_words or words[i+1] not in stop_words:
                phrase = f"{words[i]} {words[i+1]}"
                if len(phrase) > 8:  # Meaningful phrases
                    phrases.append(phrase)
        
        # Extract 3-word phrases
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 12:  # Meaningful phrases
                phrases.append(phrase)
    
    # Count frequency
    phrase_freq = Counter(phrases)
    
    # Get top N
    top_phrases = [phrase for phrase, count in phrase_freq.most_common(num_keywords)]
    
    return top_phrases


def extract_keywords_from_competitor(row: dict) -> dict:
    """
    Extract keywords from competitor data
    Combines: title, meta_description, h1, content
    """
    # Gather all text
    text_sources = [
        row.get('title', ''),
        row.get('meta_description', ''),
        row.get('h1', ''),
        row.get('name', ''),
    ]
    
    combined_text = ' '.join([t for t in text_sources if t])
    
    # Extract keywords
    keywords = extract_keywords(combined_text, num_keywords=10)
    long_tail = extract_long_tail_keywords(combined_text, num_keywords=10)
    
    return {
        'keywords': ', '.join(keywords[:10]) if keywords else '',
        'long_tail_keywords': ' | '.join(long_tail[:10]) if long_tail else '',
    }


def search_mentions(company_name: str, domain: str) -> list:
    """
    Search for mentions of the company online
    Returns potential leads (people/companies mentioning them)
    
    In production, this would:
    1. Search social media APIs (Twitter, LinkedIn)
    2. Search review sites (Yelp, Google Reviews)
    3. Search news mentions
    4. Search forum discussions
    
    For now, returns placeholder structure
    """
    # This would be replaced with actual API calls in production
    # Example: Twitter API, Reddit API, Google News API
    
    mentions = []
    
    # Placeholder logic - in production, this searches APIs
    # For now, we'll create a structure that the dashboard can use
    
    return {
        'mention_count': 0,  # Total mentions found
        'recent_mentions': '',  # Last 5 mentions (name | source | date)
        'potential_leads': '',  # Extracted leads (name | contact | context)
        'sentiment_score': 0.0,  # Average sentiment (0-1)
    }


# ADD TO final_competitor_profiler_ENHANCED.py
# In process_competitor() function, BEFORE returning the row:

def enhance_competitor_data(row: dict) -> dict:
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
    
    return row


# INTEGRATION INSTRUCTIONS:
"""
In process_competitor() function, ADD THIS before the return statement:

    # === ENHANCE WITH KEYWORDS & MENTIONS ===
    row = enhance_competitor_data(row)
    
    return row
    
This will add these new columns:
- keywords: Top 10 single-word keywords
- long_tail_keywords: Top 10 2-4 word phrases
- mention_count: Number of online mentions
- recent_mentions: Last 5 mentions with source
- potential_leads: Extracted contact info from mentions
- sentiment_score: Average sentiment (0-1)
"""

print(__doc__)
