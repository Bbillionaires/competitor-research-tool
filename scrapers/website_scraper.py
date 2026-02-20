import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_website(url):
    data = {
        "emails": [],
        "phones": [],
        "logo_url": "",
        "cms": "",
        "tracking_tools": [],
        "chat_widgets": [],
        "contact_page": "",
        "booking_links": [],
        "form_count": 0,
        "social_links": {}
    }

    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        html = r.text.lower()

        # Emails
        data["emails"] = list(set(re.findall(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", html)))

        # Phones (US-style)
        data["phones"] = list(set(re.findall(r"\(?\b\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", html)))

        # Logo
        logo = soup.find("img", {"src": re.compile("logo", re.I)})
        if logo and logo.get("src"):
            data["logo_url"] = urljoin(url, logo["src"])

        # CMS detection
        if "wp-content" in html:
            data["cms"] = "WordPress"
        elif "wix.com" in html:
            data["cms"] = "Wix"
        elif "squarespace" in html:
            data["cms"] = "Squarespace"

        # Tracking
        if "googletagmanager" in html:
            data["tracking_tools"].append("Google Tag Manager")
        if "google-analytics" in html or "gtag(" in html:
            data["tracking_tools"].append("Google Analytics")
        if "facebook.com/tr" in html:
            data["tracking_tools"].append("Meta Pixel")

        # Chat widgets
        if "intercom" in html:
            data["chat_widgets"].append("Intercom")
        if "drift" in html:
            data["chat_widgets"].append("Drift")
        if "tawk.to" in html:
            data["chat_widgets"].append("Tawk.to")

        # Forms
        data["form_count"] = len(soup.find_all("form"))

        # Contact page
        for a in soup.find_all("a", href=True):
            if "contact" in a["href"].lower():
                data["contact_page"] = urljoin(url, a["href"])
                break

        # Booking links
        for a in soup.find_all("a", href=True):
            if any(k in a["href"].lower() for k in ["book", "schedule", "appointment"]):
                data["booking_links"].append(urljoin(url, a["href"]))

        # Social links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "facebook.com" in href:
                data["social_links"]["facebook"] = href
            if "linkedin.com" in href:
                data["social_links"]["linkedin"] = href
            if "instagram.com" in href:
                data["social_links"]["instagram"] = href
            if "twitter.com" in href or "x.com" in href:
                data["social_links"]["twitter"] = href

    except Exception as e:
        pass

    return data