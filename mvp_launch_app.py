"""
app_mvp.py - Minimal Viable Product for Launch

Complete app with:
- Pricing page
- Stripe payment
- Dashboard
- Analysis endpoint

Setup:
1. pip install flask stripe
2. Set STRIPE_SECRET_KEY in .env
3. python app_mvp.py
4. Go to http://localhost:5000
"""

from flask import Flask, render_template_string, request, redirect, session, jsonify
import stripe
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')

# Stripe setup
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')

# In-memory user store (use database in production)
users = {}
analyses = {}

# ===========================
# Landing Page
# ===========================

LANDING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Competitor Intelligence Pro</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial; margin: 0; padding: 0; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center; }
        .hero h1 { font-size: 48px; margin: 0; }
        .hero p { font-size: 20px; margin: 20px 0; }
        .cta-button { background: white; color: #667eea; padding: 15px 40px; border: none; border-radius: 25px; font-size: 18px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 20px; }
        .cta-button:hover { transform: scale(1.05); }
        .pricing { max-width: 1200px; margin: 60px auto; padding: 0 20px; }
        .pricing h2 { text-align: center; font-size: 36px; margin-bottom: 40px; }
        .plans { display: flex; gap: 30px; justify-content: center; flex-wrap: wrap; }
        .plan { border: 2px solid #e0e0e0; border-radius: 10px; padding: 40px; width: 300px; text-align: center; }
        .plan.featured { border-color: #667eea; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3); transform: scale(1.05); }
        .plan h3 { font-size: 24px; margin-bottom: 10px; }
        .plan .price { font-size: 48px; font-weight: bold; color: #667eea; }
        .plan ul { text-align: left; padding-left: 20px; line-height: 2; }
        .plan button { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 20px; width: 100%; }
        .plan button:hover { background: #5568d3; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🎯 Competitor Intelligence Pro</h1>
        <p>Find your competitors AND your customers in one platform</p>
        <p style="font-size: 16px; opacity: 0.9;">Automated competitor analysis + lead generation from Reddit & LinkedIn</p>
        <a href="#pricing" class="cta-button">View Pricing</a>
    </div>

    <div class="pricing" id="pricing">
        <h2>Simple, Transparent Pricing</h2>
        <div class="plans">
            <div class="plan">
                <h3>Pro</h3>
                <div class="price">$49<span style="font-size: 20px;">/mo</span></div>
                <ul>
                    <li>50 competitor analyses/month</li>
                    <li>250 leads generated/month</li>
                    <li>CSV exports</li>
                    <li>Email support</li>
                    <li>AI-powered insights</li>
                </ul>
                <form action="/checkout" method="POST">
                    <input type="hidden" name="plan" value="pro">
                    <button type="submit">Get Started</button>
                </form>
            </div>

            <div class="plan featured">
                <h3>Enterprise</h3>
                <div class="price">$199<span style="font-size: 20px;">/mo</span></div>
                <ul>
                    <li><strong>Unlimited</strong> analyses</li>
                    <li><strong>Unlimited</strong> leads</li>
                    <li>API access</li>
                    <li>Priority support</li>
                    <li>White-label reports</li>
                    <li>Custom integrations</li>
                </ul>
                <form action="/checkout" method="POST">
                    <input type="hidden" name="plan" value="enterprise">
                    <button type="submit">Get Started</button>
                </form>
            </div>
        </div>
    </div>

    <div style="background: #f5f5f5; padding: 40px 20px; text-align: center; margin-top: 60px;">
        <p style="color: #666;">© 2024 Competitor Intelligence Pro. All rights reserved.</p>
    </div>
</body>
</html>
"""

# ===========================
# Dashboard
# ===========================

DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Competitor Intelligence Pro</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial; margin: 0; padding: 0; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }
        .header h1 { margin: 0; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 40px; }
        .stat { background: white; padding: 30px; border-radius: 10px; flex: 1; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
        .stat .number { font-size: 36px; font-weight: bold; color: #667eea; }
        .card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .card h2 { margin-top: 0; }
        input[type="text"] { width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 16px; margin-bottom: 20px; box-sizing: border-box; }
        button { background: #667eea; color: white; padding: 15px 40px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #5568d3; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Dashboard</h1>
    </div>

    <div class="container">
        {% if success %}
        <div class="success">
            ✅ Payment successful! Your {{ plan }} plan is now active.
        </div>
        {% endif %}

        <div class="stats">
            <div class="stat">
                <h3>ANALYSES THIS MONTH</h3>
                <div class="number">{{ analyses_count }}</div>
                <p style="color: #666; margin: 5px 0 0 0;">{{ analyses_remaining }} remaining</p>
            </div>
            <div class="stat">
                <h3>LEADS GENERATED</h3>
                <div class="number">{{ leads_count }}</div>
                <p style="color: #666; margin: 5px 0 0 0;">This month</p>
            </div>
            <div class="stat">
                <h3>SUBSCRIPTION</h3>
                <div class="number" style="font-size: 24px;">{{ plan }}</div>
                <p style="color: #666; margin: 5px 0 0 0;">Active</p>
            </div>
        </div>

        <div class="card">
            <h2>🔍 Run New Analysis</h2>
            <form action="/run-analysis" method="POST">
                <input type="text" name="query" placeholder="e.g., injury attorney Ventura CA" required>
                <button type="submit">Start Analysis</button>
            </form>
        </div>

        <div class="card">
            <h2>📊 Recent Analyses</h2>
            {% if recent_analyses %}
                {% for analysis in recent_analyses %}
                <div style="padding: 15px; border-bottom: 1px solid #e0e0e0;">
                    <strong>{{ analysis.query }}</strong>
                    <span style="float: right; color: #667eea;">
                        <a href="/download/{{ analysis.id }}" style="color: #667eea; text-decoration: none;">Download CSV</a>
                    </span>
                    <br>
                    <small style="color: #666;">{{ analysis.created_at }}</small>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #666;">No analyses yet. Run your first analysis above!</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# ===========================
# Routes
# ===========================

@app.route('/')
def home():
    return LANDING_PAGE

@app.route('/checkout', methods=['POST'])
def checkout():
    """Create Stripe checkout session"""
    plan = request.form.get('plan', 'pro')
    
    # For testing, skip Stripe and go straight to dashboard
    # In production, create real Stripe session
    
    # PRODUCTION CODE (uncomment when ready):
    # prices = {
    #     'pro': 'price_YOUR_PRO_PRICE_ID',
    #     'enterprise': 'price_YOUR_ENTERPRISE_PRICE_ID'
    # }
    # 
    # session = stripe.checkout.Session.create(
    #     payment_method_types=['card'],
    #     line_items=[{'price': prices[plan], 'quantity': 1}],
    #     mode='subscription',
    #     success_url=f'{request.host_url}dashboard?success=true&plan={plan}',
    #     cancel_url=f'{request.host_url}?canceled=true',
    # )
    # return redirect(session.url)
    
    # TESTING MODE: Skip payment
    session['user_id'] = 'test_user'
    session['plan'] = plan
    return redirect(f'/dashboard?success=true&plan={plan}')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id', 'test_user')
    plan = request.args.get('plan') or session.get('plan', 'Pro')
    success = request.args.get('success') == 'true'
    
    # Get user stats
    user_analyses = [a for a in analyses.values() if a.get('user_id') == user_id]
    
    limits = {'pro': 50, 'enterprise': 999}
    analyses_remaining = limits.get(plan.lower(), 50) - len(user_analyses)
    
    return render_template_string(
        DASHBOARD,
        success=success,
        plan=plan.title(),
        analyses_count=len(user_analyses),
        analyses_remaining=max(0, analyses_remaining),
        leads_count=sum(a.get('leads_count', 0) for a in user_analyses),
        recent_analyses=sorted(user_analyses, key=lambda x: x['created_at'], reverse=True)[:5]
    )

@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    user_id = session.get('user_id', 'test_user')
    query = request.form.get('query')
    
    # Run competitor analysis
    analysis_id = f"analysis_{len(analyses) + 1}"
    output_file = f"results/{analysis_id}.csv"
    
    try:
        # Run your script
        subprocess.run([
            'python', 'final_competitor_profiler_complete.py',
            '--query', query,
            '--output', output_file
        ], check=True, timeout=300)
        
        # Also run lead generation
        subprocess.run([
            'python', 'lead_scraper.py',
            '--keywords', json.dumps([query]),
            '--output', f"results/{analysis_id}_leads.json"
        ], timeout=300)
        
        # Store analysis
        analyses[analysis_id] = {
            'id': analysis_id,
            'user_id': user_id,
            'query': query,
            'output_file': output_file,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'leads_count': 0  # Parse from results
        }
        
    except Exception as e:
        print(f"Error: {e}")
    
    return redirect('/dashboard')

@app.route('/download/<analysis_id>')
def download(analysis_id):
    """Download analysis results"""
    analysis = analyses.get(analysis_id)
    if analysis and analysis.get('user_id') == session.get('user_id'):
        from flask import send_file
        return send_file(analysis['output_file'], as_attachment=True)
    return "Not found", 404

if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    
    print("=" * 60)
    print("🚀 Competitor Intelligence Pro - MVP Launch")
    print("=" * 60)
    print("Server: http://localhost:5000")
    print("Status: Testing mode (no real payments)")
    print("=" * 60)
    
    app.run(debug=True, port=5000)
