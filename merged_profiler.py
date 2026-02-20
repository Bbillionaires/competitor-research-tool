from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import csv
import tldextract
import pandas as pd
import re
from urllib.parse import urlparse
import os

# Optional: set your Google Places API key as env variable or paste directly
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAsX5EHoJ4Vfis4z20zWxNB4r7yq4Kihfc")

# Extract main domain
def extract_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

# Get list of related sites from DuckDuckGo
def get_related_sites(query):
    print(f"?? Searching competitors for: {query}")
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(f"site:similarsites.com {query}", max_results=5):
            if 'href' in r and 'similarsites.com' in r['href']:
                results.append(r['href'])

        if not results or any("porno" in url or "rule34" in url for url in results):
            print("?? Irrelevant results found. Using backup keyword-based search.")
            backup_keywords = [
                f"{query} immigration attorney ventura site:.com",
                f"{query} personal injury lawyer ventura site:.com",
                "top rated attorneys ventura ca site:.com",
                "ventura immigration law firm site:.com",
                "ventura ca personal injury attorney site:.com"
            ]
            for kw in backup_keywords:
                for r in ddgs.text(kw, max_results=5):
                    if 'href' in r:
                        results.append(r['href'])

    return list(set(results))  # Deduplicate

# Scrape title tag of a page
def fetch_page_title(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.title.string.strip() if soup.title else "No Title"
    except Exception as e:
        return f"Error fetching title: {e}"

# Scrape Avvo rating and reviews
def scrape_avvo(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        rating = soup.find("span", class_="avvo-rating-number")
        reviews = soup.find("span", class_="review-count")
        return {
            "AvvoRating": rating.text.strip() if rating else "N/A",
            "AvvoReviews": reviews.text.strip() if reviews else "0"
        }
    except:
        return {"AvvoRating": "Error", "AvvoReviews": "0"}

# Scrape Yelp reviews, rating, and photos
def scrape_yelp(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        review_count = soup.select_one("span.reviewCount__09f24__tnBk4")
        stars = soup.select_one("div.i-stars__09f24__foihJ")
        photo_count = soup.select_one("span.photoCount__09f24__EfxuW")

        return {
            "YelpReviews": review_count.text.strip() if review_count else "N/A",
            "YelpStars": stars.get("aria-label") if stars else "N/A",
            "YelpPhotos": photo_count.text.strip() if photo_count else "N/A",
        }
    except:
        return {"YelpReviews": "Error", "YelpStars": "Error", "YelpPhotos": "Error"}

# Enrich using Google Places API
def enrich_google_places(domain):
    try:
        search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json"

        params = {
            "input": domain,
            "inputtype": "textquery",
            "fields": "place_id",
            "key": GOOGLE_API_KEY
        }

        res = requests.get(search_url, params=params).json()
        if "candidates" not in res or not res["candidates"]:
            return {}

        place_id = res["candidates"][0]["place_id"]
        res = requests.get(details_url, params={
            "place_id": place_id,
            "fields": "rating,user_ratings_total,photos",
            "key": GOOGLE_API_KEY
        }).json()

        result = res.get("result", {})
        return {
            "GoogleRating": result.get("rating", "N/A"),
            "GoogleReviews": result.get("user_ratings_total", "N/A"),
            "GooglePhotos": len(result.get("photos", []))
        }
    except:
        return {}

# Full enrichment process
def enrich_sites(sites):
    enriched = []
    seen = set()

    for url in sites:
        domain = extract_domain(url)
        if domain in seen:
            continue
        seen.add(domain)

        title = fetch_page_title(url)

        # Source-specific scrapes
        avvo_data = scrape_avvo(url) if "avvo.com" in url else {}
        yelp_data = scrape_yelp(url) if "yelp.com" in url else {}
        google_data = enrich_google_places(domain)

        enriched.append({
            "Title": title,
            "URL": url,
            "Domain": domain,
            "EstimatedTraffic": "TBD",  # Placeholder
            **avvo_data,
            **yelp_data,
            **google_data
        })

    return enriched

# Save as CSV
def save_to_csv(data, filename="competitors.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"\n? Saved to {filename}")

# Run
if __name__ == "__main__":
    query = input("Enter the competitor name or domain: ")
    urls = get_related_sites(query)
    data = enrich_sites(urls)
    save_to_csv(data)
