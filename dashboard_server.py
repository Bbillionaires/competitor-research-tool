"""
dashboard_server.py - STANDALONE Live Dashboard Server
Run this separately from your existing app.py

This is a brand new server that:
- Runs on port 5001 (not 5000, won't conflict)
- Has its own routes and logic
- Uses your existing profiler and database
- Doesn't modify any of your current files

Usage:
    python dashboard_server.py
    
Then visit: http://localhost:5001
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import os
import json
import threading
from datetime import datetime
from dotenv import load_dotenv
import sys

# Import your existing components (no modifications needed)
try:
    from neon_database_manager import NeonDatabaseManager
    NEON_AVAILABLE = True
except ImportError:
    NEON_AVAILABLE = False
    print("⚠️  NeonDatabaseManager not found - will work without caching")

load_dotenv()

# Create Flask app
dashboard_app = Flask(__name__)
dashboard_app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dashboard-secret-key-12345')
CORS(dashboard_app)
socketio = SocketIO(dashboard_app, cors_allowed_origins="*")

# Global state for active scans
active_scans = {}
scan_results = {}

# ============================================================================
# DASHBOARD HTML (embedded in this file - no external templates needed)
# ============================================================================

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Competitor Intelligence Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --space-black: #0a0e27;
            --space-dark: #141b3d;
            --space-purple: #6366f1;
            --space-cyan: #06b6d4;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --card-bg: rgba(30, 41, 59, 0.6);
            --border-color: rgba(99, 102, 241, 0.3);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--space-black);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            padding: 2rem;
            background: var(--card-bg);
            border-radius: 16px;
            border: 1px solid var(--border-color);
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--space-cyan), var(--space-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .scan-form {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        
        .form-input {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 0.75rem 1rem;
            color: var(--text-primary);
            font-size: 1rem;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--space-purple), var(--space-cyan));
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            border: none;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
        }
        
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .progress-section {
            display: none;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 1rem;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--space-purple), var(--space-cyan));
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--space-cyan), var(--space-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .table-container {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            text-align: left;
            padding: 1rem;
            color: var(--text-secondary);
            font-size: 0.85rem;
            text-transform: uppercase;
            border-bottom: 2px solid var(--border-color);
        }
        
        td {
            padding: 1rem;
            border-bottom: 1px solid rgba(99, 102, 241, 0.1);
        }
        
        tr:hover {
            background: rgba(99, 102, 241, 0.05);
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .chart-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
        }
        
        .chart-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--space-cyan);
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌌 Competitor Intelligence Platform</h1>
            <p style="color: var(--text-secondary);">Live Market Analysis Dashboard</p>
        </div>

        <div class="scan-form">
            <h2 style="margin-bottom: 1.5rem;">Start New Analysis</h2>
            <div class="form-group">
                <label class="form-label">Search Query</label>
                <input type="text" id="queryInput" class="form-input" 
                       placeholder="e.g., real estate investors jacksonville fl">
            </div>
            <div class="form-group">
                <label class="form-label">Maximum Results</label>
                <input type="number" id="maxResults" class="form-input" 
                       value="20" min="5" max="50">
            </div>
            <button id="startBtn" class="btn-primary">🚀 Start Analysis</button>
        </div>

        <div id="progressSection" class="progress-section">
            <h3 style="margin-bottom: 1rem;">Scanning in Progress...</h3>
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%">0%</div>
            </div>
            <div id="progressMsg" style="color: var(--text-secondary); text-align: center;">Initializing...</div>
        </div>

        <div id="resultsSection" style="display: none;">
            <div class="dashboard-grid">
                <div class="stat-card">
                    <div class="stat-value" id="totalCompetitors">0</div>
                    <div class="stat-label">Competitors Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avgScore">0</div>
                    <div class="stat-label">Average Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="totalTraffic">0</div>
                    <div class="stat-label">Total Traffic/Month</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="totalMentions">0</div>
                    <div class="stat-label">Total Mentions</div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">📊 Top 5 by Traffic</div>
                    <canvas id="trafficChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">⭐ Rating Distribution</div>
                    <canvas id="ratingChart"></canvas>
                </div>
            </div>

            <div class="table-container">
                <h3 style="margin-bottom: 1rem; color: var(--space-cyan);">All Competitors</h3>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Name</th>
                            <th>Score</th>
                            <th>Traffic</th>
                            <th>Rating</th>
                            <th>Mentions</th>
                        </tr>
                    </thead>
                    <tbody id="resultsTable"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let currentScanId = null;

        socket.on('scan_progress', (data) => {
            if (data.scan_id === currentScanId) {
                document.getElementById('progressFill').style.width = data.progress + '%';
                document.getElementById('progressFill').textContent = data.progress + '%';
                document.getElementById('progressMsg').textContent = data.message;
            }
        });

        socket.on('scan_complete', (data) => {
            if (data.scan_id === currentScanId) {
                loadResults(currentScanId);
            }
        });

        document.getElementById('startBtn').addEventListener('click', async () => {
            const query = document.getElementById('queryInput').value.trim();
            const maxResults = parseInt(document.getElementById('maxResults').value);

            if (!query) {
                alert('Please enter a search query');
                return;
            }

            const btn = document.getElementById('startBtn');
            btn.disabled = true;
            btn.textContent = '⏳ Starting...';

            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            try {
                const response = await fetch('/api/start-scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, max_results: maxResults })
                });

                const data = await response.json();
                currentScanId = data.scan_id;
                socket.emit('subscribe_scan', { scan_id: currentScanId });

            } catch (error) {
                console.error('Error:', error);
                alert('Error starting scan');
                btn.disabled = false;
                btn.textContent = '🚀 Start Analysis';
            }
        });

        async function loadResults(scanId) {
            try {
                const response = await fetch(`/api/scan-results/${scanId}`);
                const data = await response.json();

                document.getElementById('progressSection').style.display = 'none';
                document.getElementById('resultsSection').style.display = 'block';

                const btn = document.getElementById('startBtn');
                btn.disabled = false;
                btn.textContent = '🚀 Start Analysis';

                displayResults(data.competitors);

            } catch (error) {
                console.error('Error loading results:', error);
            }
        }

        function displayResults(competitors) {
            // Update stats
            const total = competitors.length;
            const avgScore = Math.round(competitors.reduce((sum, c) => sum + (parseInt(c.competitor_score) || 0), 0) / total);
            const totalTraffic = competitors.reduce((sum, c) => sum + (parseInt(c.traffic_estimate) || 0), 0);
            const totalMentions = competitors.reduce((sum, c) => sum + (parseInt(c.mention_count_total) || 0), 0);

            document.getElementById('totalCompetitors').textContent = total;
            document.getElementById('avgScore').textContent = avgScore;
            document.getElementById('totalTraffic').textContent = (totalTraffic / 1000).toFixed(0) + 'K';
            document.getElementById('totalMentions').textContent = totalMentions.toLocaleString();

            // Populate table
            const tbody = document.getElementById('resultsTable');
            tbody.innerHTML = '';
            
            competitors.forEach((comp, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td><strong>${comp.name || comp.domain}</strong></td>
                    <td>${comp.competitor_score || 0}</td>
                    <td>${(parseInt(comp.traffic_estimate) || 0).toLocaleString()}</td>
                    <td>${parseFloat(comp.g_rating) || 'N/A'} ⭐</td>
                    <td>${parseInt(comp.mention_count_total) || 0}</td>
                `;
                tbody.appendChild(tr);
            });

            // Create charts
            const top5 = competitors.slice(0, 5);
            
            // Traffic chart
            new Chart(document.getElementById('trafficChart'), {
                type: 'bar',
                data: {
                    labels: top5.map(c => c.name || c.domain),
                    datasets: [{
                        label: 'Traffic',
                        data: top5.map(c => parseInt(c.traffic_estimate) || 0),
                        backgroundColor: 'rgba(99, 102, 241, 0.6)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#e2e8f0' } } },
                    scales: {
                        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(99, 102, 241, 0.1)' } },
                        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(99, 102, 241, 0.1)' } }
                    }
                }
            });

            // Rating distribution
            const ratingBuckets = [0, 0, 0, 0, 0];
            competitors.forEach(c => {
                const rating = parseFloat(c.g_rating) || 0;
                if (rating >= 4.5) ratingBuckets[4]++;
                else if (rating >= 4.0) ratingBuckets[3]++;
                else if (rating >= 3.5) ratingBuckets[2]++;
                else if (rating >= 3.0) ratingBuckets[1]++;
                else ratingBuckets[0]++;
            });

            new Chart(document.getElementById('ratingChart'), {
                type: 'bar',
                data: {
                    labels: ['<3.0', '3.0-3.5', '3.5-4.0', '4.0-4.5', '4.5+'],
                    datasets: [{
                        label: 'Competitors',
                        data: ratingBuckets,
                        backgroundColor: 'rgba(6, 182, 212, 0.6)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#e2e8f0' } } },
                    scales: {
                        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(99, 102, 241, 0.1)' } },
                        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(99, 102, 241, 0.1)' } }
                    }
                }
            });
        }
    </script>
</body>
</html>
'''

# ============================================================================
# ROUTES
# ============================================================================

@dashboard_app.route('/')
def index():
    """Serve the dashboard (HTML is embedded above)"""
    return render_template_string(DASHBOARD_HTML)

@dashboard_app.route('/api/start-scan', methods=['POST'])
def start_scan():
    """Start a new competitor scan"""
    data = request.json
    query = data.get('query', '')
    max_results = int(data.get('max_results', 20))
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Start scan in background
    thread = threading.Thread(
        target=run_scan_background,
        args=(scan_id, query, max_results)
    )
    thread.daemon = True  # Thread will close when main program closes
    thread.start()
    
    active_scans[scan_id] = {
        'query': query,
        'max_results': max_results,
        'status': 'running',
        'progress': 0
    }
    
    return jsonify({'scan_id': scan_id, 'status': 'started'})

@dashboard_app.route('/api/scan-results/<scan_id>')
def get_scan_results(scan_id):
    """Get results of completed scan"""
    if scan_id not in scan_results:
        return jsonify({'error': 'Results not found'}), 404
    
    return jsonify(scan_results[scan_id])

# ============================================================================
# WEBSOCKET
# ============================================================================

@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'Connected'})

@socketio.on('subscribe_scan')
def handle_subscribe(data):
    scan_id = data.get('scan_id')
    if scan_id:
        join_room(scan_id)
        emit('subscribed', {'scan_id': scan_id})

# ============================================================================
# BACKGROUND SCANNER
# ============================================================================

def run_scan_background(scan_id, query, max_results):
    """Run the profiler in background - imports only when needed"""
    
    def progress_callback(message, progress):
        """Send progress updates"""
        socketio.emit('scan_progress', {
            'scan_id': scan_id,
            'message': message,
            'progress': progress
        }, room=scan_id)
        
        active_scans[scan_id]['progress'] = progress
    
    try:
        # Import your profiler here (only when running a scan)
        progress_callback('Importing profiler modules...', 5)
        
        # Try to import your existing profiler
        try:
            import final_competitor_profiler_complete as profiler
        except ImportError:
            # If that fails, try without modifications
            progress_callback('Error: Could not import profiler', 100)
            active_scans[scan_id]['status'] = 'error'
            active_scans[scan_id]['error'] = 'Profiler module not found'
            return
        
        # Initialize database if available
        db = None
        if NEON_AVAILABLE:
            try:
                db = NeonDatabaseManager()
                progress_callback('Database connected', 10)
            except:
                progress_callback('Running without database', 10)
        
        # Run search
        progress_callback('Searching Google...', 15)
        urls = profiler.google_cse_search(query, max_results)
        
        if not urls:
            active_scans[scan_id]['status'] = 'error'
            active_scans[scan_id]['error'] = 'No URLs found'
            progress_callback('Error: No URLs found', 100)
            return
        
        progress_callback(f'Found {len(urls)} URLs', 25)
        
        # Filter directories
        competitor_urls = [u for u in urls if not profiler.is_directory_url(u)]
        progress_callback(f'Processing {len(competitor_urls)} competitors', 30)
        
        # Process competitors
        competitors = []
        total = len(competitor_urls)
        
        for idx, url in enumerate(competitor_urls):
            progress = 30 + int((idx / total) * 60)
            domain = profiler.extract_domain(url)
            progress_callback(f'Processing {domain}...', progress)
            
            # Check cache if database available
            if db:
                try:
                    cached = db.get_cached_competitor(domain, max_age_days=7)
                    if cached:
                        competitors.append(dict(cached))
                        continue
                except:
                    pass
            
            # Process fresh
            try:
                result = profiler.process_competitor(url, query, db)
                if result:
                    if db:
                        try:
                            competitor_id = db.save_competitor(result)
                            result['id'] = competitor_id
                        except:
                            pass
                    competitors.append(result)
            except Exception as e:
                print(f"Error processing {domain}: {e}")
        
        # Save results
        progress_callback('Saving results...', 95)
        
        scan_results[scan_id] = {
            'query': query,
            'competitors': competitors,
            'completed_at': datetime.now().isoformat()
        }
        
        active_scans[scan_id]['status'] = 'completed'
        progress_callback('Scan complete!', 100)
        
        if db:
            db.close()
        
        # Notify completion
        socketio.emit('scan_complete', {
            'scan_id': scan_id,
            'total': len(competitors)
        }, room=scan_id)
        
    except Exception as e:
        active_scans[scan_id]['status'] = 'error'
        active_scans[scan_id]['error'] = str(e)
        progress_callback(f'Error: {str(e)}', 100)

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌌 COMPETITOR INTELLIGENCE DASHBOARD SERVER")
    print("="*70)
    print(f"📊 Dashboard URL: http://localhost:5001")
    print(f"🔧 Running on port 5001 (won't conflict with existing app.py)")
    print(f"💾 Database: {'✅ Connected' if NEON_AVAILABLE else '⚠️  Disabled'}")
    print("="*70)
    print("\nPress Ctrl+C to stop\n")
    
    # Run on port 5001 to avoid conflicts
    socketio.run(dashboard_app, debug=True, host='0.0.0.0', port=5001)
