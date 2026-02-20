import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CompetitorProfiler/1.0)"
}

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"

SOCIAL_DOMAINS = {
    "facebook": "facebook.com",
    "linkedin": "linkedin.com",
    "instagram": "instagram.com",
    "twitter": "twitter.com",
    "x": "x.com"
}

CMS_SIGNATURES = {
    "WordPress": ["wp-content", "wp-includes"],
    "Wix": ["wix.com", "wixstatic.com"],
    "Squarespace": ["squarespace.com"],
    "Shopify": ["cdn.shopify.com"],
}

TRACKING_SIGNATURES = {
    "Google Analytics": ["google-analytics.com", "gtag("],
    "Google Tag Manager": ["googletagmanager.com"],
    "Meta Pixel": ["facebook.com/tr", "fbq("],
}

CHAT_SIGNATURES = [
    "intercom",
    "tawk.to",
    "livechat",
    "zendesk",
    "drift",
    "crisp.chat"
]


def scrape_website(url):
    data = {
        "emails": [],
        "phones": [],
        "logo_url": "",
        "social_links": {},
        "cms": "",
        "tracking_tools": [],
        "chat_widgets": [],
        "contact_page": "",
        "booking_links": [],
        "form_count": 0,
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return data

    text = soup.get_text(" ", strip=True)

    # Emails & phones
    data["emails"] = list(set(re.findall(EMAIL_REGEX, html)))
    data["phones"] = list(set(re.findall(PHONE_REGEX, text)))

    # Logo
    logo = soup.find("img", {"class": re.compile("logo", re.I)})
    if logo and logo.get("src"):
        data["logo_url"] = urljoin(url, logo["src"])

    # Social links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        for name, domain in SOCIAL_DOMAINS.items():
            if domain in href:
                data["social_links"][name] = href

    # CMS detection
    for cms, sigs in CMS_SIGNATURES.items():
        if any(sig in html for sig in sigs):
            data["cms"] = cms
            break

    # Tracking tools
    for tool, sigs in TRACKING_SIGNATURES.items():
        if any(sig in html for sig in sigs):
            data["tracking_tools"].append(tool)

    # Chat widgets
    for sig in CHAT_SIGNATURES:
        if sig in html.lower():
            data["chat_widgets"].append(sig)

    # Contact page
    for a in soup.find_all("a", href=True):
        if "contact" in a["href"].lower():
            data["contact_page"] = urljoin(url, a["href"])
            break

    # Booking links
    for a in soup.find_all("a", href=True):
        if any(k in a["href"].lower() for k in ["book", "schedule", "appointment"]):
            data["booking_links"].append(urljoin(url, a["href"]))

    # Forms
    data["form_count"] = len(soup.find_all("form"))

    return data
