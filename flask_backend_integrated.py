"""
COMPLETE FLASK BACKEND WITH INTELLIGENCE INTEGRATION
Handles: Auth, Search, Intelligence Pipeline, File Downloads, Progress Tracking
"""

from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
import subprocess
import sys
import csv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)

# ==========================================
# USER DATABASE (Replace with PostgreSQL in production)
# ==========================================

USERS_DB = {
    'admin@test.com': {
        'email': 'admin@test.com',
        'password': 'password',  # Hash in production!
        'tier': 'pro',
        'created_at': datetime.now().isoformat()
    }
}

USAGE_DB = {}

TIER_LIMITS = {
    'free': {'searches_per_month': 1, 'max_results': 10},
    'pro': {'searches_per_month': 10, 'max_results': 50},
    'business': {'searches_per_month': 50, 'max_results': 100},
    'enterprise': {'searches_per_month': 999999, 'max_results': 999999}
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_or_create_usage(email):
    """Get or create usage record"""
    if email not in USAGE_DB:
        USAGE_DB[email] = {
            'searches_used': 0,
            'last_reset': datetime.now().isoformat()
        }
    
    # Check if monthly reset needed
    usage = USAGE_DB[email]
    last_reset = datetime.fromisoformat(usage['last_reset'])
    if datetime.now() - last_reset > timedelta(days=30):
        usage['searches_used'] = 0
        usage['last_reset'] = datetime.now().isoformat()
    
    return usage

def get_user_from_request():
    """Get user from session or headers"""
    # Try session first
    email = session.get('user_email')
    
    # Try headers (for token auth)
    if not email:
        email = request.headers.get('X-User-Email')
    
    return email

# ==========================================
# AUTH ENDPOINTS
# ==========================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = USERS_DB.get(email)
    if not user:
        # Auto-create demo user
        if email == 'admin@test.com':
            USERS_DB[email] = {
                'email': email,
                'password': password,
                'tier': 'pro',
                'created_at': datetime.now().isoformat()
            }
            user = USERS_DB[email]
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    if user.get('password') != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Set session
    session['user_email'] = email
    
    # Get usage
    usage = get_or_create_usage(email)
    limit = TIER_LIMITS[user['tier']]['searches_per_month']
    
    return jsonify({
        'success': True,
        'user': {
            'email': email,
            'tier': user['tier'],
            'usage': {
                'used': usage['searches_used'],
                'limit': limit
            }
        },
        'token': 'demo-token-123'  # Implement real JWT in production
    })

# ==========================================
# INTELLIGENCE ENDPOINTS
# ==========================================

@app.route('/api/run-intelligence', methods=['POST'])
def run_intelligence():
    """
    Run complete intelligence pipeline
    Returns: JSON with results, files, stats
    """
    
    # Get user
    email = get_user_from_request()
    if not email:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = USERS_DB.get(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    tier = user.get('tier', 'free')
    
    # Get request data
    data = request.get_json()
    query = data.get('query', '').strip()
    max_results = data.get('max_results', 10)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    # Check usage limits
    usage = get_or_create_usage(email)
    limit = TIER_LIMITS[tier]['searches_per_month']
    
    if usage['searches_used'] >= limit:
        return jsonify({
            'error': 'Search limit reached',
            'upgrade_required': True,
            'current_tier': tier
        }), 403
    
    # Run the pipeline
    try:
        results = run_intelligence_pipeline(query, max_results, tier)
        
        if results['success']:
            # Update usage
            usage['searches_used'] += 1
            USAGE_DB[email] = usage
            
            return jsonify({
                'success': True,
                'results': results,
                'usage': {
                    'used': usage['searches_used'],
                    'limit': limit
                }
            })
        else:
            return jsonify({
                'success': False,
                'errors': results.get('errors', ['Unknown error'])
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': [str(e)]
        }), 500

def run_intelligence_pipeline(query, max_results, tier):
    """
    Run the complete intelligence pipeline
    Returns dict with success, files, stats, errors
    """
    
    results = {
        'success': False,
        'steps_completed': 0,
        'total_steps': 4,  # Profiler, Enhancement, Mentions, Leads
        'files': {},
        'stats': {},
        'errors': []
    }
    
    # Step 1: Run profiler
    profiler = None
    if os.path.exists('final_competitor_profiler_COMPLETE.py'):
        profiler = 'final_competitor_profiler_COMPLETE.py'
    elif os.path.exists('final_competitor_profiler_ENHANCED.py'):
        profiler = 'final_competitor_profiler_ENHANCED.py'
    
    if not profiler:
        results['errors'].append('Profiler not found')
        return results
    
    # Create wrapper to run profiler with mocked input
    wrapper_code = f"""
import sys
import builtins

inputs = ["{query}", "{max_results}"]
input_index = [0]

def mock_input(prompt=""):
    if input_index[0] < len(inputs):
        value = inputs[input_index[0]]
        input_index[0] += 1
        return value
    return ""

builtins.input = mock_input

with open('{profiler}', 'r', encoding='utf-8') as f:
    exec(f.read())
"""
    
    try:
        with open('_temp_wrapper.py', 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
        
        result = subprocess.run(
            [sys.executable, '_temp_wrapper.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        os.remove('_temp_wrapper.py')
        
        if result.returncode != 0:
            results['errors'].append(f'Profiler failed: {result.stderr[:200]}')
            return results
        
        results['steps_completed'] = 1
        
    except Exception as e:
        if os.path.exists('_temp_wrapper.py'):
            os.remove('_temp_wrapper.py')
        results['errors'].append(f'Profiler error: {str(e)[:200]}')
        return results
    
    # Step 2: Enhancement (keywords, traffic, Excel)
    if os.path.exists('master_profiler_v2.py'):
        try:
            wrapper2 = """
import builtins
builtins.input = lambda p="": ""
with open('master_profiler_v2.py', 'r', encoding='utf-8') as f:
    exec(f.read())
"""
            with open('_temp_wrapper2.py', 'w', encoding='utf-8') as f:
                f.write(wrapper2)
            
            result = subprocess.run(
                [sys.executable, '_temp_wrapper2.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            os.remove('_temp_wrapper2.py')
            results['steps_completed'] = 2
            
        except Exception as e:
            if os.path.exists('_temp_wrapper2.py'):
                os.remove('_temp_wrapper2.py')
            results['errors'].append(f'Enhancement warning: {str(e)[:200]}')
    
    # Step 3: Quality Mentions & Blogs
    if os.path.exists('quality_mentions_authority_blogs.py'):
        try:
            result = subprocess.run(
                [sys.executable, 'quality_mentions_authority_blogs.py'],
                capture_output=True,
                text=True,
                timeout=120
            )
        except Exception as e:
            results['errors'].append(f'Mentions warning: {str(e)[:200]}')
    
    # Step 4: Lead generation
    if os.path.exists('lead_generation_system.py'):
        try:
            result = subprocess.run(
                [sys.executable, 'lead_generation_system.py', tier],
                capture_output=True,
                text=True,
                timeout=180
            )
            results['steps_completed'] = 3
        except Exception as e:
            results['errors'].append(f'Lead gen warning: {str(e)[:200]}')
    
    # Collect file paths
    if os.path.exists('competitors_final_profile.xlsx'):
        results['files']['excel'] = 'competitors_final_profile.xlsx'
    
    if os.path.exists('potential_clients.csv'):
        results['files']['leads'] = 'potential_clients.csv'
    
    if os.path.exists('competitive_intelligence.json'):
        results['files']['dashboard_json'] = 'competitive_intelligence.json'
    
    # Calculate stats
    if os.path.exists('competitors_final_profile.csv'):
        try:
            with open('competitors_final_profile.csv', 'r', encoding='utf-8') as f:
                competitors = list(csv.DictReader(f))
            results['stats']['competitors_found'] = len(competitors)
        except:
            pass
    
    if os.path.exists('potential_clients.csv'):
        try:
            with open('potential_clients.csv', 'r', encoding='utf-8') as f:
                leads = list(csv.DictReader(f))
            
            results['stats']['total_leads'] = len(leads)
            results['stats']['high_intent_leads'] = sum(1 for l in leads if int(l.get('intent_score', 0)) >= 8)
            
            high = results['stats']['high_intent_leads']
            medium = sum(1 for l in leads if 5 <= int(l.get('intent_score', 0)) < 8)
            
            results['stats']['estimated_value_min'] = (high * 500) + (medium * 200)
            results['stats']['estimated_value_max'] = (high * 2000) + (medium * 800)
        except:
            pass
    
    results['success'] = True
    return results

# ==========================================
# FILE DOWNLOAD ENDPOINTS
# ==========================================

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated files"""
    
    # Security: whitelist allowed files
    allowed_files = [
        'competitors_final_profile.xlsx',
        'competitors_final_profile.csv',
        'potential_clients.csv',
        'competitive_intelligence.json'
    ]
    
    if filename not in allowed_files:
        return jsonify({'error': 'File not allowed'}), 403
    
    if not os.path.exists(filename):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filename, as_attachment=True)

# ==========================================
# UTILITY ENDPOINTS
# ==========================================

@app.route('/api/usage', methods=['GET'])
def get_usage():
    """Get current usage stats"""
    email = get_user_from_request()
    if not email:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = USERS_DB.get(email)
    usage = get_or_create_usage(email)
    limit = TIER_LIMITS[user['tier']]['searches_per_month']
    
    return jsonify({
        'used': usage['searches_used'],
        'limit': limit,
        'tier': user['tier']
    })

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 FLASK BACKEND WITH INTELLIGENCE INTEGRATION")
    print("=" * 70)
    print()
    print("Endpoints:")
    print("  POST /api/auth/login")
    print("  POST /api/run-intelligence")
    print("  GET  /api/download/<filename>")
    print("  GET  /api/usage")
    print()
    print("Demo Login:")
    print("  Email: admin@test.com")
    print("  Password: password")
    print()
    print("Running on: http://127.0.0.1:5000")
    print("=" * 70)
    print()
    
    app.run(debug=True, port=5000)
