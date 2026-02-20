"""
===============================================
COMPLETE PRODUCTION BACKEND
===============================================
Features:
- User authentication (customers)
- Admin authentication (you)
- Full competitor data display
- Excel/CSV export
- Role-based permissions
- Dashboard data API
"""

from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
import json
import os
import csv
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True)

# ==========================================
# USER DATABASE (In production, use PostgreSQL)
# ==========================================

USERS = {
    # Admin account
    "admin@spaceintel.com": {
        "password": "admin123",  # Change this!
        "role": "admin",
        "company": "Space Intel",
        "tier": "enterprise"
    },
    # Demo customer account
    "demo@customer.com": {
        "password": "demo123",
        "role": "user",
        "company": "Demo Corp",
        "tier": "pro"
    }
}

# ==========================================
# AUTHENTICATION
# ==========================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User/Admin login"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = USERS.get(email)
    
    if not user or user['password'] != password:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    
    # Create session
    session['email'] = email
    session['role'] = user['role']
    
    return jsonify({
        "success": True,
        "user": {
            "email": email,
            "role": user['role'],
            "company": user['company'],
            "tier": user['tier']
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({"success": True})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'email' in session:
        user = USERS.get(session['email'])
        return jsonify({
            "authenticated": True,
            "user": {
                "email": session['email'],
                "role": session['role'],
                "company": user['company'],
                "tier": user['tier']
            }
        })
    return jsonify({"authenticated": False})

# ==========================================
# DATA API
# ==========================================

@app.route('/api/competitors', methods=['GET'])
def get_competitors():
    """Get all competitor data"""
    
    # Check authentication
    if 'email' not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    # Load data from JSON or CSV
    data = load_competitor_data()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "No data available. Run analysis first."
        }), 404
    
    return jsonify({
        "success": True,
        "data": data
    })

@app.route('/api/competitors/search', methods=['POST'])
def search_competitors():
    """Search/filter competitors"""
    
    if 'email' not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    data = request.get_json()
    filters = data.get('filters', {})
    
    competitors = load_competitor_data()
    
    if not competitors:
        return jsonify({"success": False, "error": "No data"}), 404
    
    # Apply filters
    filtered = filter_competitors(competitors.get('competitors', []), filters)
    
    return jsonify({
        "success": True,
        "data": filtered,
        "total": len(filtered)
    })

@app.route('/api/export/<format>', methods=['GET'])
def export_data(format):
    """Export data as CSV or Excel"""
    
    if 'email' not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    data = load_competitor_data()
    
    if not data:
        return jsonify({"success": False, "error": "No data"}), 404
    
    if format == 'csv':
        filepath = 'competitors_export.csv'
        export_to_csv(data.get('competitors', []), filepath)
        return send_file(filepath, as_attachment=True)
    
    elif format == 'excel':
        # Check if Excel file exists
        if os.path.exists('competitors_final_profile.xlsx'):
            return send_file('competitors_final_profile.xlsx', as_attachment=True)
        else:
            return jsonify({"success": False, "error": "Excel file not found"}), 404
    
    return jsonify({"success": False, "error": "Invalid format"}), 400

# ==========================================
# ADMIN API
# ==========================================

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    """Get all users (Admin only)"""
    
    if session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    users_list = [
        {
            "email": email,
            "role": user['role'],
            "company": user['company'],
            "tier": user['tier']
        }
        for email, user in USERS.items()
    ]
    
    return jsonify({
        "success": True,
        "users": users_list
    })

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get system statistics (Admin only)"""
    
    if session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    data = load_competitor_data()
    
    stats = {
        "total_users": len(USERS),
        "total_competitors": len(data.get('competitors', [])) if data else 0,
        "last_analysis": data.get('date') if data else None,
        "last_query": data.get('query') if data else None,
        "competitive_score": data.get('intelligence', {}).get('competitiveness_score', 0) if data else 0
    }
    
    return jsonify({
        "success": True,
        "stats": stats
    })

@app.route('/api/admin/add-user', methods=['POST'])
def add_user():
    """Add new user (Admin only)"""
    
    if session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    company = data.get('company')
    tier = data.get('tier', 'free')
    
    if email in USERS:
        return jsonify({"success": False, "error": "User already exists"}), 400
    
    USERS[email] = {
        "password": password,
        "role": "user",
        "company": company,
        "tier": tier
    }
    
    return jsonify({"success": True, "message": "User added"})

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def load_competitor_data():
    """Load competitor data from JSON or CSV"""
    
    # Try loading from JSON first
    if os.path.exists('competitive_intelligence.json'):
        with open('competitive_intelligence.json', 'r') as f:
            return json.load(f)
    
    # Try loading from CSV
    if os.path.exists('competitors_final_profile.csv'):
        competitors = []
        with open('competitors_final_profile.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            competitors = list(reader)
        
        return {
            "query": "Loaded from CSV",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "competitors": competitors,
            "intelligence": {
                "competitiveness_score": 0,
                "difficulty_rating": "Unknown",
                "market_saturation": "Unknown",
                "insights": []
            }
        }
    
    return None

def filter_competitors(competitors, filters):
    """Filter competitors based on criteria"""
    
    filtered = competitors
    
    # Filter by tier
    if filters.get('tier'):
        filtered = [c for c in filtered if c.get('tier') == filters['tier']]
    
    # Filter by minimum score
    if filters.get('min_score'):
        filtered = [c for c in filtered 
                   if int(c.get('competitor_score', 0)) >= int(filters['min_score'])]
    
    # Filter by traffic
    if filters.get('min_traffic'):
        filtered = [c for c in filtered 
                   if int(c.get('traffic_estimate', 0)) >= int(filters['min_traffic'])]
    
    # Search by name
    if filters.get('search'):
        search_term = filters['search'].lower()
        filtered = [c for c in filtered 
                   if search_term in c.get('name', '').lower() or 
                      search_term in c.get('domain', '').lower()]
    
    return filtered

def export_to_csv(competitors, filepath):
    """Export competitors to CSV"""
    
    if not competitors:
        return
    
    # Get all keys
    all_keys = set()
    for c in competitors:
        all_keys.update(c.keys())
    
    # Priority columns first
    priority = ['name', 'domain', 'address', 'phones', 'emails', 
                'traffic_estimate', 'competitor_score', 'tier']
    
    headers = [h for h in priority if h in all_keys]
    headers += sorted([k for k in all_keys if k not in priority])
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(competitors)

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SPACE INTEL PRODUCTION SERVER")
    print("="*60)
    print("\n📡 Server running on: http://localhost:5000")
    print("\n👤 Demo Accounts:")
    print("   Admin: admin@spaceintel.com / admin123")
    print("   User:  demo@customer.com / demo123")
    print("\n🔐 Change passwords before production!")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
