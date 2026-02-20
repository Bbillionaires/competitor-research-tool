"""
FIXES APPLIED:
1. Column order: name first, address second (lines 850-870)
2. Better error handling for jwbrealestatecapital.com (lines 815-825)
3. Increased timeout for slow sites (line 43)
4. Added retry logic for failed sites (lines 680-700)
"""

# Find line 43 and change:
REQUEST_TIMEOUT = 30  # Increased from 20 to 30

# Find line 680 and add retry logic:
def process_competitor_with_retry(url: str, query: str, max_retries: int = 2) -> Optional[dict]:
    """Process competitor with retry logic"""
    for attempt in range(max_retries):
        try:
            result = process_competitor(url, query)
            if result:
                return result
            if attempt < max_retries - 1:
                print(f"  ⟳ Retrying {extract_domain(url)}...")
                time.sleep(2)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⟳ Retry {attempt + 1} for {extract_domain(url)}: {str(e)[:50]}")
                time.sleep(2)
            else:
                print(f"  ✗ Failed after {max_retries} attempts: {extract_domain(url)}")
    return None

# Find line 810 and replace the executor section with:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_competitor_with_retry, url, query): url 
            for url in competitor_urls
        }
        
        for future in as_completed(futures):
            url = futures[future]
            domain = extract_domain(url)
            try:
                row = future.result()
                if row:
                    if domain not in seen_domains:
                        seen_domains.add(domain)
                        rows.append(row)
                        print(f"  ✓ {domain} (Score: {row.get('competitor_score', 0)})")
                    else:
                        print(f"  ⊘ Duplicate: {domain}")
                else:
                    print(f"  ✗ No data: {domain}")
            except Exception as e:
                print(f"  ✗ Error processing {domain}: {str(e)[:80]}")
            
            time.sleep(SLEEP_BETWEEN_URLS_SEC)

# Find line 843 and REPLACE the headers section with:
    # Define column order: name first, address second, then organized groups
    priority_columns = [
        'name',
        'address',
        'domain',
        'url',
        'title',
        'query',
        
        # Contact info
        'phones',
        'emails',
        'contact_page',
        
        # Google Places
        'g_name',
        'g_address',
        'g_rating',
        'g_user_ratings_total',
        'g_photo_count',
        'g_google_place_url',
        'g_place_id',
        'g_website',
        
        # Social
        'social_facebook',
        'social_linkedin',
        'social_instagram',
        'social_twitter',
        'social_platform_count',
        
        # Scores
        'competitor_score',
        'confidence_score',
        'tier',
        
        # SEO
        'domain_authority',
        'backlink_signal',
        'h1',
        'meta_description',
        'word_count',
    ]
    
    # Add remaining columns alphabetically
    remaining_columns = sorted([h for h in all_headers if h not in priority_columns])
    headers = priority_columns + remaining_columns
    
    # Remove any headers that don't exist in all_headers
    headers = [h for h in headers if h in all_headers]