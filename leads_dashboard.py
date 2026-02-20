"""
leads_dashboard.py

Convert JSON leads to CSV and display in terminal dashboard
Integrates with usage tracker for cost monitoring

Usage:
    python leads_dashboard.py leads_generated.json
    python leads_dashboard.py leads_generated.json --export leads.csv
"""

import json
import csv
import argparse
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from usage_tracker import get_tracker

def json_to_csv(json_file: str, csv_file: str = None) -> str:
    """
    Convert JSON leads to CSV format
    
    Args:
        json_file: Path to JSON leads file
        csv_file: Output CSV path (auto-generated if None)
    
    Returns:
        Path to created CSV file
    """
    # Load JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        leads = json.load(f)
    
    if not leads:
        print("⚠️  No leads found in JSON file")
        return None
    
    # Auto-generate CSV filename if not provided
    if not csv_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f"leads_{timestamp}.csv"
    
    # Define CSV columns
    columns = [
        'priority',
        'platform',
        'subreddit',
        'author',
        'title',
        'content',
        'url',
        'keywords_matched',
        'emails_found',
        'phones_found',
        'created_at',
        'upvotes',
        'num_comments',
        'source'
    ]
    
    # Write CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        
        for lead in leads:
            # Convert lists to strings
            row = lead.copy()
            if isinstance(row.get('emails_found'), list):
                row['emails_found'] = ' | '.join(row['emails_found'])
            if isinstance(row.get('phones_found'), list):
                row['phones_found'] = ' | '.join(row['phones_found'])
            
            writer.writerow(row)
    
    print(f"✅ Exported {len(leads)} leads to {csv_file}")
    return csv_file


def display_dashboard(json_file: str):
    """
    Display beautiful terminal dashboard with leads and usage stats
    """
    # Load leads
    with open(json_file, 'r', encoding='utf-8') as f:
        leads = json.load(f)
    
    # Get usage stats
    tracker = get_tracker()
    all_usage = tracker.get_all_usage()
    cost_summary = tracker.get_cost_summary()
    
    # Clear screen (optional)
    print("\033[2J\033[H")  # ANSI clear screen
    
    # Header
    print("=" * 80)
    print("🎯 LEAD GENERATION DASHBOARD".center(80))
    print("=" * 80)
    
    # Summary stats
    high_priority = sum(1 for l in leads if l.get('priority') == 'high')
    medium_priority = sum(1 for l in leads if l.get('priority') == 'medium')
    low_priority = sum(1 for l in leads if l.get('priority') == 'low')
    with_emails = sum(1 for l in leads if l.get('emails_found'))
    with_phones = sum(1 for l in leads if l.get('phones_found'))
    
    reddit_leads = sum(1 for l in leads if l.get('platform') == 'reddit')
    linkedin_leads = sum(1 for l in leads if l.get('platform') == 'linkedin')
    
    print(f"\n📊 LEAD SUMMARY")
    print("-" * 80)
    print(f"Total Leads: {len(leads)}")
    print(f"  🔥 High Priority: {high_priority}")
    print(f"  ⚡ Medium Priority: {medium_priority}")
    print(f"  💤 Low Priority: {low_priority}")
    print(f"  📧 With Emails: {with_emails}")
    print(f"  📞 With Phones: {with_phones}")
    print(f"\nPlatforms:")
    print(f"  Reddit: {reddit_leads}")
    print(f"  LinkedIn: {linkedin_leads}")
    
    # Cost tracking
    print(f"\n💰 COST TRACKING")
    print("-" * 80)
    print(f"Month to Date: ${cost_summary['month_to_date']:.2f}")
    print(f"Projected Month: ${cost_summary['projected_month']:.2f}")
    print(f"Daily Average: ${cost_summary['daily_average']:.2f}")
    
    # API Usage
    print(f"\n📡 API USAGE (Free Tier Limits)")
    print("-" * 80)
    
    # Show only services with usage
    active_services = {k: v for k, v in all_usage.items() if v['total_calls'] > 0}
    
    for service, stats in active_services.items():
        status_icon = "✅" if stats['status'] == 'OK' else "⚠️" if stats['status'] == 'WARNING' else "🔴"
        bar_length = 40
        filled = int((stats['usage_pct'] / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"{status_icon} {service.upper()}")
        print(f"   [{bar}] {stats['usage_pct']:.1f}%")
        print(f"   {stats['total_calls']:,} / {stats['limit']:,} {stats['limit_unit']} | ${stats['total_cost']:.2f}")
        print()
    
    # High priority leads preview
    print(f"🔥 TOP HIGH-PRIORITY LEADS")
    print("-" * 80)
    
    high_leads = [l for l in leads if l.get('priority') == 'high'][:5]
    
    if not high_leads:
        print("   No high-priority leads yet")
    else:
        for i, lead in enumerate(high_leads, 1):
            print(f"\n{i}. [{lead.get('platform', 'unknown').upper()}] {lead.get('title', 'No title')[:60]}")
            print(f"   Author: {lead.get('author', 'Unknown')}")
            if lead.get('keywords_matched'):
                print(f"   Keywords: {lead['keywords_matched']}")
            if lead.get('emails_found'):
                emails = lead['emails_found'] if isinstance(lead['emails_found'], list) else [lead['emails_found']]
                print(f"   📧 Emails: {', '.join(emails[:3])}")
            if lead.get('phones_found'):
                phones = lead['phones_found'] if isinstance(lead['phones_found'], list) else [lead['phones_found']]
                print(f"   📞 Phones: {', '.join(phones[:3])}")
            print(f"   🔗 {lead.get('url', 'No URL')}")
    
    # Alerts
    print(f"\n⚠️  ALERTS & RECOMMENDATIONS")
    print("-" * 80)
    
    alerts = []
    for service, stats in active_services.items():
        if stats['status'] in ['WARNING', 'CRITICAL']:
            alerts.append(f"{stats['status']}: {service} at {stats['usage_pct']:.1f}% - switch to alternative")
    
    if alerts:
        for alert in alerts:
            print(f"  • {alert}")
    else:
        print("  ✅ All systems operating normally")
    
    # Arbitrage opportunities
    print(f"\n💡 COST OPTIMIZATION")
    print("-" * 80)
    
    best_service = tracker.suggest_best_service('linkedin_search')
    print(f"  Recommended for LinkedIn searches: {best_service.upper()}")
    
    if cost_summary['projected_month'] > 0:
        print(f"  💰 Potential savings: ${cost_summary['projected_month']:.2f}/month")
        print(f"     (Switch high-usage paid services to free alternatives)")
    else:
        print(f"  ✅ Operating at $0/month - all free tiers!")
    
    # Footer
    print("\n" + "=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Run with --export to save as CSV")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description='View and export lead generation results')
    parser.add_argument('json_file', help='JSON leads file to process')
    parser.add_argument('--export', '-e', help='Export to CSV file')
    parser.add_argument('--dashboard', '-d', action='store_true', default=True, help='Show dashboard (default)')
    
    args = parser.parse_args()
    
    if not Path(args.json_file).exists():
        print(f"❌ File not found: {args.json_file}")
        return
    
    # Show dashboard
    if args.dashboard:
        display_dashboard(args.json_file)
    
    # Export to CSV
    if args.export:
        json_to_csv(args.json_file, args.export)
    elif not args.dashboard:
        # Auto-export if no dashboard requested
        json_to_csv(args.json_file)


if __name__ == '__main__':
    main()
