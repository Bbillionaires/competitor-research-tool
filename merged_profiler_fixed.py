
import csv
import requests
import re
import time
import tldextract
from bs4 import BeautifulSoup
from urllib.parse import urlencode

# CONFIGURATION
GOOGLE_API_KEY = "AIzaSyAsX5EHoJ4Vfis4z20zWxNB4r7yq4Kihfc"
GOOGLE_CX = "YOUR_CX_ID"
GOOGLE_API_COST_PER_CALL = 0.005  # Example: $0.005 per query
MIN_PROFIT_PER_LOOKUP = 0.015  # Require at least $0.015 value to justify cost

EXCLUDED_DOMAINS = [
    "youtube.com", "brightlocal.com", "similarsites.com",
    "cityofventura.ca.gov", "jobs.tjx.com", "venturaattorneys.org"
]

CSV_HEADERS = [
    "Title", "URL", "Domain", "EstimatedTraffic",
    "AvvoRating", "AvvoReviews", "YelpReviews", "YelpStars", "YelpPhotos"
]

paid_api_calls = 0
enriched_rows = []

def ddg_search(query, max_results=10):
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            return [r for r in ddgs.text(query, max_results=max_results)]
    except Exception as e:
        print("DDG Error:", e)
        return []

def google_search(query):
    global paid_api_calls
    if GOOGLE_API_KEY == "AIzaSyAsX5EHoJ4Vfis4z20zWxNB4r7yq4Kihfc":
        return []
    paid_api_calls += 1
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
    }
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
    return response.json().get("items", []) if response.status_code == 200 else []

def extract_domain(url):
    try:
        return tldextract.extract(url).registered_domain
    except:
        return ""

def get_title(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.title.string.strip() if soup.title else "No Title"
    except:
        return "Just a moment..."

def enrich_yelp(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        stars = re.search(r'(\d\.\d) star rating', text)
        reviews = re.search(r'(\d{1,3}(?:,\d{3})*|\d+) reviews?', text)
        photos = re.search(r'(\d{1,3}(?:,\d{3})*|\d+) photos?', text)
        return [
            stars.group(1) if stars else "N/A",
            reviews.group(1) if reviews else "N/A",
            photos.group(1) if photos else "N/A"
        ]
    except:
        return ["N/A", "N/A", "N/A"]

def enrich_avvo(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        rating = soup.find("span", class_="avvo-rating")
        review = soup.find("span", class_="review-count")
        return [
            rating.get_text(strip=True) if rating else "N/A",
            review.get_text(strip=True).split()[0] if review else "N/A"
        ]
    except:
        return ["N/A", "N/A"]

def should_use_google(results):
    relevant = [r for r in results if extract_domain(r['href']) not in EXCLUDED_DOMAINS]
    return len(relevant) < 3

def search_competitors(query):
    results = ddg_search(query, max_results=15)
    if should_use_google(results):
        print("🔁 Fallback to Google API")
        google_results = google_search(query)
        for item in google_results:
            results.append({
                "href": item.get("link"),
                "body": item.get("snippet", ""),
                "title": item.get("title", "")
            })
    return results

def run_profiler():
    global enriched_rows
    query = input("Enter the competitor name or domain: ").strip()
    print(f"🔍 Searching competitors for: {query}\n")

    search_results = search_competitors(query)
    seen_domains = set()

    for result in search_results:
        url = result.get("href")
        if not url: continue
        domain = extract_domain(url)
        if domain in seen_domains or domain in EXCLUDED_DOMAINS: continue
        seen_domains.add(domain)
        title = result.get("title") or get_title(url)

        avvo_rating, avvo_reviews = enrich_avvo(url) if "avvo.com" in domain else ("", "")
        yelp_stars, yelp_reviews, yelp_photos = enrich_yelp(url) if "yelp.com" in domain else ("", "", "")

        enriched_rows.append([
            title, url, domain, "TBD",
            avvo_rating, avvo_reviews,
            yelp_reviews, yelp_stars, yelp_photos
        ])

    with open("competitors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        writer.writerows(enriched_rows)

    print(f"✅ Saved {len(enriched_rows)} results to competitors.csv")
    if paid_api_calls:
        cost = round(paid_api_calls * GOOGLE_API_COST_PER_CALL, 4)
        print(f"⚠️ Google API calls used: {paid_api_calls} costing approx ${cost}")

if __name__ == "__main__":
    run_profiler()
