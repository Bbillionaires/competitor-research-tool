import csv
import time
import requests
from urllib.parse import urlparse
from duckduckgo_search import DDGS

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual key

def extract_domain_name(url):
    try:
        return urlparse(url).netloc.replace("www.", "").split("/")[0]
    except:
        return ""

def get_duckduckgo_results(search_term, max_results=30):
    urls = []
    with DDGS() as ddgs:
        for r in ddgs.text(search_term, max_results=max_results):
            if r.get("href") and "http" in r["href"]:
                urls.append(r["href"])
    return urls

def get_place_details(query, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(query)}&key={api_key}"
    resp = requests.get(url).json()
    print(f"📦 Google TextSearch API response: {resp}")
    if "results" in resp and resp["results"]:
        result = resp["results"][0]
        place_id = result["place_id"]
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}&fields=name,rating,user_ratings_total,formatted_address,photos,url"
        details = requests.get(details_url).json()
        print(f"📦 Google Place Details API response: {details}")
        if "result" in details:
            place = details["result"]
            return {
                "name": place.get("name", ""),
                "address": place.get("formatted_address", ""),
                "rating": place.get("rating", ""),
                "user_ratings_total": place.get("user_ratings_total", ""),
                "photo_count": len(place.get("photos", [])),
                "google_place_url": place.get("url", "")
            }
    return None

def get_worthofweb_traffic(domain):
    try:
        url = f"https://www.worthofweb.com/website-value/{domain}/"
        response = requests.get(url, timeout=10)
        if response.ok:
            text = response.text
            if 'Estimated Worth' in text:
                return "Yes (WoW)"
        return ""
    except:
        return ""

def get_similarweb_traffic(domain):
    try:
        sw_url = f"https://data.similarweb.com/api/v1/data?domain={domain}"
        response = requests.get(sw_url, timeout=10)
        if response.ok:
            data = response.json()
            visits = data.get("visits", "")
            return visits if visits else ""
        return ""
    except:
        return ""

def main():
    search_term = input("Enter a keyword or business type + location: ").strip()
    max_results = input("Max # of DuckDuckGo results (e.g. 30): ").strip()
    max_results = int(max_results) if max_results.isdigit() else 30

    print("\nChoose traffic estimation mode:")
    print("1. High Volume (WorthOfWeb) – shows *potential*")
    print("2. High Accuracy (Similarweb) – shows *current* traffic")
    traffic_choice = input("Enter 1 or 2: ").strip()
    use_wow = traffic_choice == "1"

    print(f"\n🔍 Searching DuckDuckGo for: {search_term}")
    urls = get_duckduckgo_results(search_term, max_results=max_results)
    print(f"🧪 DuckDuckGo URLs: {urls}")

    if not urls:
        print("\n⚠️ No results returned. Try a simpler or broader keyword like:")
        print("   ➤ 'injury lawyers in California'")
        print("   ➤ 'law firms Ventura'")
        return  # Exit early, skip CSV generation

    enriched = []

    for url in urls:
        print(f"🔗 Checking URL: {url}")
        domain = extract_domain_name(url)
        print(f"🔍 Domain for Google Places Search: {domain}")

        details = get_place_details(f"{domain} {search_term}", GOOGLE_API_KEY)
        print(f"✅ Enrichment details: {details}")

        traffic = get_worthofweb_traffic(domain) if use_wow else get_similarweb_traffic(domain)

        row = {
            "source_url": url,
            "name": "",
            "address": "",
            "rating": "",
            "user_ratings_total": "",
            "photo_count": "",
            "google_place_url": "",
            "traffic_estimate": traffic
        }

        if details:
            row.update(details)

        print(f"📝 Row to save: {row}")
        enriched.append(row)
        time.sleep(1.5)

    # Write only if we have results
    if enriched:
        with open("competitors_google_places_enriched.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=enriched[0].keys())
            writer.writeheader()
            writer.writerows(enriched)
        print("\n✅ Saved enriched data to competitors_google_places_enriched.csv")
    else:
        print("\n⚠️ No enriched data to save. All lookups may have failed.")

if __name__ == "__main__":
    main()