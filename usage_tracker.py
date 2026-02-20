"""
usage_tracker.py

Track API usage, monitor costs, and enforce rate limits
Prevents overspending and tracks arbitrage opportunities

Features:
- Track all API calls with timestamps
- Monitor usage against free tier limits
- Cost calculation and alerts
- Export usage reports
- Automatic rate limiting
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class UsageTracker:
    """
    Track API usage and costs across all services
    """
    
    # Free tier limits (monthly unless specified)
    FREE_TIER_LIMITS = {
        'google_cse': {'limit': 100, 'unit': 'day', 'cost_after': 5.00, 'per': 1000},  # $5 per 1000 after 100/day
        'brave_search': {'limit': 2000, 'unit': 'month', 'cost_after': 0, 'per': 1000},  # Truly free
        'serpapi': {'limit': 100, 'unit': 'month', 'cost_after': 50.00, 'per': 1000},
        'hunter_io': {'limit': 25, 'unit': 'month', 'cost_after': 49.00, 'per': 1000},
        'deepseek': {'limit': 10000000, 'unit': 'day', 'cost_after': 0.14, 'per': 1000000},  # Tokens
        'openpagerank': {'limit': 100, 'unit': 'month', 'cost_after': 0, 'per': 1000},
        'scraperapi': {'limit': 1000, 'unit': 'month', 'cost_after': 0, 'per': 1000},
        'reddit_rss': {'limit': 999999, 'unit': 'month', 'cost_after': 0, 'per': 1000},  # Unlimited free
        'duckduckgo': {'limit': 999999, 'unit': 'month', 'cost_after': 0, 'per': 1000},  # Unlimited free
    }
    
    def __init__(self, db_path: str = 'usage_tracking.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                calls INTEGER DEFAULT 1,
                tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                user_id INTEGER,
                query TEXT,
                results_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                alert_type TEXT,
                threshold_pct REAL,
                triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def track_usage(
        self, 
        service: str, 
        calls: int = 1, 
        tokens: int = 0,
        user_id: Optional[int] = None,
        query: Optional[str] = None,
        results_count: int = 0
    ) -> Dict:
        """
        Track an API call and return usage stats
        
        Returns:
            dict with usage info, warnings, and cost estimates
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate cost
        cost = self._calculate_cost(service, calls, tokens)
        
        # Log usage
        cursor.execute('''
            INSERT INTO api_usage (service, calls, tokens, cost, user_id, query, results_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (service, calls, tokens, cost, user_id, query, results_count))
        
        conn.commit()
        
        # Get current usage stats
        stats = self.get_usage_stats(service)
        
        # Check for alerts
        alerts = self._check_alerts(service, stats)
        
        conn.close()
        
        return {
            'service': service,
            'current_usage': stats,
            'cost': cost,
            'alerts': alerts,
            'can_continue': stats['usage_pct'] < 100
        }
    
    def _calculate_cost(self, service: str, calls: int, tokens: int) -> float:
        """Calculate cost for this API call"""
        if service not in self.FREE_TIER_LIMITS:
            return 0.0
        
        limits = self.FREE_TIER_LIMITS[service]
        
        # Check if we're within free tier
        current_usage = self.get_usage_stats(service)
        total_usage = current_usage['total_calls'] + calls
        
        if total_usage <= limits['limit']:
            return 0.0  # Still in free tier
        
        # Calculate overage
        overage = total_usage - limits['limit']
        cost_per_unit = limits['cost_after'] / limits['per']
        
        # For token-based services (DeepSeek)
        if tokens > 0:
            return (tokens / limits['per']) * limits['cost_after']
        
        return overage * cost_per_unit
    
    def get_usage_stats(self, service: str, period: str = 'current') -> Dict:
        """
        Get usage statistics for a service
        
        Args:
            service: API service name
            period: 'current' (day/month based on limit), 'all_time', 'today', 'this_month'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine time window
        if service in self.FREE_TIER_LIMITS:
            unit = self.FREE_TIER_LIMITS[service]['unit']
            if unit == 'day' or period == 'today':
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif unit == 'month' or period == 'this_month':
                start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = datetime(2020, 1, 1)  # All time
        else:
            start_date = datetime(2020, 1, 1)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(calls) as total_calls,
                SUM(tokens) as total_tokens,
                SUM(cost) as total_cost,
                SUM(results_count) as total_results,
                MAX(timestamp) as last_used
            FROM api_usage
            WHERE service = ? AND timestamp >= ?
        ''', (service, start_date.isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        total_calls = row[1] or 0
        total_tokens = row[2] or 0
        total_cost = row[3] or 0.0
        
        # Calculate usage percentage
        limit_info = self.FREE_TIER_LIMITS.get(service, {})
        limit = limit_info.get('limit', 999999)
        
        # For token-based services
        if total_tokens > 0:
            usage_pct = (total_tokens / limit) * 100
        else:
            usage_pct = (total_calls / limit) * 100
        
        return {
            'service': service,
            'total_requests': row[0] or 0,
            'total_calls': total_calls,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'total_results': row[4] or 0,
            'last_used': row[5],
            'limit': limit,
            'limit_unit': limit_info.get('unit', 'month'),
            'usage_pct': min(usage_pct, 100),
            'remaining': max(0, limit - (total_tokens if total_tokens > 0 else total_calls)),
            'status': 'OK' if usage_pct < 80 else 'WARNING' if usage_pct < 95 else 'CRITICAL'
        }
    
    def _check_alerts(self, service: str, stats: Dict) -> List[Dict]:
        """Check if usage triggers any alerts"""
        alerts = []
        
        usage_pct = stats['usage_pct']
        
        # 80% warning
        if usage_pct >= 80 and usage_pct < 95:
            alerts.append({
                'level': 'WARNING',
                'message': f"{service} at {usage_pct:.1f}% of free tier limit",
                'recommendation': 'Consider using alternative free service'
            })
        
        # 95% critical
        elif usage_pct >= 95 and usage_pct < 100:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"{service} at {usage_pct:.1f}% - approaching limit!",
                'recommendation': 'Switch to alternative service immediately'
            })
        
        # 100% limit reached
        elif usage_pct >= 100:
            alerts.append({
                'level': 'LIMIT_REACHED',
                'message': f"{service} free tier limit exceeded",
                'recommendation': 'Use alternative free service or wait for reset'
            })
        
        return alerts
    
    def get_all_usage(self) -> Dict:
        """Get usage for all services"""
        all_stats = {}
        
        for service in self.FREE_TIER_LIMITS.keys():
            all_stats[service] = self.get_usage_stats(service)
        
        return all_stats
    
    def get_cost_summary(self) -> Dict:
        """Get total costs and projections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # This month's costs
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        cursor.execute('''
            SELECT SUM(cost) FROM api_usage WHERE timestamp >= ?
        ''', (month_start.isoformat(),))
        
        month_cost = cursor.fetchone()[0] or 0.0
        
        # All time costs
        cursor.execute('SELECT SUM(cost) FROM api_usage')
        total_cost = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        # Calculate projection
        days_in_month = (datetime.now().replace(month=datetime.now().month % 12 + 1, day=1) - timedelta(days=1)).day
        current_day = datetime.now().day
        daily_avg = month_cost / current_day if current_day > 0 else 0
        projected_month = daily_avg * days_in_month
        
        return {
            'month_to_date': month_cost,
            'all_time': total_cost,
            'daily_average': daily_avg,
            'projected_month': projected_month,
            'days_remaining': days_in_month - current_day
        }
    
    def suggest_best_service(self, task: str = 'linkedin_search') -> str:
        """
        Suggest which service to use based on current usage
        Implements automatic arbitrage
        """
        all_usage = self.get_all_usage()
        
        # Services for LinkedIn search (in order of preference when all equal)
        linkedin_services = ['duckduckgo', 'brave_search', 'google_cse', 'serpapi']
        
        # Filter to services under 80% usage
        available = [
            (service, all_usage[service]) 
            for service in linkedin_services 
            if service in all_usage and all_usage[service]['usage_pct'] < 80
        ]
        
        if not available:
            # All services high - use unlimited free ones
            return 'duckduckgo'  # Always available
        
        # Sort by usage percentage (use least-used first)
        available.sort(key=lambda x: x[1]['usage_pct'])
        
        return available[0][0]
    
    def export_usage_report(self, output_file: str = 'usage_report.json'):
        """Export detailed usage report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'cost_summary': self.get_cost_summary(),
            'service_usage': self.get_all_usage(),
            'recommendations': self._generate_recommendations()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Usage report saved to {output_file}")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate cost-saving recommendations"""
        recommendations = []
        all_usage = self.get_all_usage()
        
        # Check for overused paid services
        for service, stats in all_usage.items():
            if stats['usage_pct'] > 50 and self.FREE_TIER_LIMITS[service]['cost_after'] > 0:
                recommendations.append(
                    f"Consider reducing {service} usage (currently {stats['usage_pct']:.1f}%) - "
                    f"switch to free alternatives"
                )
        
        # Suggest free alternatives
        if all_usage.get('google_cse', {}).get('usage_pct', 0) > 70:
            recommendations.append(
                "Google CSE usage high - switch to DuckDuckGo (unlimited free) or Brave Search (2000/month free)"
            )
        
        return recommendations
    
    def reset_usage(self, service: Optional[str] = None):
        """Reset usage tracking (use carefully - mainly for testing)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if service:
            cursor.execute('DELETE FROM api_usage WHERE service = ?', (service,))
            print(f"✅ Reset usage for {service}")
        else:
            cursor.execute('DELETE FROM api_usage')
            print("✅ Reset all usage tracking")
        
        conn.commit()
        conn.close()


# ===========================
# Wrapper Functions for Easy Integration
# ===========================

# Global tracker instance
_tracker = None

def get_tracker() -> UsageTracker:
    """Get or create global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker


def track_api_call(service: str, calls: int = 1, **kwargs) -> Dict:
    """
    Easy wrapper to track an API call
    
    Example:
        result = track_api_call('google_cse', calls=1, query='injury lawyer')
        if not result['can_continue']:
            # Switch to alternative service
            service = get_tracker().suggest_best_service()
    """
    tracker = get_tracker()
    return tracker.track_usage(service, calls, **kwargs)


def check_usage_before_call(service: str, required_calls: int = 1) -> bool:
    """
    Check if we can make API calls without exceeding limits
    
    Returns:
        True if we can proceed, False if we should use alternative
    """
    tracker = get_tracker()
    stats = tracker.get_usage_stats(service)
    
    projected_usage = stats['total_calls'] + required_calls
    limit = stats['limit']
    
    return projected_usage <= limit


def get_best_service_for_task(task: str = 'linkedin_search') -> str:
    """Get recommended service based on current usage"""
    tracker = get_tracker()
    return tracker.suggest_best_service(task)


# ===========================
# CLI for Usage Monitoring
# ===========================

if __name__ == '__main__':
    import sys
    
    tracker = UsageTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        # Generate usage report
        report = tracker.export_usage_report()
        
        print("\n" + "=" * 60)
        print("💰 COST SUMMARY")
        print("=" * 60)
        costs = report['cost_summary']
        print(f"Month to date: ${costs['month_to_date']:.2f}")
        print(f"Projected month: ${costs['projected_month']:.2f}")
        print(f"All time: ${costs['all_time']:.2f}")
        
        print("\n" + "=" * 60)
        print("📊 SERVICE USAGE")
        print("=" * 60)
        
        for service, stats in report['service_usage'].items():
            status_icon = "✅" if stats['status'] == 'OK' else "⚠️" if stats['status'] == 'WARNING' else "🔴"
            print(f"\n{status_icon} {service.upper()}")
            print(f"   Usage: {stats['usage_pct']:.1f}% ({stats['total_calls']:,} / {stats['limit']:,})")
            print(f"   Cost: ${stats['total_cost']:.2f}")
            print(f"   Remaining: {stats['remaining']:,}")
        
        if report['recommendations']:
            print("\n" + "=" * 60)
            print("💡 RECOMMENDATIONS")
            print("=" * 60)
            for rec in report['recommendations']:
                print(f"  • {rec}")
    
    else:
        # Show quick stats
        all_usage = tracker.get_all_usage()
        costs = tracker.get_cost_summary()
        
        print("\n" + "=" * 60)
        print("📊 API USAGE TRACKER")
        print("=" * 60)
        print(f"Month to date cost: ${costs['month_to_date']:.2f}")
        print(f"Projected month: ${costs['projected_month']:.2f}")
        print("\n" + "-" * 60)
        
        for service, stats in all_usage.items():
            if stats['total_calls'] > 0:
                status = "✅" if stats['status'] == 'OK' else "⚠️" if stats['status'] == 'WARNING' else "🔴"
                print(f"{status} {service}: {stats['usage_pct']:.1f}% used ({stats['total_calls']:,}/{stats['limit']:,})")
        
        print("\n💡 Run 'python usage_tracker.py report' for detailed report")
