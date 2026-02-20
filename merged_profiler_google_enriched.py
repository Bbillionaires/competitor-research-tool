
import csv
import time
import re
from duckduckgo_search import DDGS
from googleapiclient.discovery import build
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def search_duckduckgo(query, max_results=10):
    with DDGS() as ddgs:
        return [r for r in ddgs.text(query, max_results=max_results)]

def search_google(query):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("Google API key or CSE ID not set.")
        return None
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=GOOGLE_CSE_ID).execute()
        return res.get("items", [])
    except Exception as e:
        print(f"Google Search error: {e}")
        return []

def enrich_google_place_data(business_name):
    service = build('customsearch', 'v1', developerKey=GOOGLE_API_KEY)
    try:
        res = service.cse().list(q=business_name + " site:maps.google.com", cx=GOOGLE_CSE_ID).execute()
        for item in res.get("items", []):
            snippet = item.get("snippet", "")
            match_reviews = re.search(r'(\d+[,.]?\d*) reviews', snippet)
            match_rating = re.search(r'Rated (\d\.\d) out of 5', snippet)
            return {
                "GoogleLink": item.get("link"),
                "GoogleReviews": match_reviews.group(1) if match_reviews else "N/A",
                "GoogleStars": match_rating.group(1) if match_rating else "N/A",
            }
    except Exception as e:
        print(f"Error enriching Google data: {e}")
    return {"GoogleLink": "N/A", "GoogleReviews": "N/A", "GoogleStars": "N/A"}

def main():
    query = input("Enter a keyword or business type + location: ").strip()
    print(f"Searching DuckDuckGo for: {query}...")

    duck_results = search_duckduckgo(query)
    if not duck_results:
        print("Trying Google as fallback...")
        duck_results = search_google(query)

    data = []
    seen_domains = set()
    for result in duck_results:
        title = result.get("title")
        href = result.get("href")
        if not href or any(domain in href for domain in seen_domains):
            continue
        domain_match = re.search(r"https?://([^/]+)", href)
        domain = domain_match.group(1) if domain_match else "N/A"
        seen_domains.add(domain)

        g_data = enrich_google_place_data(title)

        data.append({
            "Title": title,
            "URL": href,
            "Domain": domain,
            "GoogleLink": g_data["GoogleLink"],
            "GoogleReviews": g_data["GoogleReviews"],
            "GoogleStars": g_data["GoogleStars"],
        })
        time.sleep(1)

    keys = data[0].keys() if data else ["Title", "URL", "Domain", "GoogleLink", "GoogleReviews", "GoogleStars"]
    with open("competitors_google_enriched.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print("Saved enriched data to competitors_google_enriched.csv")

if __name__ == "__main__":
    main()
