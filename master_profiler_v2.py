"""
🚀 MASTER COMPETITIVE INTELLIGENCE PROFILER V2
Simplified version - runs everything in the same process

Usage: python master_profiler_v2.py
"""

import os
import sys
import json
import csv
import re
import math
import random
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

print("\n" + "=" * 70)
print("🚀 MASTER COMPETITIVE INTELLIGENCE PROFILER V2")
print("=" * 70)
print()

# Get inputs
query = input("🔍 Enter search query: ").strip()
if not query:
    print("❌ Query required")
    sys.exit(1)

try:
    max_results = int(input("📊 Max results (default 20): ") or "20")
except:
    max_results = 20

print()
print("Pipeline:")
print("  1. Run profiler (manual)")
print("  2. Enhance data automatically")
print("  3. Create Excel automatically")
print("  4. Generate dashboard automatically")
print()
print("=" * 70)
print()

# STEP 1: Manual profiler run
print("⏸️  STEP 1: Please run the profiler manually")
print()
print("Open a NEW terminal window and run:")
print(f"   python final_competitor_profiler_COMPLETE.py")
print()
print("When prompted, enter:")
print(f"   Query: {query}")
print(f"   Max: {max_results}")
print()
input("Press ENTER when the profiler finishes... ")
print()

# Check if CSV exists
if not os.path.exists('competitors_final_profile.csv'):
    print("❌ CSV not found. Make sure profiler completed successfully.")
    sys.exit(1)

print("✅ CSV found!")
print()

# STEP 2-4: Auto enhancement
print("=" * 70)
print("🔧 STEP 2-4: Auto Enhancement (Keywords + Traffic + Excel)")
print("=" * 70)
print()

def extract_keywords(text):
    if not text or len(text) < 50:
        return "legal, services, professional"
    
    stopwords = {'the', 'and', 'for', 'law', 'firm', 'llp', 'pllc', 'pc', 
                 'inc', 'llc', 'attorney', 'lawyer', 'legal', 'office', 'offices'}
    
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    word_freq = {}
    for word in words:
        if word not in stopwords:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return ', '.join([w for w, c in sorted_words[:10]]) or 'professional, services'

def extract_long_tail(text):
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    phrases = []
    for i in range(min(len(words) - 2, 20)):
        p2 = f"{words[i]} {words[i+1]}"
        if len(p2) > 12 and p2 not in phrases:
            phrases.append(p2)
        p3 = f"{words[i]} {words[i+1]} {words[i+2]}"
        if len(p3) > 18 and p3 not in phrases:
            phrases.append(p3)
    return ' | '.join(phrases[:8]) or 'legal services'

def calc_traffic(row):
    da = int(row.get('domain_authority', 20))
    bl = int(row.get('backlink_signal', 10))
    wc = int(row.get('word_count', 500))
    rating = float(row.get('g_rating', 3.0))
    reviews = int(row.get('g_user_ratings_total', 0))
    
    base = 2000
    da_f = min(da / 50, 1.5) ** 1.4
    bl_f = min(math.log10(bl + 1) / 3, 2.0) ** 1.2
    wc_f = min(wc / 800, 2.5) ** 0.7
    rev_f = min(math.log10(reviews + 1) / 2, 2.0)
    rat_f = (rating / 5.0) ** 0.5
    
    traffic = base * (da_f * bl_f) ** 0.4 * (wc_f ** 0.25) * (rev_f * rat_f * 1.5) ** 0.2
    
    if bl > 250: traffic *= 2.5
    elif bl > 100: traffic *= 1.8
    elif bl > 50: traffic *= 1.4
    
    if reviews > 500: traffic *= 1.6
    elif reviews > 100: traffic *= 1.3
    
    traffic *= random.uniform(0.88, 1.12)
    return max(300, min(150000, int(round(traffic / 50) * 50)))

# Read CSV
with open('competitors_final_profile.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Processing {len(rows)} competitors...")
print()

# Enhance
for i, row in enumerate(rows, 1):
    name = row.get('name', 'Unknown')[:35]
    text = row.get('title', '') + ' ' + row.get('meta_description', '') + ' ' + row.get('h1', '')
    
    row['keywords'] = extract_keywords(text)
    row['long_tail_keywords'] = extract_long_tail(text)
    row['traffic_estimate'] = str(calc_traffic(row))
    row['traffic_formula'] = f"DA:{row.get('domain_authority')} + {row.get('backlink_signal')} BL + {row.get('g_user_ratings_total')} reviews"
    
    print(f"[{i}/{len(rows)}] {name:<35} {int(row['traffic_estimate']):>8,}/mo")

# Save CSV
with open('competitors_final_profile.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print()
print("✅ Enhancement complete")
print()

# Create Excel
print("📊 Creating Excel...")

wb = Workbook()
ws = wb.active
ws.title = "Competitors"

priority = ['name', 'domain', 'address', 'phones', 'emails', 'traffic_estimate', 
            'traffic_formula', 'keywords', 'long_tail_keywords', 'competitor_score',
            'domain_authority', 'backlink_signal', 'word_count', 'g_rating', 'g_user_ratings_total']

all_cols = list(rows[0].keys())
headers = [c for c in priority if c in all_cols] + [c for c in all_cols if c not in priority]

# Header styling
hf = Font(bold=True, color='FFFFFF', size=11, name='Arial')
hp = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')

for col_idx, h in enumerate(headers, 1):
    cell = ws.cell(1, col_idx)
    cell.value = h.replace('_', ' ').title()
    cell.font = hf
    cell.fill = hp
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Data
for row_idx, row_data in enumerate(rows, 2):
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row_idx, col_idx)
        val = row_data.get(h, '')
        
        if h in ['traffic_estimate', 'competitor_score', 'domain_authority', 'backlink_signal', 'word_count', 'g_user_ratings_total']:
            try:
                cell.value = int(float(val)) if val else 0
                cell.number_format = '#,##0'
            except:
                cell.value = val
        elif h == 'g_rating':
            try:
                cell.value = float(val)
                cell.number_format = '0.0'
            except:
                cell.value = val
        else:
            cell.value = str(val) if val else ''
        
        if row_idx % 2 == 0:
            cell.fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
        
        if h in ['keywords', 'long_tail_keywords', 'address', 'traffic_formula']:
            cell.alignment = Alignment(wrap_text=True, vertical='top')

# Widths
widths = {'name': 35, 'domain': 22, 'address': 40, 'phones': 25, 'emails': 30,
          'traffic_estimate': 16, 'traffic_formula': 35, 'keywords': 45, 'long_tail_keywords': 50}

for col_idx, h in enumerate(headers, 1):
    from openpyxl.utils import get_column_letter
    ws.column_dimensions[get_column_letter(col_idx)].width = widths.get(h, 15)

ws.freeze_panes = 'B2'
wb.save('competitors_final_profile.xlsx')

print("✅ Excel saved: competitors_final_profile.xlsx")
print()

# Dashboard JSON
print("📱 Creating dashboard JSON...")

dashboard_data = {
    'query': query,
    'date': datetime.now().strftime('%Y-%m-%d'),
    'competitors': rows,
    'intelligence': {
        'competitiveness_score': min(50 + len(rows) * 2, 100),
        'difficulty_rating': 'High' if len(rows) >= 15 else 'Moderate',
        'metrics': {
            'total_competitors': len(rows),
            'avg_traffic': int(sum(int(r['traffic_estimate']) for r in rows) / len(rows))
        }
    }
}

with open('competitive_intelligence.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=2, default=str)

print("✅ Dashboard JSON saved")
print()

print("=" * 70)
print("✨ SUCCESS! ✨")
print("=" * 70)
print()
print("📁 Files created:")
print("  ✅ competitors_final_profile.csv")
print("  ✅ competitors_final_profile.xlsx")
print("  ✅ competitive_intelligence.json")
print()
print("📊 Traffic range: {:,} - {:,}/month".format(
    min(int(r['traffic_estimate']) for r in rows),
    max(int(r['traffic_estimate']) for r in rows)
))
print()
print("🎯 Next: Open competitors_final_profile.xlsx")
print("=" * 70)
