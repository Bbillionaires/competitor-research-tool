"""
enrichments/phase1_enrichment.py

Phase 1 enrichment adds FREE + Google-optional fields without breaking your main script.
- Adds stable headers (no missing columns)
- Adds collection_date + confidence_score
- Adds Google Places optional: latest_review_date, review_velocity, photo_frequency (delta-based)
- Adds FREE website/on-page basics: meta, headers, word count, links, schema, robots/sitemap
- Adds FREE SEO estimate using CSE if available: indexed_pages_estimate (site:)
- Adds basic ads signals + hiring signals + pricing page signal
- Adds change-tracking deltas stored locally (JSON) to compute velocities
"""

from __future__ import annotations

import os
import re
import json
import time
import math
import datetime as dt
from urllib.parse import urlparse, quote

import requests
from bs4 import BeautifulSoup

TRACKING_PATH = os.path.join(os.path.dirname(__file__), "change_tracking.json")

# -----------------------------
# Helpers
# -----------------------------

def _now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")

def _safe_get(d: dict, k: str, default=""):
    return d.get(k, default) if isinstance(d, dict) else default

def _domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def _join_list(x):
    if x is None:
        return ""
    if isinstance(x, str):
        return x.strip()
    if isinstance(x, (list, tuple, set)):
        return "; ".join([str(i).strip() for i in x if str(i).strip()])
    return str(x).strip()

def _load_tracking() -> dict:
    try:
        if os.path.exists(TRACKING_PATH):
            with open(TRACKING_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_tracking(data: dict) -> None:
    try:
        with open(TRACKING_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def _calc_velocity(prev_count: int, prev_ts: str, new_count: int, new_ts: str):
    """
    Returns per-day velocity based on delta counts and delta time.
    """
    try:
        t0 = dt.datetime.fromisoformat(prev_ts)
        t1 = dt.datetime.fromisoformat(new_ts)
        days = max((t1 - t0).total_seconds() / 86400.0, 0.0001)
        delta = new_count - prev_count
        return round(delta / days, 4)
    except Exception:
        return ""

def _http_get(url: str, timeout: int = 20) -> requests.Response | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        return requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    except Exception:
        return None

# -----------------------------
# Google Places: optional
# -----------------------------

def _google_places_textsearch(query: str, places_key: str):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": places_key}
    r = requests.get(url, params=params, timeout=20)
    return r.json()

def _google_places_details(place_id: str, places_key: str):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    # NOTE: reviews field is optional; Google may return limited reviews
    fields = "name,formatted_address,rating,user_ratings_total,photos,url,reviews"
    params = {"place_id": place_id, "key": places_key, "fields": fields}
    r = requests.get(url, params=params, timeout=20)
    return r.json()

def enrich_google_optional(row: dict) -> dict:
    """
    Uses GOOGLE_PLACES_API_KEY if present to fill:
      name, address, rating, user_ratings_total, photo_count, google_place_url,
      latest_review_date, review_velocity_per_day, photo_frequency_per_day
    """
    places_key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
    if not places_key:
        # Ensure headers exist even without key
        row.setdefault("name", "")
        row.setdefault("address", "")
        row.setdefault("rating", "")
        row.setdefault("user_ratings_total", "")
        row.setdefault("photo_count", "")
        row.setdefault("google_place_url", "")
        row.setdefault("latest_review_date", "")
        row.setdefault("review_velocity_per_day", "")
        row.setdefault("photo_frequency_per_day", "")
        return row

    url = _safe_get(row, "url", "")
    title = _safe_get(row, "title", "")
    query = _safe_get(row, "query", "")  # main script should pass this; fallback ok
    domain = _safe_get(row, "domain", _domain_from_url(url))

    business_query = " ".join([p for p in [title, query, domain] if p]).strip()

    try:
        ts = _google_places_textsearch(business_query, places_key)
        results = ts.get("results", []) if isinstance(ts, dict) else []
        if not results:
            # preserve headers
            row.setdefault("name", "")
            row.setdefault("address", "")
            row.setdefault("rating", "")
            row.setdefault("user_ratings_total", "")
            row.setdefault("photo_count", "")
            row.setdefault("google_place_url", "")
            row.setdefault("latest_review_date", "")
            row.setdefault("review_velocity_per_day", "")
            row.setdefault("photo_frequency_per_day", "")
            return row

        place_id = results[0].get("place_id", "")
        if not place_id:
            return row

        det = _google_places_details(place_id, places_key)
        place = det.get("result", {}) if isinstance(det, dict) else {}

        row["name"] = place.get("name", "") or row.get("name", "")
        row["address"] = place.get("formatted_address", "") or row.get("address", "")
        row["rating"] = place.get("rating", "") or row.get("rating", "")
        row["user_ratings_total"] = place.get("user_ratings_total", "") or row.get("user_ratings_total", "")
        row["photo_count"] = len(place.get("photos", []) or [])
        row["google_place_url"] = place.get("url", "") or row.get("google_place_url", "")

        # Latest review date (if reviews returned)
        latest_ts = ""
        reviews = place.get("reviews", []) or []
        if reviews:
            # reviews have 'time' epoch seconds
            times = [rv.get("time") for rv in reviews if isinstance(rv, dict) and isinstance(rv.get("time"), int)]
            if times:
                latest_ts = dt.datetime.fromtimestamp(max(times)).date().isoformat()
        row["latest_review_date"] = latest_ts

        # Delta-based velocities (requires prior run)
        tracking = _load_tracking()
        key = domain or _domain_from_url(url) or url
        now = _now_iso()

        # reviews velocity
        new_reviews = int(row["user_ratings_total"] or 0) if str(row.get("user_ratings_total", "")).isdigit() else 0
        prev = tracking.get(key, {})
        prev_reviews = int(prev.get("user_ratings_total") or 0)
        prev_ts = prev.get("ts", "")

        if prev_ts:
            row["review_velocity_per_day"] = _calc_velocity(prev_reviews, prev_ts, new_reviews, now)
        else:
            row["review_velocity_per_day"] = ""

        # photo frequency
        new_photos = int(row["photo_count"] or 0) if str(row.get("photo_count", "")).isdigit() else 0
        prev_photos = int(prev.get("photo_count") or 0)
        if prev_ts:
            row["photo_frequency_per_day"] = _calc_velocity(prev_photos, prev_ts, new_photos, now)
        else:
            row["photo_frequency_per_day"] = ""

        # save tracking
        tracking[key] = {
            "ts": now,
            "user_ratings_total": new_reviews,
            "photo_count": new_photos,
        }
        _save_tracking(tracking)

        return row

    except Exception:
        # preserve headers on failure
        row.setdefault("latest_review_date", "")
        row.setdefault("review_velocity_per_day", "")
        row.setdefault("photo_frequency_per_day", "")
        return row

# -----------------------------
# Free: website / on-page basics
# -----------------------------

def enrich_onpage_free(row: dict) -> dict:
    """
    Pulls basic on-page SEO + site hygiene from the URL itself.
    """
    url = _safe_get(row, "url", "")
    row.setdefault("meta_description", "")
    row.setdefault("h1", "")
    row.setdefault("word_count", "")
    row.setdefault("image_count", "")
    row.setdefault("alt_coverage_pct", "")
    row.setdefault("internal_links", "")
    row.setdefault("external_links", "")
    row.setdefault("schema_present", "")
    row.setdefault("robots_txt", "")
    row.setdefault("sitemap_xml", "")

    if not url:
        return row

    resp = _http_get(url)
    if not resp or not getattr(resp, "text", None):
        return row

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    # meta description
    md = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if md and md.get("content"):
        row["meta_description"] = md.get("content", "").strip()

    # h1
    h1 = soup.find("h1")
    if h1:
        row["h1"] = re.sub(r"\s+", " ", h1.get_text(" ", strip=True))

    # word count
    text = soup.get_text(" ", strip=True)
    words = re.findall(r"\b\w+\b", text)
    row["word_count"] = len(words)

    # images & alt coverage
    imgs = soup.find_all("img")
    row["image_count"] = len(imgs)
    if imgs:
        with_alt = sum(1 for i in imgs if (i.get("alt") or "").strip())
        row["alt_coverage_pct"] = round((with_alt / len(imgs)) * 100, 2)
    else:
        row["alt_coverage_pct"] = ""

    # links internal/external
    domain = _domain_from_url(url)
    links = [a.get("href") for a in soup.find_all("a") if a.get("href")]
    internal = 0
    external = 0
    for href in links:
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        if href.startswith("http"):
            d = _domain_from_url(href)
            if d and domain and d.endswith(domain):
                internal += 1
            else:
                external += 1
        else:
            # relative
            internal += 1
    row["internal_links"] = internal
    row["external_links"] = external

    # schema presence (very simple check)
    schema = soup.find_all("script", attrs={"type": "application/ld+json"})
    row["schema_present"] = "yes" if schema else "no"

    # robots/sitemap existence checks
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    r1 = _http_get(base + "/robots.txt")
    row["robots_txt"] = "yes" if r1 and r1.status_code == 200 else "no"
    r2 = _http_get(base + "/sitemap.xml")
    row["sitemap_xml"] = "yes" if r2 and r2.status_code == 200 else "no"

    return row

# -----------------------------
# Free-ish: indexed pages estimate using CSE (if available)
# -----------------------------

def enrich_indexed_pages_estimate(row: dict) -> dict:
    """
    Uses Google CSE JSON API if key+cx are present to estimate indexed pages via:
      q = "site:domain"
    """
    row.setdefault("indexed_pages_estimate", "")

    api_key = os.getenv("GOOGLE_CSE_API_KEY", "").strip()
    cx = os.getenv("GOOGLE_CSE_CX", "").strip() or os.getenv("GOOGLE_CSE_ID", "").strip()

    domain = _safe_get(row, "domain", "")
    if not domain:
        domain = _domain_from_url(_safe_get(row, "url", ""))

    if not api_key or not cx or not domain:
        return row

    try:
        q = f"site:{domain}"
        params = {"key": api_key, "cx": cx, "q": q}
        url = "https://www.googleapis.com/customsearch/v1?" + urlencode(params)
        r = requests.get(url, timeout=20)
        data = r.json()
        total = _safe_get(_safe_get(data, "searchInformation", {}), "totalResults", "")
        row["indexed_pages_estimate"] = total
        return row
    except Exception:
        return row

# -----------------------------
# Signals: ads, hiring, pricing (FREE)
# -----------------------------

def enrich_marketing_signals(row: dict) -> dict:
    row.setdefault("ads_signals", "")
    row.setdefault("hiring_signals", "")
    row.setdefault("pricing_page_url", "")

    url = _safe_get(row, "url", "")
    if not url:
        return row

    resp = _http_get(url)
    if not resp or not getattr(resp, "text", None):
        return row

    html = resp.text.lower()

    # ads signals
    ads_hits = []
    if "adsbygoogle" in html or "googlesyndication" in html:
        ads_hits.append("google_adsense")
    if "doubleclick.net" in html:
        ads_hits.append("doubleclick")
    if "fbq(" in html or "facebook pixel" in html:
        ads_hits.append("facebook_pixel")
    if "ttq.track" in html or "tiktok pixel" in html:
        ads_hits.append("tiktok_pixel")
    row["ads_signals"] = _join_list(ads_hits)

    # hiring signals (simple keywords)
    hiring = []
    for kw in ["careers", "jobs", "join our team", "hiring"]:
        if kw in html:
            hiring.append(kw)
    row["hiring_signals"] = _join_list(sorted(set(hiring)))

    # pricing page (try common paths)
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    for path in ["/pricing", "/prices", "/fees", "/rate", "/rates", "/cost"]:
        r = _http_get(base + path)
        if r and r.status_code == 200 and r.text and len(r.text) > 300:
            row["pricing_page_url"] = base + path
            break

    return row

# -----------------------------
# Score + collection metadata
# -----------------------------

def enrich_metadata_and_score(row: dict) -> dict:
    """
    Adds:
      collection_date
      confidence_score (0-100) based on presence of core data
    """
    row.setdefault("collection_date", dt.date.today().isoformat())
    row.setdefault("confidence_score", "")

    score = 0
    # Core website presence
    if _safe_get(row, "url", ""):
        score += 10
    if _safe_get(row, "title", ""):
        score += 10

    # Contact
    if _safe_get(row, "emails", ""):
        score += 10
    if _safe_get(row, "phones", ""):
        score += 10

    # Google
    if _safe_get(row, "name", ""):
        score += 10
    if _safe_get(row, "address", ""):
        score += 10
    if str(_safe_get(row, "rating", "")).strip():
        score += 10
    if str(_safe_get(row, "user_ratings_total", "")).strip():
        score += 10
    if str(_safe_get(row, "photo_count", "")).strip():
        score += 10

    # SEO
    if str(_safe_get(row, "indexed_pages_estimate", "")).strip():
        score += 10

    row["confidence_score"] = min(score, 100)
    return row

# -----------------------------
# Public entrypoint
# -----------------------------

def run_phase1_enrichment(row: dict) -> dict:
    """
    Call this from your main loop:
      row = run_phase1_enrichment(row)
    """
    # Ensure the query gets passed in (if missing)
    row.setdefault("query", row.get("query", ""))

    # Normalize list-ish fields to keep columns clean
    for k in ["emails", "phones", "social_facebook", "social_linkedin", "social_instagram", "social_twitter"]:
        if k in row:
            row[k] = _join_list(row[k])

    # Add metadata first
    row = enrich_metadata_and_score(row)

    # Google optional
    row = enrich_google_optional(row)

    # Free enrichments
    row = enrich_onpage_free(row)
    row = enrich_indexed_pages_estimate(row)
    row = enrich_marketing_signals(row)

    # Refresh score after enrichments
    row = enrich_metadata_and_score(row)

    return row
