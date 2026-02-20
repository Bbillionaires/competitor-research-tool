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
from capabilities_manifest import CAPABILITIES
from scrapers.website_scraper import scrape_website
print("✅ Capabilities loaded:", CAPABILITIES.keys())

# ============================
# FIXED CSV SCHEMA (DO NOT MOVE)
# ============================

CSV_HEADERS = [
    # Core
    "url",
    "domain",
    "title",
    "traffic_estimate",

    # Google / Maps
    "name",
    "address",
    "rating",
    "user_ratings_total",
    "photo_count",
    "google_place_url",

    # Website intelligence
    "emails",
    "phones",
    "logo_url",
    "cms",
    "tracking_tools",
    "chat_widgets",
    "contact_page",
    "booking_links",
    "form_count",

    # Social
    "social_facebook",
    "social_linkedin",
    "social_instagram",
    "social_twitter"
]


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

def should_output(domain: str) -> bool:
    BLOCKED_DOMAINS = {
        "yelp.com",
        "justia.com",
        "avvo.com",
        "superlawyers.com",
        "findlaw.com",
        "lawyers.com",
        "threebestrated.com",
        "expertise.com",
        "facebook.com",
        "linkedin.com",
        "twitter.com",
        "instagram.com",
        "youtube.com",
        "wikipedia.org",
        "bbb.org",
        "yellowpages.com",
        "mapquest.com",
        "court",
        "courts.ca.gov"
    }

    domain = domain.lower().strip()

    return not any(
        domain == blocked or domain.endswith("." + blocked)
        for blocked in BLOCKED_DOMAINS
    )



# =========================
# GOOGLE SEARCH (PRIMARY)
# =========================
def google_search(query, max_results=20):
    service = build(
        "customsearch",
        "v1",
        developerKey=os.getenv("GOOGLE_CSE_API_KEY")
    )

    cx = os.getenv("GOOGLE_CSE_ID")
    if not cx:
        raise RuntimeError("GOOGLE_CSE_ID is not set")

    results = []
    start = 1

    while len(results) < max_results:
        res = service.cse().list(
            q=query,
            cx=cx,
            start=start,
            num=min(10, max_results - len(results))
        ).execute()

        items = res.get("items", [])
        if not items:
            break

        for item in items:
            link = item.get("link")
            if link:
                results.append(link)

        # 🔑 Pagination check
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

def normalize_contact_fields(row):
    # Force strings so CSV never shifts columns
    emails = row.get("emails", "")
    phones = row.get("phones", "")

    # If some scraper returned lists, join them safely
    if isinstance(emails, list):
        emails = " | ".join(sorted(set([e.strip() for e in emails if e and str(e).strip()])))
    if isinstance(phones, list):
        phones = " | ".join(sorted(set([p.strip() for p in phones if p and str(p).strip()])))

    # If already string (like your current code), just clean it
    if isinstance(emails, str):
        emails = " | ".join(sorted(set([e.strip() for e in emails.replace(";", "|").split("|") if e.strip()])))
    if isinstance(phones, str):
        phones = " | ".join(sorted(set([p.strip() for p in phones.replace(";", "|").split("|") if p.strip()])))

    row["emails"] = emails
    row["phones"] = phones
    return row

def normalize_contact_fields(row):
    """
    Ensures contact data stays in correct columns
    and removes cross-contamination.
    """

    def clean_list(value):
        if not value:
            return ""
        if isinstance(value, list):
            return "; ".join(sorted(set(v.strip() for v in value if v.strip())))
        return value

    # Normalize emails
    emails = row.get("emails", "")
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", emails)
    row["emails"] = clean_list(emails)

    # Normalize phones (digits only, formatted)
    phones = re.findall(r"\+?\d[\d\s().-]{7,}\d", row.get("phones", ""))
    phones = [re.sub(r"[^\d+]", "", p) for p in phones]
    row["phones"] = clean_list(phones)

    # Normalize social links
    for platform in ["facebook", "linkedin", "instagram", "twitter"]:
        val = row.get(platform, "")
        links = re.findall(r"https?://[^\s;]+", val)
        row[platform] = clean_list(links)

    return row


# =========================
# MAIN
# =========================
def main():
    print("\n[Starting] Competitor Profiler...\n")

    query = input("Enter keyword (e.g. injury attorney Ventura CA): ").strip()
    max_results = input("Max # of results (default 20): ").strip()
    max_results = int(max_results) if max_results.isdigit() else 20

    # ---- SEARCH ----
    print("🔍 Google search first...")
    urls = google_search(query, max_results=max_results)

    print("🧪 GOOGLE URL COUNT:", len(urls))

    if not urls:
        print("⚠️ No valid competitors found.")
        return

    rows = []
    seen_domains = set()

    for url in urls:
        domain = extract_domain(url)

    # ✅ HARD STOP: skip duplicate domains
        if not domain or domain in seen_domains:
            continue

    seen_domains.add(domain)

    # ✅ Skip junk / directories / non-business
    if any(bad in domain for bad in [
        "yelp.com",
        "justia.com",
        "avvo.com",
        "superlawyers.com",
        "lawyers.",
        "findlaw.com",
        "expertise.com",
        "thumbtack.com",
        "facebook.com",
        "linkedin.com",
        "youtube.com",
        ".gov",
        ".edu"
    ]):
        continue

    print("✅ ACCEPTED DOMAIN:", domain)

    # ---- ONLY NOW DO WORK ----
    title = get_title(url)
    website_data = scrape_website(url)

    business_query = f"{title} {query}"
    place = get_place_details(business_query)

    row = {
        "url": url,
        "domain": domain,
        "title": title,
        "traffic_estimate": "N/A",

        # Google Places
        "name": place.get("name", "") if place else "",
        "address": place.get("address", "") if place else "",
        "rating": place.get("rating", "") if place else "",
        "user_ratings_total": place.get("user_ratings_total", "") if place else "",
        "photo_count": place.get("photo_count", "") if place else "",
        "google_place_url": place.get("google_place_url", "") if place else "",

        # Contact
        "emails": "; ".join(set(website_data.get("emails", []))),
        "phones": "; ".join(set(website_data.get("phones", []))),

        # Website
        "logo_url": website_data.get("logo_url", ""),
        "cms": website_data.get("cms", ""),
        "tracking_tools": "; ".join(set(website_data.get("tracking_tools", []))),
        "chat_widgets": "; ".join(set(website_data.get("chat_widgets", []))),
        "contact_page": website_data.get("contact_page", ""),
        "booking_links": "; ".join(set(website_data.get("booking_links", []))),
        "form_count": int(website_data.get("form_count", 0)),

        # Social (STRICT COLUMNS — no leakage)
        "social_facebook": "; ".join(set(website_data.get("social_links", {}).get("facebook", []))),
        "social_linkedin": "; ".join(set(website_data.get("social_links", {}).get("linkedin", []))),
        "social_instagram": "; ".join(set(website_data.get("social_links", {}).get("instagram", []))),
        "social_twitter": "; ".join(set(website_data.get("social_links", {}).get("twitter", []))),
    }

    row = normalize_contact_fields(row)
    rows.append(row)

    time.sleep(1)



    print("FINAL ROW COUNT:", len(rows))

    if not rows:
        print("⚠️ No rows collected.")
        return

    headers = list(rows[0].keys())

    with open("competitors_final_profile.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"✅ Saved {len(rows)} competitors to competitors_final_profile.csv")



if __name__ == "__main__":
    main()