"""
final_competitor_profiler_complete.py - FIXED VERSION

FIXES APPLIED:
1. ✅ Column order: name FIRST, address SECOND
2. ✅ Retry logic for failed sites (like jwbrealestatecapital.com)
3. ✅ Increased timeout from 20s to 30s
4. ✅ Better error logging

ENV VARIABLES (.env file):
  GOOGLE_CSE_API_KEY=...
  GOOGLE_CSE_ID=...
  GOOGLE_PLACES_API_KEY=...
  HUNTER_API_KEY=...
  DEEPSEEK_API_KEY=...
  OPENPAGERANK_API_KEY=...
  LLM_ENABLED=true
"""

from __future__ import annotations

import os
import re
import csv
import time
import json
import math
import datetime as _dt
from urllib.parse import urlparse, urlencode, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests
from bs4 import BeautifulSoup

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from enrichments.phase1_enrichment import run_phase1_enrichment
    from enrichments.phase2_enrichment import run_phase2_enrichment
    from enrichments.phase3_enrichment import run_phase3_enrichment
except ImportError:
    def run_phase1_enrichment(row): return row
    def run_phase2_enrichment(row): return row
    def run_phase3_enrichment(row): return row

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID") or ""
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY") or ""
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY") or ""
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or ""
OPENPAGERANK_API_KEY = os.getenv("OPENPAGERANK_API_KEY") or ""
LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"

REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_URLS_SEC = 0.3
MAX_WORKERS = 3

DIRECTORY_DOMAINS = {
    "yelp.com", "www.yelp.com", "justia.com", "www.justia.com",
    "superlawyers.com", "attorneys.superlawyers.com", "avvo.com", "www.avvo.com",
    "findlaw.com", "www.findlaw.com", "lawyers.com", "www.lawyers.com",
    "expertise.com", "www.expertise.com", "threebestrated.com", "www.threebestrated.com",
    "thumbtack.com", "www.thumbtack.com", "lawcrossing.com", "www.lawcrossing.com",
    "facebook.com", "www.facebook.com", "linkedin.com", "www.linkedin.com",
    "instagram.com", "www.instagram.com", "tiktok.com", "www.tiktok.com",
    "youtube.com", "www.youtube.com",
}

DIRECTORY_KEYWORDS_IN_PATH = [
    "/lawyers/", "/attorneys/", "/directory/", "/listings/", "/best-", "/top-",
    "/search?", "/profiles/", "/people/", "/companies/",
]

JUNK_TLDS = (".gov", ".edu")

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(
    r"(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*\d{3}\s*\)|\d{3})\s*(?:[.-]\s*)?)\d{3}\s*(?:[.-]\s*)?\d{4}"
)

def safe_get(url: str, *, timeout: int = REQUEST_TIMEOUT) -> Optional[requests.Response]:
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    except Exception as e:
        print(f"⚠️  Error fetching {url[:60]}: {str(e)[:50]}")
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