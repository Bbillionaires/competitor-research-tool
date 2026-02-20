"""
QUICK PATCH: Fix login KeyError
Run this to fix the password error in Flask backend
"""

import os

def fix_login_error():
    filename = "flask_backend_production.py"
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the login function
    old_code = '''    user = USERS_DB.get(email)
    if not user or user['password'] != password:  # Should verify hashed password
        return jsonify({'error': 'Invalid credentials'}), 401'''
    
    new_code = '''    user = USERS_DB.get(email)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password (should be hashed in production)
    if user.get('password') != password:
        return jsonify({'error': 'Invalid credentials'}), 401'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed login KeyError!")
        print()
        print("Now restart Flask:")
        print("  1. Press Ctrl+C in Flask window")
        print("  2. Make sure venv is activated: .\\venv\\Scripts\\Activate")
        print("  3. Run: python flask_backend_production.py")
    else:
        print("⚠️  Code already patched or different version")

if __name__ == "__main__":
    print("🔧 Fixing Flask login error...")
    print()
    fix_login_error()
