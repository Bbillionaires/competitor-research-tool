"""
final_competitor_profiler.py

Google-first competitor discovery using Google Custom Search JSON API (CSE),
with directory filtering + separate directory output, Google Places enrichment,
website scraping (emails/phones/social), dedupe-by-domain, column-safe CSV.

ENV (.env supported if python-dotenv installed):
  GOOGLE_CSE_API_KEY=...
  GOOGLE_CSE_CX=...          # your CSE "cx" id (looks like: 044d08ff7240e4288)
  GOOGLE_PLACES_API_KEY=...  # optional (enrichment)
"""

from __future__ import annotations

import os
import re
import csv
import time
import json
import math
import datetime as _dt
from urllib.parse import urlparse, urlencode

import requests
from bs4 import BeautifulSoup

# Optional: load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from enrichments.phase1_enrichment import run_phase1_enrichment

from enrichments.phase2_enrichment import run_phase2_enrichment

from enrichments.phase3_enrichment import run_phase3_enrichment

# -----------------------------
# Config
# -----------------------------

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  
}

GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
GOOGLE_CSE_CX = os.getenv("GOOGLE_CSE_CX") or os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_CSE_ID") or ""
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY") or ""

REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_URLS_SEC = 0.8

# Directory / aggregator domains to separate out
DIRECTORY_DOMAINS = {
    "yelp.com", "www.yelp.com",
    "justia.com", "www.justia.com",
    "superlawyers.com", "attorneys.superlawyers.com",
    "avvo.com", "www.avvo.com",
    "findlaw.com", "www.findlaw.com",
    "lawyers.com", "www.lawyers.com",
    "expertise.com", "www.expertise.com",
    "threebestrated.com", "www.threebestrated.com",
    "thumbtack.com", "www.thumbtack.com",
    "lawcrossing.com", "www.lawcrossing.com",
    "facebook.com", "www.facebook.com",
    "linkedin.com", "www.linkedin.com",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com",
    "youtube.com", "www.youtube.com",
}

DIRECTORY_KEYWORDS_IN_PATH = [
    "/lawyers/", "/attorneys/", "/directory/", "/listings/", "/best-", "/top-",
    "/search?", "/profiles/", "/people/", "/companies/",
]

JUNK_TLDS = (".gov", ".edu")


# -----------------------------
# Helpers
# -----------------------------

def safe_get(url: str, *, timeout: int = REQUEST_TIMEOUT) -> requests.Response | None:
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    except Exception:
        return None


def normalize_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip()
    if u.startswith("//"):
        u = "https:" + u
    return u


def extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def is_directory_url(url: str) -> bool:
    d = extract_domain(url)
    if not d:
        return True
    if d.endswith(JUNK_TLDS):
        return True
    if d in DIRECTORY_DOMAINS:
        return True
    path = (urlparse(url).path or "").lower()
    q = (urlparse(url).query or "").lower()
    for kw in DIRECTORY_KEYWORDS_IN_PATH:
        if kw in path or kw in q:
            return True
    return False


def unique_keep_order(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for x in items:
        x = (x or "").strip()
        if not x:
            continue
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


# -----------------------------
# Google CSE Search (Google-first)
# -----------------------------

def google_cse_search(query: str, max_results: int = 20) -> list[str]:
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX:
        print("⚠️ Missing GOOGLE_CSE_API_KEY or GOOGLE_CSE_CX. Set them in .env (recommended).")
        return []

    urls: list[str] = []
    start = 1  # 1-based
    # CSE allows num <= 10
    while len(urls) < max_results:
        num = min(10, max_results - len(urls))
        params = {
            "key": GOOGLE_CSE_API_KEY,
            "cx": GOOGLE_CSE_CX,
            "q": query,
            "num": num,
            "start": start,
        }
        endpoint = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)

        resp = safe_get(endpoint, timeout=REQUEST_TIMEOUT)
        if not resp:
            break

        if resp.status_code != 200:
            # Print full error once (helps debugging 403/400)
            try:
                print("Google CSE Error:", resp.status_code, resp.text[:500])
            except Exception:
                print("Google CSE Error:", resp.status_code)
            break

        data = {}
        try:
            data = resp.json()
        except Exception:
            break

        items = data.get("items", []) or []
        if not items:
            break

        for it in items:
            link = it.get("link") or ""
            link = normalize_url(link)
            if link:
                urls.append(link)

        start += 10
        if start > 91:  # CSE pagination practical limit
            break

    return unique_keep_order(urls)


# -----------------------------
# Website scraping (column-safe)
# -----------------------------

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(
    r"(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*\d{3}\s*\)|\d{3})\s*(?:[.-]\s*)?)\d{3}\s*(?:[.-]\s*)?\d{4}"
)

def scrape_website(url: str) -> dict:
    out = {
        "emails": [],
        "phones": [],
        "logo_url": "",
        "social_facebook": [],
        "social_linkedin": [],
        "social_instagram": [],
        "social_twitter": [],
        "contact_page": "",
        "booking_links": [],
    }

    resp = safe_get(url, timeout=REQUEST_TIMEOUT)
    if not resp or resp.status_code >= 400:
        return out

    html = resp.text or ""
    soup = BeautifulSoup(html, "html.parser")

    # Title (fallback)
    # (kept separate via get_title)

    # Emails / phones
    emails = EMAIL_RE.findall(html)
    phones = PHONE_RE.findall(html)
    out["emails"] = unique_keep_order(emails)
    out["phones"] = unique_keep_order([p.strip() for p in phones])

    # Logo: try schema/og first then common header img
    og = soup.find("meta", attrs={"property": "og:logo"}) or soup.find("meta", attrs={"property": "og:image"})
    if og and og.get("content"):
        out["logo_url"] = normalize_url(og.get("content"))

    if not out["logo_url"]:
        # Try <img> with logo in alt/class/id
        for img in soup.find_all("img"):
            alt = (img.get("alt") or "").lower()
            cls = " ".join(img.get("class") or []).lower()
            iid = (img.get("id") or "").lower()
            if "logo" in alt or "logo" in cls or "logo" in iid:
                src = img.get("src") or ""
                if src:
                    out["logo_url"] = normalize_url(src)
                    break

    # Social links + booking links + contact page
    for a in soup.find_all("a", href=True):
        href = normalize_url(a.get("href") or "")
        if not href:
            continue
        low = href.lower()

        if "facebook.com" in low:
            out["social_facebook"].append(href)
        elif "linkedin.com" in low:
            out["social_linkedin"].append(href)
        elif "instagram.com" in low:
            out["social_instagram"].append(href)
        elif "twitter.com" in low or "x.com" in low:
            out["social_twitter"].append(href)

        if any(k in low for k in ["book", "schedule", "appointment", "calendly.com"]):
            out["booking_links"].append(href)

        if "contact" in low and not out["contact_page"] and extract_domain(href) == extract_domain(url):
            out["contact_page"] = href

    # De-dupe lists
    out["social_facebook"] = unique_keep_order(out["social_facebook"])
    out["social_linkedin"] = unique_keep_order(out["social_linkedin"])
    out["social_instagram"] = unique_keep_order(out["social_instagram"])
    out["social_twitter"] = unique_keep_order(out["social_twitter"])
    out["booking_links"] = unique_keep_order(out["booking_links"])

    return out


def get_title(url: str) -> str:
    resp = safe_get(url, timeout=REQUEST_TIMEOUT)
    if not resp or resp.status_code >= 400:
        return ""
    soup = BeautifulSoup(resp.text or "", "html.parser")
    t = soup.find("title")
    return (t.get_text(strip=True) if t else "")[:250]


# -----------------------------
# Google Places enrichment (optional)
# -----------------------------

def get_place_details(query: str) -> dict:
    """
    Uses Places Text Search + Details to fetch rating/reviews/photos/maps URL.
    Returns empty dict if key missing or no match.
    """
    if not GOOGLE_PLACES_API_KEY:
        return {}

    # Text search
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_PLACES_API_KEY}
    resp = safe_get(search_url + "?" + urlencode(params), timeout=REQUEST_TIMEOUT)
    if not resp or resp.status_code != 200:
        return {}

    data = {}
    try:
        data = resp.json()
    except Exception:
        return {}

    results = data.get("results") or []
    if not results:
        return {}

    first = results[0]
    place_id = first.get("place_id") or ""
    if not place_id:
        return {}

    # Details
    fields = "name,rating,user_ratings_total,formatted_address,photos,url,website"
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params2 = {"place_id": place_id, "key": GOOGLE_PLACES_API_KEY, "fields": fields}
    resp2 = safe_get(details_url + "?" + urlencode(params2), timeout=REQUEST_TIMEOUT)
    if not resp2 or resp2.status_code != 200:
        return {}

    d2 = {}
    try:
        d2 = resp2.json()
    except Exception:
        return {}

    place = d2.get("result") or {}
    photos = place.get("photos") or []

    return {
        "g_name": place.get("name", ""),
        "g_address": place.get("formatted_address", ""),
        "g_rating": place.get("rating", ""),
        "g_user_ratings_total": place.get("user_ratings_total", ""),
        "g_photo_count": len(photos),
        "g_google_place_url": place.get("url", ""),
        "g_website": place.get("website", ""),
        "g_place_id": place_id,
    }


# -----------------------------
# (Free) traffic estimation fallback
# -----------------------------

def estimate_traffic(domain: str) -> str:
    """
    Free fallback (best-effort). Many free sources block scraping.
    Returns "N/A" if not obtainable.
    """
    if not domain:
        return "N/A"
    # Placeholder: keep stable and fast for now
    return "N/A"


# -----------------------------
# Scoring / tiering
# -----------------------------

def compute_score(row: dict) -> int:
    score = 0

    # Google rating / reviews (if available)
    try:
        r = float(row.get("g_rating") or 0)
        score += int(min(5.0, r) * 10)  # up to 50
    except Exception:
        pass

    try:
        reviews = int(row.get("g_user_ratings_total") or 0)
        score += int(min(50, math.log10(reviews + 1) * 20))  # up to ~50
    except Exception:
        pass

    # Contact completeness
    if row.get("emails"):
        score += 10
    if row.get("phones"):
        score += 10

    # Social presence
    if row.get("social_facebook"):
        score += 5
    if row.get("social_linkedin"):
        score += 5

    return max(0, min(100, score))


def tier_from_score(score: int) -> str:
    if score >= 80:
        return "Tier 1"
    if score >= 55:
        return "Tier 2"
    return "Tier 3"


# -----------------------------
# CSV output (column-safe)
# -----------------------------

OUTPUT_HEADERS = [
    # Core
    "url", "domain", "title", "traffic_estimate",
    # Google Places
    "g_name", "g_address", "g_rating", "g_user_ratings_total", "g_photo_count", "g_google_place_url", "g_place_id", "g_website",
    # Website
    "emails", "phones", "logo_url", "contact_page", "booking_links",
    # Social
    "social_facebook", "social_linkedin", "social_instagram", "social_twitter",
    # Scoring
    "competitor_score", "tier",
    # Evidence
    "source", "collected_at",
]


def row_to_csv_safe(row: dict) -> dict:
    """
    Ensures each field stays in the correct column (no leaking).
    """
    safe = {}
    for h in OUTPUT_HEADERS:
        safe[h] = row.get(h, "")

    # Force string columns
    for k in ["emails", "phones", "booking_links", "social_facebook", "social_linkedin", "social_instagram", "social_twitter"]:
        v = safe.get(k, "")
        if isinstance(v, list):
            v = " | ".join(unique_keep_order([str(x) for x in v]))
        safe[k] = v

    return safe


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    query = input("Enter keyword (e.g. injury attorney Ventura CA): ").strip()
    if not query:
        print("⚠️ Empty query.")
        return

    max_results_in = input("Max # of results (default 20): ").strip()
    max_results = 20
    if max_results_in:
        try:
            max_results = max(5, min(50, int(max_results_in)))
        except Exception:
            max_results = 20

    print("🔍 Google search first...")
    urls = google_cse_search(query, max_results=max_results)
    print(f"🧪 GOOGLE URL COUNT: {len(urls)}")

    if not urls:
        print("⚠️ No URLs returned. Check GOOGLE_CSE_API_KEY and GOOGLE_CSE_CX.")
        return

    # Separate directories vs competitors
    competitor_urls = []
    directory_urls = []

    for u in urls:
        if is_directory_url(u):
            directory_urls.append(u)
        else:
            competitor_urls.append(u)

    competitor_urls = unique_keep_order(competitor_urls)
    directory_urls = unique_keep_order(directory_urls)

    # Save directories file (so you can see what directories show up)
    if directory_urls:
        with open("directories_filtered.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["query", "url", "domain"])
            w.writeheader()
            for u in directory_urls:
                w.writerow({"query": query, "url": u, "domain": extract_domain(u)})
        print(f"📁 Saved {len(directory_urls)} directories to directories_filtered.csv")

    # Dedupe by domain for competitors
    rows = []
    seen_domains = set()

    for url in competitor_urls:
        domain = extract_domain(url)
        if not domain:
            continue
        if domain in seen_domains:
            continue
        seen_domains.add(domain)

        if domain.endswith(JUNK_TLDS):
            continue

        title = get_title(url)
        web = scrape_website(url)

        # Google Places enrichment query: use title + user query (works well in practice)
        place_query = f"{title} {query}".strip()
        g = get_place_details(place_query)

        traffic = estimate_traffic(domain)

        row = {
            "url": url,
            "domain": domain,
            "title": title,
            "traffic_estimate": traffic,

            # Google Places
            "g_name": g.get("g_name", ""),
            "g_address": g.get("g_address", ""),
            "g_rating": g.get("g_rating", ""),
            "g_user_ratings_total": g.get("g_user_ratings_total", ""),
            "g_photo_count": g.get("g_photo_count", ""),
            "g_google_place_url": g.get("g_google_place_url", ""),
            "g_place_id": g.get("g_place_id", ""),
            "g_website": g.get("g_website", ""),

            # Website (force correct columns)
            "emails": " | ".join(web.get("emails", [])),
            "phones": " | ".join(web.get("phones", [])),
            "logo_url": web.get("logo_url", ""),
            "contact_page": web.get("contact_page", ""),
            "booking_links": " | ".join(web.get("booking_links", [])),

            # Social
            "social_facebook": " | ".join(web.get("social_facebook", [])),
            "social_linkedin": " | ".join(web.get("social_linkedin", [])),
            "social_instagram": " | ".join(web.get("social_instagram", [])),
            "social_twitter": " | ".join(web.get("social_twitter", [])),

            # Evidence
            "source": "google_cse",
            "collected_at": _dt.datetime.utcnow().isoformat() + "Z",
        }

        score = compute_score(row)
        row["competitor_score"] = score
        row["tier"] = tier_from_score(score)
        row = run_phase1_enrichment(row)
        row = run_phase2_enrichment(row)
        row = run_phase3_enrichment(row)
        rows.append(row)
        time.sleep(SLEEP_BETWEEN_URLS_SEC)

    if not rows:
        print("⚠️ No valid competitors found.")
        return

    # Write output with strict headers + QUOTE_ALL to prevent leaking
    with open("competitors_final_profile.csv", "w", newline="", encoding="utf-8") as f:
    
           # -------- FORCE ALL HEADERS (ALL PHASES) --------
           ALL_HEADERS = set()
           for r in rows:
               ALL_HEADERS.update(r.keys())

           headers = sorted(ALL_HEADERS)

           writer = csv.DictWriter(f, fieldnames=headers)
           writer.writeheader()
        
           for r in rows:
              writer.writerow(row_to_csv_safe(r))

           print(f"✅ Saved {len(rows)} competitors to competitors_final_profile.csv")
           print("Tip: Open directories_filtered.csv to see which directories were filtered out.")


if __name__ == "__main__":
    main()
