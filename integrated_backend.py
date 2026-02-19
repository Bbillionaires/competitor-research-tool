"""
===============================================
COMPLETE INTEGRATED BACKEND
===============================================
Features:
- User login
- Run profiler on demand
- Return results to dashboard
- No file uploads needed
"""

from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
import subprocess
import json
import os
import csv
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True)

# USER DATABASE
USERS = {
    "admin@spaceintel.com": {
        "password": "admin123",
        "role": "admin",
        "company": "Space Intel",
        "tier": "enterprise"
    },
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
    """User login"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = USERS.get(email)
    
    if not user or user['password'] != password:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    
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

# ==========================================
# RUN ANALYSIS
# ==========================================

@app.route('/api/run-analysis', methods=['POST'])
def run_analysis():
    """Run the profiler and return results"""
    
    # Check authentication
    if 'email' not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    data = request.get_json()
    industry = data.get('industry', '')
    location = data.get('location', '')
    max_results = data.get('max_results', 10)
    
    if not industry or not location:
        return jsonify({"success": False, "error": "Industry and location required"}), 400
    
    query = f"{industry} {location}"
    
    print(f"\n🚀 Running analysis for: {query}")
    print(f"   Max results: {max_results}")
    
    try:
        # Run the profiler
        print("   ⚡ Executing profiler...")
        
        # Create input for profiler
        profiler_input = f"{query}\n{max_results}\n"
        
        result = subprocess.run(
            ['python', 'final_competitor_profiler_complete.py'],
            input=profiler_input,
            text=True,
            capture_output=True,
            timeout=300  # 5 minute timeout
        )
        
        print("   ✅ Profiler completed")
        
        # Load the results
        if os.path.exists('competitors_final_profile.csv'):
            print("   📊 Loading results...")
            
            competitors = []
            with open('competitors_final_profile.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                competitors = list(reader)
            
            # Calculate stats
            stats = calculate_stats(competitors, query)
            
            print(f"   ✅ Found {len(competitors)} competitors")
            
            return jsonify({
                "success": True,
                "query": query,
                "competitors": competitors,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Profiler ran but no results file created"
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Analysis timed out (over 5 minutes)"
        }), 500
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error running analysis: {str(e)}"
        }), 500

# ==========================================
# EXPORT
# ==========================================

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export CSV"""
    if 'email' not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    if os.path.exists('competitors_final_profile.csv'):
        return send_file('competitors_final_profile.csv', as_attachment=True)
    else:
        return jsonify({"success": False, "error": "No data available"}), 404

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    """Export Excel"""
    if 'email' not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    if os.path.exists('competitors_final_profile.xlsx'):
        return send_file('competitors_final_profile.xlsx', as_attachment=True)
    else:
        return jsonify({"success": False, "error": "No Excel file available"}), 404

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def calculate_stats(competitors, query):
    """Calculate statistics from competitor data"""
    
    if not competitors:
        return {
            "total": 0,
            "avg_traffic": 0,
            "avg_score": 0,
            "tier1_count": 0,
            "tier2_count": 0,
            "tier3_count": 0
        }
    
    total = len(competitors)
    
    # Calculate averages
    total_traffic = sum(int(c.get('traffic_estimate', 0) or 0) for c in competitors)
    total_score = sum(int(c.get('competitor_score', 0) or 0) for c in competitors)
    
    avg_traffic = total_traffic // total if total > 0 else 0
    avg_score = total_score // total if total > 0 else 0
    
    # Count tiers
    tier1 = sum(1 for c in competitors if c.get('tier') == 'Tier 1')
    tier2 = sum(1 for c in competitors if c.get('tier') == 'Tier 2')
    tier3 = sum(1 for c in competitors if c.get('tier') == 'Tier 3')
    
    return {
        "total": total,
        "avg_traffic": avg_traffic,
        "avg_score": avg_score,
        "tier1_count": tier1,
        "tier2_count": tier2,
        "tier3_count": tier3,
        "query": query
    }

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SPACE INTEL INTEGRATED BACKEND")
    print("="*60)
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n📡 Server: Port {port}")
    print("\n👤 Demo Accounts:")
    print("   User:  demo@customer.com / demo123")
    print("   Admin: admin@spaceintel.com / admin123")
    print("\n✨ Features:")
    print("   - Login → Search → Auto-run profiler → Show results")
    print("   - No file uploads needed!")
    print("="*60 + "\n")
    
    # Render requires 0.0.0.0 host
    app.run(host='0.0.0.0', port=port, debug=False)
