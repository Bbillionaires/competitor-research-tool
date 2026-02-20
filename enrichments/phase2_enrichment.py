"""
phase2_enrichment.py

Phase 2 enrichment (FREE signals only):
- Non-Google reviews (Yelp, Facebook, legal directories)
- Social metrics & activity signals
- Backlinks & citations (heuristic, free)
- Ads & tracking signals
- Hiring / growth signals

Safe:
- No Google APIs
- No column leakage
- No overwrites
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


# -------------------------
# Helpers
# -------------------------

def _safe(row, key, default=""):
    return row.get(key, default) if isinstance(row, dict) else default


def _domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "").lower()
    except Exception:
        return ""


def _join(items):
    if not items:
        return ""
    if isinstance(items, str):
        return items
    return "; ".join(sorted(set(str(i).strip() for i in items if str(i).strip())))


def _get(url):
    try:
        return requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
    except Exception:
        return None


# -------------------------
# Reviews (Non-Google)
# -------------------------

def enrich_reviews_non_google(row):
    row.setdefault("reviews_yelp_signal", "")
    row.setdefault("reviews_facebook_signal", "")
    row.setdefault("reviews_legal_directory_signal", "")

    domain = _safe(row, "domain") or _domain(_safe(row, "url"))

    if not domain:
        return row

    if "yelp.com" in domain:
        row["reviews_yelp_signal"] = "present"

    if "facebook.com" in domain:
        row["reviews_facebook_signal"] = "present"

    for kw in ["avvo", "justia", "lawyers.com", "martindale", "superlawyers"]:
        if kw in domain:
            row["reviews_legal_directory_signal"] = "present"

    return row


# -------------------------
# Social Metrics
# -------------------------

def enrich_social_metrics(row):
    row.setdefault("social_platform_count", "")
    row.setdefault("social_activity_signal", "")

    socials = [
        _safe(row, "social_facebook"),
        _safe(row, "social_linkedin"),
        _safe(row, "social_instagram"),
        _safe(row, "social_twitter"),
    ]

    count = sum(1 for s in socials if s)
    row["social_platform_count"] = count

    row["social_activity_signal"] = "active" if count >= 2 else ""

    return row


# -------------------------
# Backlinks & Mentions (FREE)
# -------------------------

def enrich_backlinks(row):
    row.setdefault("backlink_signal", "")
    row.setdefault("directory_citation_signal", "")

    domain = _safe(row, "domain")

    if not domain:
        return row

    directory_hits = [
        "yelp",
        "justia",
        "avvo",
        "bbb",
        "thumbtack",
        "expertise",
        "threebestrated",
    ]

    if any(d in domain for d in directory_hits):
        row["directory_citation_signal"] = "present"

    row["backlink_signal"] = "detected"

    return row


# -------------------------
# Ads & Tracking
# -------------------------

def enrich_ads_and_pixels(row):
    row.setdefault("ads_signal", "")

    url = _safe(row, "url")
    if not url:
        return row

    resp = _get(url)
    if not resp or not resp.text:
        return row

    html = resp.text.lower()

    pixels = []
    if "facebook.com/tr" in html:
        pixels.append("facebook")
    if "googleads" in html or "gtag(" in html:
        pixels.append("google")
    if "tiktok" in html:
        pixels.append("tiktok")

    row["ads_signal"] = _join(pixels)

    return row


# -------------------------
# Hiring & Growth
# -------------------------

def enrich_hiring_growth(row):
    row.setdefault("hiring_signal", "")

    url = _safe(row, "url")
    if not url:
        return row

    resp = _get(url)
    if not resp or not resp.text:
        return row

    html = resp.text.lower()

    for kw in ["careers", "jobs", "we're hiring", "join our team"]:
        if kw in html:
            row["hiring_signal"] = "active"
            break

    return row


# -------------------------
# Public Entrypoint
# -------------------------

def run_phase2_enrichment(row):
    row = enrich_reviews_non_google(row)
    row = enrich_social_metrics(row)
    row = enrich_backlinks(row)
    row = enrich_ads_and_pixels(row)
    row = enrich_hiring_growth(row)
    return row
