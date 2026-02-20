import requests
import csv
import time

GOOGLE_API_KEY = "AIzaSyAsX5EHoJ4Vfis4z20zWxNB4r7yq4Kihfc"

def get_places(query, api_key):
    print(f"🔍 Searching Google Places for: {query}")
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(query)}&key={api_key}"
    response = requests.get(url).json()
    return response.get("results", [])

def get_place_details(place_id, api_key):
    fields = "name,rating,user_ratings_total,formatted_address,photos,url"
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={api_key}"
    response = requests.get(url).json()
    return response.get("result", {})

def get_worthofweb_traffic(domain):
    try:
        url = f"https://www.worthofweb.com/website-value/{domain}/"
        resp = requests.get(url, timeout=10)
        est_text = "Estimated Worth:"
        if est_text in resp.text:
            start = resp.text.find(est_text)
            snippet = resp.text[start:start+500]
            for line in snippet.splitlines():
                if "$" in line and "per day" in line:
                    return line.strip()
    except Exception as e:
        print(f"❌ WoW traffic error for {domain}: {e}")
    return ""

def get_similarweb_traffic(domain):
    try:
        url = f"https://data.similarweb.com/api/v1/data?domain={domain}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if "EstimatedMonthlyVisits" in data:
            return str(data["EstimatedMonthlyVisits"])
    except Exception as e:
        print(f"❌ Similarweb error for {domain}: {e}")
    return ""

def extract_domain(url):
    try:
        return url.split("//")[-1].split("/")[0].replace("www.", "")
    except:
        return ""

def main():
    search_term = input("Enter business type and location (e.g. 'injury attorney Ventura CA'): ")
    traffic_choice = input("\nChoose traffic estimation mode:\n1. High Volume (WorthOfWeb)\n2. High Accuracy (Similarweb)\nEnter 1 or 2: ")

    places = get_places(search_term, GOOGLE_API_KEY)
    if not places:
        print("❌ No results found.")
        return

    filename = "google_places_competitor_results.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "address", "rating", "user_ratings_total", "photo_count", "google_place_url", "estimated_traffic", "source_url"])

        for place in places:
            place_id = place.get("place_id")
            details = get_place_details(place_id, GOOGLE_API_KEY)
            name = details.get("name", "")
            address = details.get("formatted_address", "")
            rating = details.get("rating", "")
            user_ratings_total = details.get("user_ratings_total", "")
            photo_count = len(details.get("photos", []))
            google_url = details.get("url", "")

            domain = extract_domain(google_url)
            if traffic_choice == "1":
                traffic = get_worthofweb_traffic(domain)
            else:
                traffic = get_similarweb_traffic(domain)

            print(f"✅ {name} | Traffic: {traffic}")
            writer.writerow([name, address, rating, user_ratings_total, photo_count, google_url, traffic, domain])
            time.sleep(2)  # Respectful delay

    print(f"\n✅ Done! Results saved to: {filename}")

if __name__ == "__main__":
    main()