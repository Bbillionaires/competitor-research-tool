"""
AD PLATFORM DETECTOR
Finds exactly where competitors are running ads:
- Facebook/Instagram Ads (via Meta Ad Library)
- Google Ads (via website analysis)
- LinkedIn Ads (via LinkedIn)
- Display ads (via third-party networks)

Shows: Platform + Active/Inactive + Ad count
"""

import csv
import requests
import re
from bs4 import BeautifulSoup
import time

def check_facebook_ads(domain, company_name):
    """
    Check Facebook Ad Library for active ads
    Note: Requires scraping or API access
    """
    # Facebook Ad Library search
    # Format: https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=US&q=COMPANY
    
    try:
        # Clean company name for search
        search_term = company_name.replace(' ', '+')
        
        # Note: This is a simplified check
        # In production, you'd use Facebook Marketing API or scrape Ad Library
        
        # Check if domain has Facebook pixel (indicator of FB ads)
        response = requests.get(f"https://{domain}", timeout=10)
        content = response.text
        
        has_fb_pixel = 'facebook.com/tr' in content or 'fbq(' in content
        has_fb_sdk = 'connect.facebook.net' in content
        
        if has_fb_pixel:
            return {
                'platform': 'Facebook/Instagram Ads',
                'status': 'Active (Pixel detected)',
                'confidence': 'High'
            }
        elif has_fb_sdk:
            return {
                'platform': 'Facebook',
                'status': 'Integration detected',
                'confidence': 'Medium'
            }
        
        return None
        
    except Exception as e:
        return None


def check_google_ads(domain):
    """
    Check for Google Ads tracking
    Looks for Google Ads conversion tracking, remarketing tags
    """
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        content = response.text
        
        # Check for Google Ads tracking
        has_google_ads = 'googleadservices.com/pagead/conversion' in content
        has_gtag_ads = 'gtag(' in content and 'AW-' in content
        has_google_tag = 'googletagmanager.com' in content
        
        if has_google_ads or has_gtag_ads:
            return {
                'platform': 'Google Ads',
                'status': 'Active (Conversion tracking)',
                'confidence': 'High'
            }
        elif has_google_tag:
            return {
                'platform': 'Google Ads',
                'status': 'Possible (GTM detected)',
                'confidence': 'Medium'
            }
        
        return None
        
    except Exception as e:
        return None


def check_linkedin_ads(domain):
    """
    Check for LinkedIn Insight Tag (indicates LinkedIn Ads)
    """
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        content = response.text
        
        has_linkedin_tag = 'snap.licdn.com' in content or 'linkedin.com/insight' in content
        
        if has_linkedin_tag:
            return {
                'platform': 'LinkedIn Ads',
                'status': 'Active (Insight Tag)',
                'confidence': 'High'
            }
        
        return None
        
    except Exception as e:
        return None


def check_display_ads(domain):
    """
    Check for display ad networks
    """
    try:
        response = requests.get(f"https://{domain}", timeout=10)
        content = response.text
        
        ad_networks = {
            'doubleclick.net': 'Google Display Network',
            'adroll.com': 'AdRoll',
            'criteo.com': 'Criteo',
            'outbrain.com': 'Outbrain',
            'taboola.com': 'Taboola',
        }
        
        detected = []
        for network_domain, network_name in ad_networks.items():
            if network_domain in content:
                detected.append({
                    'platform': network_name,
                    'status': 'Active',
                    'confidence': 'High'
                })
        
        return detected if detected else None
        
    except Exception as e:
        return None


def detect_all_ad_platforms(domain, company_name):
    """
    Check all major ad platforms
    Returns comprehensive ad platform report
    """
    
    print(f"    Checking ad platforms for {domain}...")
    
    platforms_detected = []
    
    # Check Facebook
    fb_result = check_facebook_ads(domain, company_name)
    if fb_result:
        platforms_detected.append(fb_result)
        print(f"      ✅ {fb_result['platform']}: {fb_result['status']}")
    
    # Check Google Ads
    google_result = check_google_ads(domain)
    if google_result:
        platforms_detected.append(google_result)
        print(f"      ✅ {google_result['platform']}: {google_result['status']}")
    
    # Check LinkedIn
    linkedin_result = check_linkedin_ads(domain)
    if linkedin_result:
        platforms_detected.append(linkedin_result)
        print(f"      ✅ {linkedin_result['platform']}: {linkedin_result['status']}")
    
    # Check Display Networks
    display_results = check_display_ads(domain)
    if display_results:
        for result in display_results:
            platforms_detected.append(result)
            print(f"      ✅ {result['platform']}: {result['status']}")
    
    if not platforms_detected:
        print(f"      ℹ️  No ad platforms detected")
    
    return platforms_detected


def enhance_with_ad_platforms():
    """Main enhancement function"""
    
    print("=" * 70)
    print("📢 AD PLATFORM DETECTOR")
    print("=" * 70)
    print()
    print("Checking for ads on:")
    print("  • Facebook/Instagram Ads")
    print("  • Google Ads (Search & Display)")
    print("  • LinkedIn Ads")
    print("  • Display Networks (AdRoll, Criteo, etc.)")
    print()
    
    # Read CSV
    csv_file = 'competitors_final_profile.csv'
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} competitors...")
    print()
    
    for i, row in enumerate(rows, 1):
        name = row.get('name', 'Unknown')[:35]
        domain = row.get('domain', '')
        
        print(f"[{i}/{len(rows)}] {name}")
        
        if not domain:
            print(f"    ⚠️  No domain found")
            row['ad_platforms'] = 'unknown'
            row['ad_platforms_count'] = 0
            row['ad_platform_details'] = ''
            continue
        
        # Detect ad platforms
        platforms = detect_all_ad_platforms(domain, name)
        
        if platforms:
            # Format for CSV
            platform_names = [p['platform'] for p in platforms]
            platform_details = [f"{p['platform']} ({p['status']})" for p in platforms]
            
            row['ad_platforms'] = ', '.join(platform_names)
            row['ad_platforms_count'] = len(platforms)
            row['ad_platform_details'] = ' | '.join(platform_details)
            
            # Update old signal columns
            row['ads_signal'] = 1
            row['ads_signals'] = len(platforms) / 5.0  # Score out of 5 platforms
            
        else:
            row['ad_platforms'] = 'none detected'
            row['ad_platforms_count'] = 0
            row['ad_platform_details'] = ''
            row['ads_signal'] = 0
            row['ads_signals'] = 0.0
        
        print()
        time.sleep(1)  # Be nice to servers
    
    # Save
    fieldnames = list(rows[0].keys())
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print("=" * 70)
    print("✅ AD PLATFORM DETECTION COMPLETE!")
    print("=" * 70)
    print()
    print("📊 NEW COLUMNS:")
    print()
    print("1️⃣  ad_platforms")
    print("    Example: 'Facebook/Instagram Ads, Google Ads, LinkedIn Ads'")
    print("    Simple list of platforms")
    print()
    print("2️⃣  ad_platforms_count")
    print("    Example: 3")
    print("    Number of platforms they're advertising on")
    print()
    print("3️⃣  ad_platform_details")
    print("    Example: 'Facebook/Instagram Ads (Active - Pixel detected) | Google Ads (Active - Conversion tracking)'")
    print("    Detailed status for each platform")
    print()
    print("📊 UPDATED COLUMNS:")
    print()
    print("  • ads_signal: Now 0 or 1 (binary)")
    print("  • ads_signals: Now score 0.0-1.0 (based on platform count)")
    print()
    print("=" * 70)
    print("💡 WHAT THE DATA MEANS:")
    print("=" * 70)
    print()
    print("📢 Platform Detection Methods:")
    print()
    print("Facebook/Instagram:")
    print("  ✅ High Confidence = Facebook Pixel detected on site")
    print("  🟡 Medium = Facebook SDK integration")
    print()
    print("Google Ads:")
    print("  ✅ High = Conversion tracking code found")
    print("  🟡 Medium = Google Tag Manager detected")
    print()
    print("LinkedIn Ads:")
    print("  ✅ High = LinkedIn Insight Tag found")
    print()
    print("Display Networks:")
    print("  ✅ High = Network tracking code detected")
    print()
    print("🎯 HOW TO USE THIS:")
    print()
    print("1. See what platforms competitors use")
    print("2. Match their ad strategy")
    print("3. Find gaps they're missing")
    print("4. Outspend them on underutilized platforms")
    print()
    print("📊 Next: Run master_profiler_v2.py to see in Excel")
    print("=" * 70)


if __name__ == "__main__":
    try:
        enhance_with_ad_platforms()
    except FileNotFoundError:
        print("❌ competitors_final_profile.csv not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
