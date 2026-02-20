"""
ONE-BUTTON INTELLIGENCE
Simplified version - runs everything you have
"""

import subprocess
import sys
import os
from datetime import datetime

print("=" * 70)
print("🚀 ONE-BUTTON COMPETITIVE INTELLIGENCE")
print("=" * 70)
print()

# Get inputs
query = input("🔍 Enter search query: ").strip()
if not query:
    print("❌ Query required!")
    sys.exit(1)

max_results = input("📊 Max results (default 10): ").strip() or "10"
tier = input("💰 Tier (free/pro/business, default 'pro'): ").strip() or "pro"

print()
print(f"Query: {query}")
print(f"Max: {max_results}")
print(f"Tier: {tier}")
print()
input("Press ENTER to start... ")

start = datetime.now()

# Step 1: Run profiler
print()
print("=" * 70)
print("[1/3] RUNNING PROFILER...")
print("=" * 70)

profiler = None
if os.path.exists('final_competitor_profiler_COMPLETE.py'):
    profiler = 'final_competitor_profiler_COMPLETE.py'
elif os.path.exists('final_competitor_profiler_ENHANCED.py'):
    profiler = 'final_competitor_profiler_ENHANCED.py'

if not profiler:
    print("❌ Profiler not found!")
    sys.exit(1)

try:
    process = subprocess.Popen(
        [sys.executable, profiler],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    inputs = f"{query}\n{max_results}\n"
    stdout, stderr = process.communicate(input=inputs, timeout=300)
    
    if process.returncode != 0:
        print("❌ Failed!")
        print(stderr[:500])
        sys.exit(1)
    
    print("✅ Profiler complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Step 2: Enhance data
print()
print("=" * 70)
print("[2/3] ENHANCING DATA...")
print("=" * 70)

if os.path.exists('master_profiler_v2.py'):
    try:
        result = subprocess.run(
            [sys.executable, 'master_profiler_v2.py'],
            stdin=subprocess.PIPE,
            input='\n',
            capture_output=True,
            text=True,
            timeout=60
        )
        print("✅ Keywords & traffic done!")
    except:
        print("⚠️  Enhancement had issues")
else:
    print("⚠️  master_profiler_v2.py not found")

# Step 3: Find leads
print()
print("=" * 70)
print("[3/3] FINDING LEADS...")
print("=" * 70)

if os.path.exists('lead_generation_system.py'):
    try:
        result = subprocess.run(
            [sys.executable, 'lead_generation_system.py', tier],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if os.path.exists('potential_clients.csv'):
            import csv
            with open('potential_clients.csv', 'r', encoding='utf-8') as f:
                leads = list(csv.DictReader(f))
            print(f"✅ Found {len(leads)} potential clients!")
        else:
            print("✅ Lead generation complete!")
            
    except Exception as e:
        print(f"⚠️  Leads: {str(e)[:100]}")
else:
    print("⚠️  lead_generation_system.py not found")

# Done!
elapsed = (datetime.now() - start).total_seconds()

print()
print("=" * 70)
print("✨ COMPLETE! ✨")
print("=" * 70)
print()
print(f"⏱️  Time: {int(elapsed)} seconds ({elapsed/60:.1f} minutes)")
print()
print("📁 Files:")

if os.path.exists('competitors_final_profile.xlsx'):
    print("  ✅ competitors_final_profile.xlsx")
if os.path.exists('potential_clients.csv'):
    print("  ✅ potential_clients.csv")

print()
print("🎯 Next: Open the Excel file!")
print("=" * 70)
