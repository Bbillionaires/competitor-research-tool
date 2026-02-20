import os
import csv
import time
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ddgs import DDGS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

DIRECTORY_KEYWORDS = [
    "yelp.", "justia.", "avvo.", "findlaw.", "superlawyers.",
    "expertise.", "thumbtack.", "threebestrated.", "lawyers.",
    "attorneys.", "legalmatch.", "lawinfo."
]

MAX_RESULTS_DEFAULT = 20

def extract_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""

def is_directory(domain):
    return any(d in domain for d in DIRECTORY_KEYWORDS)

def clean_list(values):
    return "; ".join(sorted(set(v for v in values if v)))

def get_title(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.title.text.strip() if soup.title else ""
    except:
        return ""

def scrape_website(url):
    data = {
        "emails": [],
        "phones": [],
        "social_facebook": [],
        "social_linkedin": [],
        "social_instagram": [],
        "social_twitter": []
    }
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        html = r.text

        data["emails"] = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)
        data["phones"] = re.findall(r"\\(?\\b\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}\\b", html)

        for link in re.findall(r'href=["\\\'](.*?)["\\\']', html):
            if "facebook.com" in link:
                data["social_facebook"].append(link)
            elif "linkedin.com" in link:
                data["social_linkedin"].append(link)
            elif "instagram.com" in link:
                data["social_instagram"].append(link)
            elif "twitter.com" in link or "x.com" in link:
                data["social_twitter"].append(link)
    except:
        pass

    return {
        "emails": clean_list(data["emails"]),
        "phones": clean_list(data["phones"]),
        "social_facebook": clean_list(data["social_facebook"]),
        "social_linkedin": clean_list(data["social_linkedin"]),
        "social_instagram": clean_list(data["social_instagram"]),
        "social_twitter": clean_list(data["social_twitter"])
    }

def google_like_search(query, max_results):
    urls = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results * 2):
            href = r.get("href")
            if href and href.startswith("http"):
                urls.append(href)
            if len(urls) >= max_results:
                break
    return urls

def compute_score(row):
    score = 0
    if row["emails"]:
        score += 10
    if row["phones"]:
        score += 10
    if not is_directory(row["domain"]):
        score += 40
    return score

def classify(score):
    if score >= 60:
        return "Tier 1"
    elif score >= 30:
        return "Tier 2"
    return "Tier 3"

def main():
    query = input("Enter keyword (e.g. injury attorney Ventura CA): ").strip()
    max_results = input(f"Max # of results (default {MAX_RESULTS_DEFAULT}): ").strip()
    max_results = int(max_results) if max_results.isdigit() else MAX_RESULTS_DEFAULT

    print("🔍 Searching Google-style results...")
    urls = google_like_search(query, max_results)

    print(f"🧪 URL COUNT: {len(urls)}")

    rows = []
    directories = []
    seen_domains = set()

    for url in urls:
        domain = extract_domain(url)
        if not domain or domain in seen_domains:
            continue
        seen_domains.add(domain)

        row = {
            "url": url,
            "domain": domain,
            "title": get_title(url),
            "traffic_estimate": "N/A"
        }

        row.update(scrape_website(url))
        row["competitor_score"] = compute_score(row)
        row["tier"] = classify(row["competitor_score"])

        if is_directory(domain):
            directories.append(row)
        else:
            rows.append(row)

        time.sleep(0.5)

    if rows:
        with open("top_competitors.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    if directories:
        with open("directories.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=directories[0].keys())
            writer.writeheader()
            writer.writerows(directories)

    print("✅ Done. Files generated.")

if __name__ == "__main__":
    main()
