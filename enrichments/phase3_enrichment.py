"""
enrichments/phase3_enrichment.py

PHASE 3 – FREE signals enrichment
Adds:
- backlink_signal (heuristic)
- ads_library_signal
- hiring_growth_signal
- social_metrics_signal

NO APIs required
SAFE column handling
"""

from __future__ import annotations

import re
import requests
from urllib.parse import urlparse

# -------------------------
# Helpers
# -------------------------

def _safe_get(d: dict, k: str, default=""):
    return d.get(k, default) if isinstance(d, dict) else default

def _http_get(url: str, timeout: int = 20):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        return requests.get(url, headers=headers, timeout=timeout)
    except Exception:
        return None

def _domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

# -------------------------
# Backlink signal (FREE heuristic)
# -------------------------

def enrich_backlink_signals(row: dict) -> dict:
    row.setdefault("backlink_signal", "")

    url = _safe_get(row, "url", "")
    if not url:
        return row

    resp = _http_get(url)
    if not resp or not resp.text:
        return row

    html = resp.text.lower()

    backlink_hits = 0
    if 'href="http' in html:
        backlink_hits += html.count('href="http')

    row["backlink_signal"] = backlink_hits
    return row

# -------------------------
# Ads library signal
# -------------------------

def enrich_ads_library_signal(row: dict) -> dict:
    row.setdefault("ads_library_signal", "")

    url = _safe_get(row, "url", "")
    if not url:
        return row

    resp = _http_get(url)
    if not resp or not resp.text:
        return row

    html = resp.text.lower()
    ads = []

    if "adsbygoogle" in html or "googlesyndication" in html:
        ads.append("google_ads")

    if "facebook pixel" in html or "fbq(" in html:
        ads.append("meta_ads")

    if "doubleclick.net" in html:
        ads.append("doubleclick")

    row["ads_library_signal"] = "; ".join(sorted(set(ads)))
    return row

# -------------------------
# Hiring growth signal
# -------------------------

def enrich_hiring_growth_signal(row: dict) -> dict:
    row.setdefault("hiring_growth_signal", "")

    url = _safe_get(row, "url", "")
    if not url:
        return row

    resp = _http_get(url)
    if not resp or not resp.text:
        return row

    html = resp.text.lower()
    hiring_hits = []

    for kw in ["careers", "jobs", "join our team", "hiring"]:
        if kw in html:
            hiring_hits.append(kw)

    row["hiring_growth_signal"] = "; ".join(sorted(set(hiring_hits)))
    return row

# -------------------------
# Social metrics (presence)
# -------------------------

def enrich_social_metrics(row: dict) -> dict:
    row.setdefault("social_metrics_signal", "")

    socials = []
    for key in [
        "social_facebook",
        "social_linkedin",
        "social_instagram",
        "social_twitter",
    ]:
        val = _safe_get(row, key, "")
        if val:
            socials.append(key.replace("social_", ""))

    row["social_metrics_signal"] = "; ".join(sorted(set(socials)))
    return row

# -------------------------
# PUBLIC ORCHESTRATOR
# -------------------------

def run_phase3_enrichment(row: dict) -> dict:
    """
    Phase 3 enrichment orchestrator
    """
    row = enrich_backlink_signals(row)
    row = enrich_ads_library_signal(row)
    row = enrich_hiring_growth_signal(row)
    row = enrich_social_metrics(row)
    return row