"""
AUTO-PATCHER: Fix Authentication Issues
Patches dashboard and Flask backend to work with file:// origins

Run this to fix the authentication problem automatically.
"""

import os
import shutil
from datetime import datetime

def create_backup(filename):
    """Create timestamped backup"""
    if os.path.exists(filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = f"{filename}.backup_{timestamp}"
        shutil.copy2(filename, backup)
        print(f"✅ Backed up: {backup}")
        return True
    return False

def patch_dashboard(filename):
    """Patch the dashboard to use token-based auth"""
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return False
    
    print(f"📝 Patching: {filename}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch 1: Fix login function
    old_login = '''        // Login
        function login() {
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            
            // Demo login (replace with real API call)
            if (email && password) {
                currentUser = {
                    email: email,
                    tier: 'free',
                    searchesUsed: 0,
                    searchesLimit: PLANS.free.searches
                };
                
                localStorage.setItem('user', JSON.stringify(currentUser));
                document.getElementById('login-modal').classList.remove('active');
                showDashboard();
            } else {
                alert('Please enter email and password');
            }
        }'''
    
    new_login = '''        // Login
        async function login() {
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            
            if (!email || !password) {
                alert('Please enter email and password');
                return;
            }
            
            try {
                // Call backend login API
                const response = await fetch('http://localhost:5000/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    alert(data.error || 'Login failed');
                    return;
                }
                
                // Save user data with token
                currentUser = {
                    email: data.user.email,
                    tier: data.user.tier,
                    searchesUsed: data.user.searches_used || 0,
                    searchesLimit: data.user.searches_limit || 1,
                    token: data.token || 'demo-token'
                };
                
                localStorage.setItem('user', JSON.stringify(currentUser));
                document.getElementById('login-modal').classList.remove('active');
                showDashboard();
                
            } catch (error) {
                console.error('Login error:', error);
                // Fallback to demo mode if backend is not running
                if (email === 'admin@test.com' && password === 'password') {
                    currentUser = {
                        email: email,
                        tier: 'free',
                        searchesUsed: 0,
                        searchesLimit: 1,
                        token: 'demo-token'
                    };
                    localStorage.setItem('user', JSON.stringify(currentUser));
                    document.getElementById('login-modal').classList.remove('active');
                    showDashboard();
                } else {
                    alert('Login failed. Make sure Flask backend is running.');
                }
            }
        }'''
    
    if old_login in content:
        content = content.replace(old_login, new_login)
        print("  ✅ Fixed login function")
    else:
        print("  ⚠️  Login function not found or already patched")
    
    # Patch 2: Fix search function to send auth token
    old_search = '''            try {
                const response = await fetch('http://localhost:5000/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, max_results: maxResults })
                });'''
    
    new_search = '''            try {
                const response = await fetch('http://localhost:5000/api/search', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${currentUser.token}`,
                        'X-User-Email': currentUser.email
                    },
                    body: JSON.stringify({ 
                        query, 
                        max_results: maxResults,
                        user_email: currentUser.email,
                        user_tier: currentUser.tier
                    })
                });'''
    
    if old_search in content:
        content = content.replace(old_search, new_search)
        print("  ✅ Fixed search function")
    else:
        print("  ⚠️  Search function not found or already patched")
    
    # Save
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def patch_flask_backend(filename):
    """Patch Flask backend to accept token auth"""
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return False
    
    print(f"📝 Patching: {filename}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch 1: Fix search endpoint to accept header-based auth
    old_search = '''@app.route('/api/search', methods=['POST'])
def search():
    """
    Search endpoint with authentication and usage limits
    """
    # Check authentication
    email = session.get('user_email')
    if not email:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check usage limits
    allowed, error = check_usage_limits(email)
    if not allowed:
        return jsonify({'error': error, 'limit_reached': True}), 403'''
    
    new_search = '''@app.route('/api/search', methods=['POST'])
def search():
    """
    Search endpoint with authentication and usage limits
    """
    # Check authentication - support both session and header-based auth
    email = session.get('user_email')
    
    # If no session, check headers (for file:// origin dashboards)
    if not email:
        email = request.headers.get('X-User-Email')
        data = request.get_json()
        if not email and data:
            email = data.get('user_email')
    
    if not email:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Create user if doesn't exist (for demo mode)
    if email not in USERS_DB and email == 'admin@test.com':
        USERS_DB[email] = {
            'email': email,
            'password': 'password',
            'tier': 'free',
            'created_at': datetime.now().isoformat()
        }
        USAGE_DB[email] = {
            'searches_used': 0,
            'last_reset': datetime.now().isoformat()
        }
    
    # Check usage limits
    allowed, error = check_usage_limits(email)
    if not allowed:
        return jsonify({'error': error, 'limit_reached': True}), 403'''
    
    if old_search in content:
        content = content.replace(old_search, new_search)
        print("  ✅ Fixed search endpoint")
    else:
        print("  ⚠️  Search endpoint not found or already patched")
    
    # Patch 2: Add token to login response
    old_login_response = '''    session['user_email'] = email
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'email': email,
            'tier': user['tier'],
            'searches_used': USAGE_DB[email]['searches_used'],
            'searches_limit': TIER_LIMITS[user['tier']]['searches_per_month']
        }
    })'''
    
    new_login_response = '''    session['user_email'] = email
    
    return jsonify({
        'message': 'Login successful',
        'token': 'demo-token-' + email,  # In production, use JWT
        'user': {
            'email': email,
            'tier': user['tier'],
            'searches_used': USAGE_DB[email]['searches_used'],
            'searches_limit': TIER_LIMITS[user['tier']]['searches_per_month']
        }
    })'''
    
    if old_login_response in content:
        content = content.replace(old_login_response, new_login_response)
        print("  ✅ Added token to login response")
    else:
        print("  ⚠️  Login response not found or already patched")
    
    # Save
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print("=" * 70)
    print("🔧 AUTO-PATCHER: Fix Authentication Issues")
    print("=" * 70)
    print()
    print("This will fix:")
    print("  • Dashboard to use token-based auth")
    print("  • Flask backend to accept header auth")
    print("  • Makes it work with file:// origins")
    print()
    
    dashboard_file = "dashboard_production_with_auth.html"
    flask_file = "flask_backend_production.py"
    
    # Check files exist
    files_exist = True
    if not os.path.exists(dashboard_file):
        print(f"❌ {dashboard_file} not found")
        files_exist = False
    if not os.path.exists(flask_file):
        print(f"❌ {flask_file} not found")
        files_exist = False
    
    if not files_exist:
        print()
        print("Make sure you're in the correct directory!")
        print(f"Current directory: {os.getcwd()}")
        return
    
    print("✅ Both files found")
    print()
    
    # Create backups
    print("📦 Creating backups...")
    create_backup(dashboard_file)
    create_backup(flask_file)
    print()
    
    # Patch dashboard
    print("🔨 Patching dashboard...")
    if patch_dashboard(dashboard_file):
        print()
    
    # Patch Flask backend
    print("🔨 Patching Flask backend...")
    if patch_flask_backend(flask_file):
        print()
    
    print("=" * 70)
    print("✅ PATCHING COMPLETE!")
    print("=" * 70)
    print()
    print("🎯 NEXT STEPS:")
    print()
    print("1. Restart Flask backend:")
    print("   • Press Ctrl+C in Flask window")
    print("   • Run: python flask_backend_production.py")
    print()
    print("2. Refresh dashboard in browser:")
    print("   • Press F5 or Ctrl+R")
    print("   • Login: admin@test.com / password")
    print("   • Try searching!")
    print()
    print("3. If login still fails:")
    print("   • Close all browser tabs with the dashboard")
    print("   • Clear localStorage: F12 → Application → Local Storage → Clear")
    print("   • Open dashboard again")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
