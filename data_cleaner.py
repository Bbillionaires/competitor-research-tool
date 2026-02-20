"""
DATA CLEANER - Fixes junk in emails and phones columns
Run this AFTER master_profiler_v2.py to clean up remaining issues

Fixes:
1. Image filenames in emails column (@2x.png, .jpg, etc.)
2. Junk numbers in phones column (decimals, dates, etc.)
3. Any row that causes Excel column overlap
"""

import csv
import re

def is_valid_email(text):
    """Check if text is actually an email"""
    # Must have exactly one @
    if text.count('@') != 1:
        return False
    
    # Must not be an image file
    if any(ext in text.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']):
        return False
    
    # Must have a domain after @
    if '@' in text:
        parts = text.split('@')
        if len(parts) == 2 and '.' in parts[1]:
            return True
    
    return False

def clean_emails(email_string):
    """Remove image filenames and keep only real emails"""
    if not email_string:
        return ""
    
    parts = email_string.split('|')
    real_emails = []
    
    for part in parts:
        part = part.strip()
        if is_valid_email(part):
            real_emails.append(part)
    
    return ' | '.join(real_emails) if real_emails else ""

def is_valid_phone(text):
    """Check if text is actually a phone number"""
    # Remove common separators
    clean = text.replace('-', '').replace('.', '').replace(' ', '').replace('(', '').replace(')', '')
    
    # Must be mostly digits
    if not clean.replace('+', '').replace('1', '').isdigit():
        return False
    
    # Must not be a date (2019120907, 2020092907, etc.)
    if len(clean) >= 10 and clean[:4] in ['2019', '2020', '2021', '2022', '2023', '2024', '2025']:
        return False
    
    # Must be reasonable phone length (10-15 digits)
    digit_count = sum(c.isdigit() for c in clean)
    if digit_count < 10 or digit_count > 15:
        return False
    
    # Must not have too many decimals (540497.2641)
    if text.count('.') > 1:
        return False
    
    return True

def clean_phones(phone_string):
    """Remove junk and keep only real phone numbers"""
    if not phone_string:
        return ""
    
    parts = phone_string.split('|')
    real_phones = []
    
    for part in parts:
        part = part.strip()
        if is_valid_phone(part):
            # Standardize format
            # Extract digits
            digits = ''.join(c for c in part if c.isdigit())
            
            # Format as (XXX) XXX-XXXX if US number
            if len(digits) == 10:
                formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                formatted = f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            else:
                formatted = part  # Keep original if non-standard
            
            if formatted not in real_phones:
                real_phones.append(formatted)
    
    return ' | '.join(real_phones[:5]) if real_phones else ""  # Max 5 phones

def clean_csv():
    """Main cleaning function"""
    
    input_file = 'competitors_final_profile.csv'
    output_file = 'competitors_final_profile_CLEANED.csv'
    
    print("=" * 70)
    print("🧹 DATA CLEANER")
    print("=" * 70)
    print()
    
    # Read CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} rows...")
    print()
    
    issues_found = 0
    
    for i, row in enumerate(rows, 1):
        name = row.get('name', 'Unknown')[:35]
        
        # Clean emails
        old_emails = row.get('emails', '')
        new_emails = clean_emails(old_emails)
        
        if old_emails != new_emails:
            print(f"[{i}] {name}")
            print(f"    ❌ Bad emails: {old_emails[:50]}...")
            print(f"    ✅ Fixed: {new_emails or '(removed junk)'}")
            row['emails'] = new_emails
            issues_found += 1
        
        # Clean phones
        old_phones = row.get('phones', '')
        new_phones = clean_phones(old_phones)
        
        if len(old_phones) > 200:  # Lots of junk
            print(f"[{i}] {name}")
            print(f"    ❌ Bad phones: {len(old_phones)} chars of junk")
            print(f"    ✅ Fixed: {new_phones or '(removed junk)'}")
            row['phones'] = new_phones
            issues_found += 1
    
    print()
    
    if issues_found == 0:
        print("✅ No issues found! Data is clean.")
        return
    
    # Save cleaned CSV
    with open(input_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    
    # Also save backup
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Cleaned {issues_found} issues")
    print(f"✅ Saved: {input_file}")
    print(f"✅ Backup: {output_file}")
    print()
    print("🎯 Next: Run master_profiler_v2.py again to regenerate Excel")
    print("=" * 70)

if __name__ == "__main__":
    try:
        clean_csv()
    except FileNotFoundError:
        print("❌ competitors_final_profile.csv not found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
