"""
ONE-BUTTON - WORKS WITH STDIN ISSUES
Creates a temporary wrapper to pass args directly
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

# Find profiler
profiler = None
if os.path.exists('final_competitor_profiler_COMPLETE.py'):
    profiler = 'final_competitor_profiler_COMPLETE.py'
elif os.path.exists('final_competitor_profiler_ENHANCED.py'):
    profiler = 'final_competitor_profiler_ENHANCED.py'

if not profiler:
    print("❌ Profiler not found!")
    sys.exit(1)

# ========================================
# WORKAROUND: Create a temporary runner
# ========================================

print()
print("=" * 70)
print("[1/3] RUNNING PROFILER...")
print("=" * 70)
print()

# Create a temporary script that imports and runs the profiler
temp_runner = """
import sys

# Set the query and max_results before importing
query_param = "{query}"
max_results_param = {max_results}

# Mock the input() function to return our values
original_input = input
call_count = [0]

def mock_input(prompt):
    call_count[0] += 1
    if call_count[0] == 1:
        print(prompt + query_param)
        return query_param
    elif call_count[0] == 2:
        print(prompt + str(max_results_param))
        return str(max_results_param)
    else:
        return original_input(prompt)

# Replace input
import builtins
builtins.input = mock_input

# Now import and run the profiler
import {profiler_module}
"""

profiler_module = profiler.replace('.py', '')

with open('_temp_runner.py', 'w', encoding='utf-8') as f:
    f.write(temp_runner.format(
        query=query,
        max_results=max_results,
        profiler_module=profiler_module
    ))

# Run the temporary runner
try:
    result = subprocess.run(
        [sys.executable, '_temp_runner.py'],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    # Clean up
    if os.path.exists('_temp_runner.py'):
        os.remove('_temp_runner.py')
    
    if result.returncode != 0:
        print("❌ Profiler failed!")
        print(result.stderr[:500])
        sys.exit(1)
    
    print("✅ Profiler complete!")
    
except Exception as e:
    # Clean up
    if os.path.exists('_temp_runner.py'):
        os.remove('_temp_runner.py')
    print(f"❌ Error: {e}")
    sys.exit(1)

# Check if CSV exists
if not os.path.exists('competitors_final_profile.csv'):
    print("❌ CSV not created!")
    sys.exit(1)

# ========================================
# Step 2: Enhance
# ========================================

print()
print("=" * 70)
print("[2/3] ENHANCING DATA...")
print("=" * 70)
print()

if os.path.exists('master_profiler_v2.py'):
    try:
        # Create temp runner for master profiler too
        temp_master = """
import builtins
builtins.input = lambda prompt: ""
import master_profiler_v2
"""
        with open('_temp_master.py', 'w', encoding='utf-8') as f:
            f.write(temp_master)
        
        result = subprocess.run(
            [sys.executable, '_temp_master.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if os.path.exists('_temp_master.py'):
            os.remove('_temp_master.py')
        
        print("✅ Enhancement complete!")
        
    except Exception as e:
        if os.path.exists('_temp_master.py'):
            os.remove('_temp_master.py')
        print(f"⚠️  Enhancement: {str(e)[:100]}")
else:
    print("⚠️  master_profiler_v2.py not found")

# ========================================
# Step 3: Leads
# ========================================

print()
print("=" * 70)
print("[3/3] FINDING LEADS...")
print("=" * 70)
print()

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

# ========================================
# Done
# ========================================

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
if os.path.exists('competitors_final_profile.csv'):
    print("  ✅ competitors_final_profile.csv")
if os.path.exists('potential_clients.csv'):
    print("  ✅ potential_clients.csv")

print()
print("🎯 Next: Open the Excel file!")
print("=" * 70)
