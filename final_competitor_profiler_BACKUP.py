import os
import csv
import time
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ddgs import DDGS
from googleapiclient.discovery import build

# =========================
# ENV SETUP
# =========================
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY") or os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY") or GOOGLE_API_KEY

# =========================
# BLOCKED DOMAINS (FINAL OUTPUT ONLY)
# =========================
BLOCKED_DOMAINS = [
    "justia.com",
    "avvo.com",
    "yelp.com",
    "findlaw.com",
    "lawyers.com",
    "superlawyers.com",
    "threebestrated.com",
    "thumbtack.com",
    "expertise.com",
    "lawinfo.com",
    "legalmatch",
    "cornell.edu",
    ".gov",
    ".edu",
]

# =========================
# HELPERS
# =========================
def extract_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""

def should_output(domain):
    return not any(bad in domain for bad in BLOCKED_DOMAINS)

# =========================
# GOOGLE SEARCH (PRIMARY)
# =========================
def google_search(query, max_results):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    results = []
    start = 1

    while len(results) < max_results:
        res = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            start=start,
            num=min(10, max_results - len(results))
        ).execute()

        for item in res.get("items", []):
            results.append(item["link"])

        if "nextPage" not in res.get("queries", {}):
            break

        start += 10

    return results

# =========================
# DUCKDUCKGO FALLBACK
# =========================
def duckduckgo_search(query, max_results):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query):
            if "href" in r:
                results.append(r["href"])
            if len(results) >= max_results:
                break
    return results

# =========================
# GOOGLE PLACES ENRICHMENT
# =========================
def get_place_details(business_query):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": business_query,
        "key": GOOGLE_PLACES_API_KEY
    }

    r = requests.get(search_url, params=params).json()
    if not r.get("results"):
        return {}

    place = r["results"][0]
    place_id = place.get("place_id")

    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    details_params = {
        "place_id": place_id,
        "fields": "name,formatted_address,rating,user_ratings_total,photos,url",
        "key": GOOGLE_PLACES_API_KEY
    }

    d = requests.get(details_url, params=details_params).json()
    result = d.get("result", {})

    return {
        "name": result.get("name", ""),
        "address": result.get("formatted_address", ""),
        "rating": result.get("rating", ""),
        "user_ratings_total": result.get("user_ratings_total", ""),
        "photo_count": len(result.get("photos", [])),
        "google_place_url": result.get("url", "")
    }

# =========================
# TITLE FETCH
# =========================
def get_title(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.title.text.strip() if soup.title else ""
    except:
        return ""

# =========================
# MAIN
# =========================
def main():
    query = input("Enter keyword (e.g. injury attorney Ventura CA): ").strip()
    max_results = int(input("Max # of results (default 20): ") or 20)

    print("🔍 Google search first...")
    urls = []

    try:
        urls = google_search(query, max_results)
    except Exception as e:
        print("Google error:", e)

    if not urls:
        print("⚠️ Google empty → DuckDuckGo fallback")
        urls = duckduckgo_search(query, max_results)

    if not urls:
        print("❌ No results at all.")
        return

    rows = []

    for url in set(urls):
        domain = extract_domain(url)
        title = get_title(url)

        place = get_place_details(f"{domain} {query}")

        row = {
            "url": url,
            "domain": domain,
            "title": title,
            "traffic_estimate": "N/A",
            "name": place.get("name", ""),
            "address": place.get("address", ""),
            "rating": place.get("rating", ""),
            "user_ratings_total": place.get("user_ratings_total", ""),
            "photo_count": place.get("photo_count", ""),
            "google_place_url": place.get("google_place_url", "")
        }

        # ✅ FINAL FILTER ONLY
        if should_output(domain):
            rows.append(row)

        time.sleep(1)

    if not rows:
        print("⚠️ No valid competitors found.")
        return

    with open("competitors_final_profile.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("✅ Saved competitors_final_profile.csv")

# =========================
if __name__ == "__main__":
    main()