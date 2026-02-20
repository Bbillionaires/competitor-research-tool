
# FINAL COMPETITOR PROFILER (WINDOWS)
# Single-file, stable build

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

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def extract_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "").lower()
    except:
        return ""

def is_directory(domain):
    return any(k in domain for k in [
        "yelp","justia","avvo","superlawyers","findlaw","expertise",
        "thumbtack","threebestrated","directory","listing"
    ])

def clean_list(items):
    return "; ".join(sorted(set([i for i in items if i])))

def google_search(query, max_results):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    urls, start = [], 1
    while len(urls) < max_results:
        res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=10, start=start).execute()
        items = res.get("items", [])
        if not items:
            break
        for i in items:
            urls.append(i["link"])
        start += 10
    return urls[:max_results]

def duckduckgo_search(query, max_results):
    urls = []
    with DDGS() as ddgs:
        for r in ddgs.text(query):
            if "href" in r:
                urls.append(r["href"])
            if len(urls) >= max_results:
                break
    return urls

def scrape_website(url):
    data = {"emails": [], "phones": [], "facebook": [], "linkedin": [], "instagram": [], "twitter": []}
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ")
        data["emails"] = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        data["phones"] = re.findall(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
        for a in soup.find_all("a", href=True):
            h = a["href"].lower()
            if "facebook.com" in h: data["facebook"].append(h)
            if "linkedin.com" in h: data["linkedin"].append(h)
            if "instagram.com" in h: data["instagram"].append(h)
            if "twitter.com" in h or "x.com" in h: data["twitter"].append(h)
    except:
        pass
    return data

def get_place_details(query):
    if not GOOGLE_PLACES_API_KEY:
        return {}
    try:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        r = requests.get(url, params={"query":query,"key":GOOGLE_PLACES_API_KEY}).json()
        if not r.get("results"):
            return {}
        p = r["results"][0]
        return {
            "name": p.get("name",""),
            "address": p.get("formatted_address",""),
            "rating": p.get("rating",""),
            "reviews": p.get("user_ratings_total",""),
            "maps_url": f"https://www.google.com/maps/place/?q=place_id:{p.get('place_id')}"
        }
    except:
        return {}

def main():
    query = input("Enter keyword: ").strip()
    max_results = int(input("Max results (20): ") or 20)
    rows, directories, seen = [], [], set()

    urls = []
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        try:
            urls = google_search(query, max_results)
        except:
            pass
    if not urls:
        urls = duckduckgo_search(query, max_results)

    for url in urls:
        domain = extract_domain(url)
        if not domain or domain in seen:
            continue
        seen.add(domain)

        if is_directory(domain):
            directories.append({"url":url,"domain":domain})
            continue

        web = scrape_website(url)
        place = get_place_details(f"{domain} {query}")

        rows.append({
            "url": url,
            "domain": domain,
            "name": place.get("name",""),
            "address": place.get("address",""),
            "rating": place.get("rating",""),
            "reviews": place.get("reviews",""),
            "maps_url": place.get("maps_url",""),
            "emails": clean_list(web["emails"]),
            "phones": clean_list(web["phones"]),
            "facebook": clean_list(web["facebook"]),
            "linkedin": clean_list(web["linkedin"]),
            "instagram": clean_list(web["instagram"]),
            "twitter": clean_list(web["twitter"]),
        })
        time.sleep(1)

    if rows:
        with open("competitors_final_profile.csv","w",newline="",encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)

    if directories:
        with open("directories_used.csv","w",newline="",encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=directories[0].keys())
            w.writeheader()
            w.writerows(directories)

    print(f"Done. Competitors: {len(rows)}, Directories: {len(directories)}")

if __name__ == "__main__":
    main()
