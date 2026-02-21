"""
DASHBOARD SERVER - Serves the frontend HTML
For SaaS production use
"""

from flask import Flask, send_file, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_file('COMPLETE_SYSTEM.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve any other static files if needed"""
    if os.path.exists(path):
        return send_file(path)
    return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
