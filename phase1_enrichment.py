
"""
enrichments/phase1_enrichment.py

PHASE 1 ENRICHMENT (STABLE, FREE-FIRST, GOOGLE-OPTIONAL)

This module safely enriches a single competitor row WITHOUT:
- breaking CSV headers
- leaking data into wrong columns
- introducing duplicates
- requiring paid APIs (Google is optional)

FEATURES INCLUDED
-----------------
GOOGLE (optional if keys exist)
- name
- address
- rating
- user_ratings_total
- photo_count
- google_place_url
- latest_review_date
- review_velocity_per_day (delta-based)
- photo_frequency_per_day (delta-based)

WEBSITE / ON-PAGE (FREE)
- meta_description
- h1
- word_count
- image_count
- alt_coverage_pct
- internal_links
- external_links
- schema_present
- robots_txt
- sitemap_xml

SEO (FREE)
- indexed_pages_estimate (via Google CSE if available)

MARKETING SIGNALS (FREE)
- ads_signals
- hiring_signals
- pricing_page_url

METADATA
- collection_date
- confidence_score (0–100)

SAFE TO CALL:
    row = run_phase1_enrichment(row)
"""

from __future__ import annotations

import os
import re
import json
import datetime as dt
from urllib.parse import urlparse, urlencode

import requests
from bs4 import BeautifulSoup

TRACKING_PATH = os.path.join(os.path.dirname(__file__), "change_tracking.json")

# -----------------
# Helpers
# -----------------

def _now_iso():
    return dt.datetime.now().isoformat(timespec="seconds")

def _safe_get(d, k, default=""):
    return d.get(k, default) if isinstance(d, dict) else default

def _domain_from_url(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def _join_list(x):
    if not x:
        return ""
    if isinstance(x, str):
        return x.strip()
    if isinstance(x, (list, set, tuple)):
        return "; ".join(sorted({str(i).strip() for i in x if str(i).strip()}))
    return str(x).strip()

def _http_get(url, timeout=20):
    try:
        return requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            allow_redirects=True,
        )
    except Exception:
        return None

def _load_tracking():
    if os.path.exists(TRACKING_PATH):
        try:
            with open(TRACKING_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_tracking(data):
    try:
        with open(TRACKING_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def _calc_velocity(prev, prev_ts, now_val, now_ts):
    try:
        t0 = dt.datetime.fromisoformat(prev_ts)
        t1 = dt.datetime.fromisoformat(now_ts)
        days = max((t1 - t0).total_seconds() / 86400, 0.0001)
        return round((now_val - prev) / days, 4)
    except Exception:
        return ""

# -----------------
# GOOGLE PLACES (OPTIONAL)
# -----------------

def enrich_google_optional(row):
    key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()

    for h in [
        "name","address","rating","user_ratings_total",
        "photo_count","google_place_url",
        "latest_review_date","review_velocity_per_day","photo_frequency_per_day"
    ]:
        row.setdefault(h, "")

    if not key:
        return row

    query = " ".join(filter(None, [
        row.get("title",""),
        row.get("query",""),
        row.get("domain","")
    ]))

    try:
        ts = requests.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": query, "key": key},
            timeout=20,
        ).json()

        results = ts.get("results", [])
        if not results:
            return row

        place_id = results[0].get("place_id")
        if not place_id:
            return row

        details = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "key": key,
                "fields": "name,formatted_address,rating,user_ratings_total,photos,url,reviews",
            },
            timeout=20,
        ).json()

        place = details.get("result", {})

        row["name"] = place.get("name","")
        row["address"] = place.get("formatted_address","")
        row["rating"] = place.get("rating","")
        row["user_ratings_total"] = place.get("user_ratings_total","")
        row["photo_count"] = len(place.get("photos",[]) or [])
        row["google_place_url"] = place.get("url","")

        reviews = place.get("reviews",[]) or []
        if reviews:
            times = [r.get("time") for r in reviews if isinstance(r.get("time"),int)]
            if times:
                row["latest_review_date"] = dt.datetime.fromtimestamp(max(times)).date().isoformat()

        tracking = _load_tracking()
        key_id = row.get("domain") or row.get("url")
        now = _now_iso()

        prev = tracking.get(key_id,{})
        if prev:
            row["review_velocity_per_day"] = _calc_velocity(
                int(prev.get("user_ratings_total",0)),
                prev.get("ts",""),
                int(row.get("user_ratings_total") or 0),
                now,
            )
            row["photo_frequency_per_day"] = _calc_velocity(
                int(prev.get("photo_count",0)),
                prev.get("ts",""),
                int(row.get("photo_count") or 0),
                now,
            )

        tracking[key_id] = {
            "ts": now,
            "user_ratings_total": row.get("user_ratings_total",0),
            "photo_count": row.get("photo_count",0),
        }
        _save_tracking(tracking)

    except Exception:
        pass

    return row

# -----------------
# ON-PAGE / SEO FREE
# -----------------

def enrich_onpage_free(row):
    url = row.get("url","")
    for h in [
        "meta_description","h1","word_count","image_count","alt_coverage_pct",
        "internal_links","external_links","schema_present","robots_txt","sitemap_xml"
    ]:
        row.setdefault(h,"")

    if not url:
        return row

    r = _http_get(url)
    if not r or not r.text:
        return row

    soup = BeautifulSoup(r.text,"html.parser")

    md = soup.find("meta",attrs={"name":"description"})
    if md and md.get("content"):
        row["meta_description"] = md.get("content","").strip()

    h1 = soup.find("h1")
    if h1:
        row["h1"] = h1.get_text(" ",strip=True)

    text = soup.get_text(" ",strip=True)
    row["word_count"] = len(re.findall(r"\w+",text))

    imgs = soup.find_all("img")
    row["image_count"] = len(imgs)
    if imgs:
        with_alt = sum(1 for i in imgs if i.get("alt"))
        row["alt_coverage_pct"] = round(with_alt/len(imgs)*100,2)

    domain = _domain_from_url(url)
    links = [a.get("href") for a in soup.find_all("a") if a.get("href")]
    for l in links:
        if l.startswith("http"):
            if domain in l:
                row["internal_links"] = int(row["internal_links"] or 0)+1
            else:
                row["external_links"] = int(row["external_links"] or 0)+1

    row["schema_present"] = "yes" if soup.find("script",{"type":"application/ld+json"}) else "no"

    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    row["robots_txt"] = "yes" if _http_get(base+"/robots.txt") else "no"
    row["sitemap_xml"] = "yes" if _http_get(base+"/sitemap.xml") else "no"

    return row

# -----------------
# INDEXED PAGES (CSE)
# -----------------

def enrich_indexed_pages_estimate(row):
    row.setdefault("indexed_pages_estimate","")
    api = os.getenv("GOOGLE_CSE_API_KEY","").strip()
    cx = os.getenv("GOOGLE_CSE_CX","").strip()
    domain = row.get("domain","")

    if not api or not cx or not domain:
        return row

    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key":api,"cx":cx,"q":f"site:{domain}"},
            timeout=20
        ).json()
        row["indexed_pages_estimate"] = r.get("searchInformation",{}).get("totalResults","")
    except Exception:
        pass

    return row

# -----------------
# MARKETING SIGNALS
# -----------------

def enrich_marketing_signals(row):
    row.setdefault("ads_signals","")
    row.setdefault("hiring_signals","")
    row.setdefault("pricing_page_url","")

    html = ""
    r = _http_get(row.get("url",""))
    if r and r.text:
        html = r.text.lower()

    ads = []
    if "adsbygoogle" in html: ads.append("google_adsense")
    if "doubleclick" in html: ads.append("doubleclick")
    if "facebook pixel" in html: ads.append("facebook_pixel")
    row["ads_signals"] = _join_list(ads)

    hiring = [k for k in ["careers","jobs","hiring"] if k in html]
    row["hiring_signals"] = _join_list(hiring)

    base = f"{urlparse(row.get('url','')).scheme}://{urlparse(row.get('url','')).netloc}"
    for p in ["/pricing","/fees","/rates"]:
        if _http_get(base+p):
            row["pricing_page_url"] = base+p
            break

    return row

# -----------------
# METADATA + SCORE
# -----------------

def enrich_metadata_and_score(row):
    row.setdefault("collection_date",dt.date.today().isoformat())
    score = 0
    for k in ["url","title","emails","phones","name","address","rating","photo_count"]:
        if str(row.get(k,"")).strip():
            score += 10
    row["confidence_score"] = min(score,100)
    return row

# -----------------
# PUBLIC ENTRY
# -----------------

def run_phase1_enrichment(row):
    row = enrich_metadata_and_score(row)
    row = enrich_google_optional(row)
    row = enrich_onpage_free(row)
    row = enrich_indexed_pages_estimate(row)
    row = enrich_marketing_signals(row)
    row = enrich_metadata_and_score(row)
    return row
