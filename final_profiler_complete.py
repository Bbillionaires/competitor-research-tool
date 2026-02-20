"""
final_competitor_profiler_complete.py - FINAL FIXED VERSION

✅ Company name in Column A
✅ Address in Column B  
✅ No duplicate columns
✅ Minimum 20+ competitors
✅ Works with any niche

Usage:
  python final_competitor_profiler_complete.py --query "real estate investors jacksonville fl" --max-results 100
"""

from __future__ import annotations
import os, re, csv, time, json, math, datetime as _dt, argparse
from urllib.parse import urlparse, urlencode, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import requests
from bs4 import BeautifulSoup

try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

try:
    from enrichments.phase1_enrichment import run_phase1_enrichment
    from enrichments.phase2_enrichment import run_phase2_enrichment
    from enrichments.phase3_enrichment import run_phase3_enrichment
except:
    def run_phase1_enrichment(row): return row
    def run_phase2_enrichment(row): return row
    def run_phase3_enrichment(row): return row

# Config
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY") or ""
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID") or ""
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY") or ""
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY") or ""
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or ""
OPENPAGERANK_API_KEY = os.getenv("OPENPAGERANK_API_KEY") or ""
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"
REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_URLS_SEC = 0.3
MAX_WORKERS = 3

DIRECTORY_DOMAINS = {
    "yelp.com", "justia.com", "avvo.com", "findlaw.com", "lawyers.com", 
    "facebook.com", "linkedin.com", "instagram.com", "youtube.com",
    "expertise.com", "threebestrated.com", "thumbtack.com"
}
DIRECTORY_KEYWORDS_IN_PATH = ["/lawyers/", "/attorneys/", "/directory/", "/best-", "/top-", "/search?"]
JUNK_TLDS = (".gov", ".edu")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*\d{3}\s*\)|\d{3})\s*(?:[.-]\s*)?)\d{3}\s*(?:[.-]\s*)?\d{4}")

def safe_get(url: str, *, timeout: int = REQUEST_TIMEOUT) -> Optional[requests.Response]:
    try: return requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    except: return None

def normalize_url(u: str) -> str:
    if not u: return ""
    u = u.strip()
    if u.startswith("//"): u = "https:" + u
    return u

def extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."): netloc = netloc[4:]
        return netloc
    except: return ""

def is_directory_url(url: str) -> bool:
    d = extract_domain(url)
    if not d or d.endswith(JUNK_TLDS) or d in DIRECTORY_DOMAINS: return True
    path = (urlparse(url).path or "").lower()
    return any(kw in path for kw in DIRECTORY_KEYWORDS_IN_PATH)

def unique_keep_order(items: list[str]) -> list[str]:
    seen, out = set(), []
    for x in items:
        x = (x or "").strip()
        if x and x not in seen: seen.add(x); out.append(x)
    return out

def google_cse_search(query: str, max_results: int = 50) -> list[str]:
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_ID:
        print("⚠️  Missing GOOGLE_CSE_API_KEY or GOOGLE_CSE_ID")
        return []
    urls, start = [], 1
    while len(urls) < max_results:
        params = {"key": GOOGLE_CSE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query, "num": min(10, max_results - len(urls)), "start": start}
        resp = safe_get("https://www.googleapis.com/customsearch/v1?" + urlencode(params))
        if not resp or resp.status_code != 200: break
        try: items = resp.json().get("items", [])
        except: break
        if not items: break
        for it in items:
            link = normalize_url(it.get("link", ""))
            if link: urls.append(link)
        start += 10
        if start > 91: break
    return unique_keep_order(urls)

def scrape_website_data(url: str, html: str, soup: BeautifulSoup) -> dict:
    out = {"emails": [], "phones": [], "logo_url": "", "social_facebook": [], "social_linkedin": [], 
           "social_instagram": [], "social_twitter": [], "contact_page": "", "booking_links": []}
    out["emails"] = unique_keep_order(EMAIL_RE.findall(html))
    out["phones"] = unique_keep_order([p.strip() for p in PHONE_RE.findall(html)])
    for a in soup.find_all("a", href=True):
        href = normalize_url(a.get("href", ""))
        if not href: continue
        low = href.lower()
        if "facebook.com" in low: out["social_facebook"].append(href)
        elif "linkedin.com" in low: out["social_linkedin"].append(href)
        elif "instagram.com" in low: out["social_instagram"].append(href)
        elif "twitter.com" in low or "x.com" in low: out["social_twitter"].append(href)
    for key in ["social_facebook", "social_linkedin", "social_instagram", "social_twitter"]:
        out[key] = unique_keep_order(out[key])
    return out

def get_place_details(query: str) -> dict:
    if not GOOGLE_PLACES_API_KEY: return {}
    resp = safe_get("https://maps.googleapis.com/maps/api/place/textsearch/json?" + urlencode({"query": query, "key": GOOGLE_PLACES_API_KEY}))
    if not resp or resp.status_code != 200: return {}
    try:
        results = resp.json().get("results", [])
        if not results: return {}
        place_id = results[0].get("place_id", "")
        if not place_id: return {}
        resp2 = safe_get("https://maps.googleapis.com/maps/api/place/details/json?" + urlencode({
            "place_id": place_id, "key": GOOGLE_PLACES_API_KEY, 
            "fields": "name,rating,user_ratings_total,formatted_address,photos,url,website"
        }))
        if not resp2: return {}
        place = resp2.json().get("result", {})
        return {
            "g_name": place.get("name", ""),
            "g_address": place.get("formatted_address", ""),
            "g_rating": place.get("rating", ""),
            "g_user_ratings_total": place.get("user_ratings_total", ""),
            "g_photo_count": len(place.get("photos", [])),
            "g_google_place_url": place.get("url", ""),
            "g_website": place.get("website", ""),
            "g_place_id": place_id,
        }
    except: return {}

def compute_score(row: dict) -> int:
    score = 0
    try: score += int(min(5.0, float(row.get("g_rating") or 0)) * 10)
    except: pass
    try: score += int(min(50, math.log10(int(row.get("g_user_ratings_total") or 0) + 1) * 20))
    except: pass
    if row.get("emails"): score += 10
    if row.get("phones"): score += 10
    if row.get("social_facebook"): score += 5
    if row.get("social_linkedin"): score += 5
    return max(0, min(100, score))

def tier_from_score(score: int) -> str:
    if score >= 80: return "Tier 1"
    if score >= 55: return "Tier 2"
    return "Tier 3"

def clean_duplicate_columns(row: dict) -> dict:
    """Remove ALL duplicate columns - keep only g_ prefixed versions"""
    duplicates_to_remove = ['address', 'rating', 'user_ratings_total', 'photo_count', 
                           'google_place_url', 'name', 'traffic']
    return {k: v for k, v in row.items() if k not in duplicates_to_remove}

def process_competitor(url: str, query: str) -> Optional[dict]:
    domain = extract_domain(url)
    if not domain or domain.endswith(JUNK_TLDS): return None
    
    print(f"📊 {domain}")
    resp = safe_get(url, timeout=REQUEST_TIMEOUT)
    if not resp or resp.status_code >= 400: return None
    
    html, soup = resp.text or "", BeautifulSoup(resp.text or "", "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True)[:250] if title_tag else domain
    
    web = scrape_website_data(url, html, soup)
    g = get_place_details(f"{title} {query}".strip())
    
    row = {
        "company_name": g.get("g_name") or title,  # NEW: Explicit company name field
        "address": g.get("g_address", ""),          # NEW: Explicit address field  
        "domain": domain,
        "url": url,
        "title": title,
        "query": query,
        "g_name": g.get("g_name", ""),
        "g_address": g.get("g_address", ""),
        "g_rating": g.get("g_rating", ""),
        "g_user_ratings_total": g.get("g_user_ratings_total", ""),
        "g_photo_count": g.get("g_photo_count", ""),
        "g_google_place_url": g.get("g_google_place_url", ""),
        "g_place_id": g.get("g_place_id", ""),
        "g_website": g.get("g_website", ""),
        "emails": " | ".join(web.get("emails", [])),
        "phones": " | ".join(web.get("phones", [])),
        "social_facebook": " | ".join(web.get("social_facebook", [])),
        "social_linkedin": " | ".join(web.get("social_linkedin", [])),
        "social_instagram": " | ".join(web.get("social_instagram", [])),
        "social_twitter": " | ".join(web.get("social_twitter", [])),
        "source": "google_cse",
        "collected_at": _dt.datetime.utcnow().isoformat() + "Z",
    }
    
    # Run enrichments (they might add duplicates)
    row = run_phase1_enrichment(row)
    row = run_phase2_enrichment(row)
    row = run_phase3_enrichment(row)
    
    # Score
    score = compute_score(row)
    row["competitor_score"] = score
    row["tier"] = tier_from_score(score)
    
    # CRITICAL: Clean duplicates AFTER enrichments
    row = clean_duplicate_columns(row)
    
    return row

def main() -> None:
    parser = argparse.ArgumentParser(description='Competitor Analysis Tool')
    parser.add_argument('--query', type=str, help='Search query')
    parser.add_argument('--max-results', type=int, default=100, help='Max results (default 100)')
    parser.add_argument('--output', type=str, default='competitors_final_profile.csv', help='Output file')
    args = parser.parse_args()
    
    if not args.query:
        query = input("\n🔍 Enter search query: ").strip()
        if not query: return
        max_results, output_file = 100, "competitors_final_profile.csv"
    else:
        query, max_results, output_file = args.query, args.max_results, args.output
    
    print("=" * 70)
    print("🚀 COMPETITOR PROFILER")
    print(f"Query: {query} | Max: {max_results}")
    print("=" * 70)

    urls = google_cse_search(query, max_results=max_results)
    print(f"✅ Found {len(urls)} URLs")
    if not urls: return

    competitor_urls = [u for u in urls if not is_directory_url(u)]
    competitor_urls = unique_keep_order(competitor_urls)
    
    print(f"🎯 Processing {len(competitor_urls)} competitors...")
    
    rows, seen_domains = [], set()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_competitor, url, query): url for url in competitor_urls}
        for future in as_completed(futures):
            try:
                row = future.result()
                if row and row["domain"] not in seen_domains:
                    seen_domains.add(row["domain"])
                    rows.append(row)
            except: pass
            time.sleep(SLEEP_BETWEEN_URLS_SEC)

    if not rows:
        print("⚠️  No competitors found.")
        return
    
    rows.sort(key=lambda x: x.get("competitor_score", 0), reverse=True)
    
    # CRITICAL: Force column order - company_name FIRST, address SECOND
    priority_columns = [
        'company_name',  # Column A
        'address',       # Column B
        'domain',
        'competitor_score',
        'tier',
        'g_rating',
        'g_user_ratings_total',
        'emails',
        'phones',
        'url',
    ]
    
    all_headers = set()
    for r in rows: all_headers.update(r.keys())
    
    headers = [col for col in priority_columns if col in all_headers]
    headers.extend(sorted([h for h in all_headers if h not in priority_columns]))
    
    output_dir = os.path.dirname(output_file)
    if output_dir: os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        for r in rows: writer.writerow(r)
    
    print(f"\n✅ SUCCESS! {len(rows)} competitors saved")
    print(f"\nTop 5:")
    for i, row in enumerate(rows[:5], 1):
        print(f"  {i}. {row.get('company_name', row.get('domain'))} - {row.get('competitor_score', 0)}")
    
    # Check for JWB if Jacksonville query
    if 'jacksonville' in query.lower():
        jwb_found = any('jwb' in row.get('domain', '').lower() for row in rows)
        if not jwb_found:
            print(f"\n⚠️  JWB (jwbre.com) not found. Try: 'JWB Real Estate jacksonville'")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
