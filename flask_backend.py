"""
FLASK BACKEND API
Connects the live dashboard to the profiler

Run this to enable live search in the dashboard:
python flask_backend.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for dashboard to connect

@app.route('/api/search', methods=['POST'])
def search():
    """
    API endpoint for live search
    Receives: { query: str, max_results: int }
    Returns: { competitors: [...], intelligence: {...} }
    """
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        max_results = data.get('max_results', 20)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        print(f"🔍 Search request: '{query}' (max: {max_results})")
        
        # Run the profiler
        profiler_script = 'final_competitor_profiler_COMPLETE.py'
        
        # Check if file exists
        if not os.path.exists(profiler_script):
            profiler_script = 'final_competitor_profiler_ENHANCED.py'
        
        if not os.path.exists(profiler_script):
            return jsonify({
                'error': 'Profiler not found. Make sure final_competitor_profiler_COMPLETE.py exists'
            }), 500
        
        # Run profiler with arguments
        cmd = [
            'python',
            profiler_script,
            '--query', query,
            '--max-results', str(max_results),
            '--output', 'temp_results.csv'
        ]
        
        print(f"⚡ Running profiler...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ Profiler failed: {result.stderr[:500]}")
            return jsonify({
                'error': 'Profiler execution failed',
                'details': result.stderr[:500]
            }), 500
        
        # Load results
        if os.path.exists('competitive_intelligence.json'):
            with open('competitive_intelligence.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ Found {len(data.get('competitors', []))} competitors")
            return jsonify(data)
        else:
            return jsonify({
                'error': 'Results file not found. Check profiler output.'
            }), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'error': 'Search timed out (5 min limit). Try fewer results.'
        }), 408
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'profiler': 'ready',
        'message': 'Backend is running'
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 FLASK BACKEND API - Starting")
    print("=" * 70)
    print()
    print("Dashboard can now search live!")
    print()
    print("Endpoints:")
    print("  POST http://localhost:5000/api/search")
    print("  GET  http://localhost:5000/api/status")
    print()
    print("To use:")
    print("  1. Keep this running")
    print("  2. Open dashboard_with_live_search.html")
    print("  3. Type a search query and click 🚀 Search")
    print()
    print("=" * 70)
    print()
    
    # Install flask-cors if needed
    try:
        import flask_cors
    except ImportError:
        print("⚠️  Installing flask-cors...")
        subprocess.run(['pip', 'install', 'flask-cors'], check=True)
        print("✅ Installed flask-cors")
        print()
    
    app.run(debug=True, port=5000)
