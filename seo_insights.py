import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_domain(url):
    return urlparse(url).netloc.replace('www.', '')

def get_estimated_traffic(domain):
    try:
        # Placeholder for SimilarWeb real API (you must register for key)
        headers = {'Authorization': 'Bearer YOUR_API_KEY'}
        response = requests.get(f"https://api.similarweb.com/v1/website/{domain}/total-traffic-and-engagement/overview?country=us", headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')
        est = soup.find('span', {'data-test': 'traffic-stat-value'})
        if est:
            return est.text.strip()
        return "Traffic not found"
    except Exception as e:
        return f"Error: {e}"

def process_csv(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'URL', 'Domain', 'EstimatedTraffic']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            domain = extract_domain(row['URL'])
            traffic = get_estimated_traffic(domain)
            writer.writerow({
                'Title': row['Title'],
                'URL': row['URL'],
                'Domain': domain,
                'EstimatedTraffic': traffic
            })

if __name__ == "__main__":
    process_csv('competitors.csv', 'seo_insights.csv')
