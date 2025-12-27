import requests
from bs4 import BeautifulSoup
import tldextract
import re

# Optional: Uncomment and configure for Google Places enrichment
# import os
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def extract_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def fetch_page_title(url):
    try:
        print(f"🌐 Fetching title from: {url}")
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.title.string.strip() if soup.title else "No Title"
    except Exception as e:
        return f"Error: {e}"

def scrape_avvo(url):
    try:
        if "avvo.com" not in url:
            return {"Rating": "N/A", "ReviewCount": "0"}

        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        rating = soup.find("span", class_="avvo-rating-number")
        reviews = soup.find("span", class_="review-count")

        return {
            "Rating": rating.text.strip() if rating else "N/A",
            "ReviewCount": reviews.text.strip() if reviews else "0"
        }
    except:
        return {"Rating": "Error", "ReviewCount": "0"}

def scrape_yelp(url):
    try:
        if "yelp.com" not in url:
            return {"Rating": "N/A", "ReviewCount": "0", "PhotoCount": "0"}

        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        rating = soup.find("div", attrs={"role": "img"})
        reviews = soup.find("span", string=lambda t: t and "review" in t.lower())
        photos = soup.find("span", string=re.compile(r'\d+\s+photo'))

        return {
            "Rating": rating["aria-label"] if rating and "aria-label" in rating.attrs else "N/A",
            "ReviewCount": reviews.text.strip() if reviews else "0",
            "PhotoCount": photos.text.strip() if photos else "0"
        }
    except:
        return {"Rating": "Error", "ReviewCount": "0", "PhotoCount": "0"}

# Optional: Google Places Enrichment
# def enrich_with_google(domain):
#     try:
#         url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
#         params = {
#             "key": GOOGLE_API_KEY,
#             "input": domain,
#             "inputtype": "textquery",
#             "fields": "place_id"
#         }
#         r = requests.get(url, params=params)
#         place_data = r.json()
#         if not place_data.get("candidates"):
#             return {"Traffic": "N/A", "GRating": "N/A", "GReviewCount": "0"}

#         place_id = place_data["candidates"][0]["place_id"]
#         detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
#         detail_params = {
#             "key": GOOGLE_API_KEY,
#             "place_id": place_id,
#             "fields": "user_ratings_total,rating"
#         }
#         detail_r = requests.get(detail_url, params=detail_params)
#         details = detail_r.json()

#         result = details.get("result", {})
#         return {
#             "GRating": result.get("rating", "N/A"),
#             "GReviewCount": result.get("user_ratings_total", "0"),
#             "Traffic": "High" if int(result.get("user_ratings_total", 0)) > 500 else "Low"
#         }
#     except Exception as e:
#         return {"Traffic": "Error", "GRating": "Error", "GReviewCount": "0"}
