"""
app.py - Main Launch App (Clean Version)

Stripe payment handling is in stripe_handler.py (separate file)
"""

from flask import Flask, request, redirect, session
import os
import subprocess
from datetime import datetime

# Import Stripe handler
from stripe_handler import add_stripe_routes

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-me')

# Simple in-memory storage (use database in production)
users = {}

# Usage limits
TRIAL_LIMITS = {'analyses': 2, 'leads': 15}
PRO_LIMITS = {'analyses': 50, 'leads': 250}
ENTERPRISE_LIMITS = {'analyses': 999999, 'leads': 999999}


def get_user():
    """Get or create user session"""
    user_id = session.get('user_id')
    if not user_id:
        user_id = f"user_{len(users) + 1}"
        session['user_id'] = user_id
        users[user_id] = {
            'plan': 'trial',
            'analyses_used': 0,
            'leads_used': 0,
            'created_at': datetime.now().isoformat()
        }
    return user_id, users.get(user_id, users[user_id])


def check_usage_limit(user_data, action='analysis'):
    """Check if user has usage remaining"""
    plan = user_data.get('plan', 'trial')
    
    if plan == 'trial':
        limits = TRIAL_LIMITS
    elif plan == 'pro':
        limits = PRO_LIMITS
    else:
        limits = ENTERPRISE_LIMITS
    
    if action == 'analysis':
        return user_data['analyses_used'] < limits['analyses']
    return user_data['leads_used'] < limits['leads']


# Add Stripe routes (from separate file)
add_stripe_routes(app, users)


# ===========================
# Landing Page
# ===========================

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Competitor Intelligence Pro</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
            
            .hero { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 100px 20px; 
                text-align: center; 
            }
            .hero h1 { font-size: 48px; margin-bottom: 20px; }
            .hero p { font-size: 20px; opacity: 0.95; max-width: 600px; margin: 0 auto; }
            
            .cta { 
                background: white; 
                color: #667eea; 
                padding: 18px 50px; 
                border-radius: 30px; 
                text-decoration: none; 
                display: inline-block; 
                margin-top: 40px; 
                font-weight: bold; 
                font-size: 18px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .cta:hover { transform: translateY(-2px); }
            
            .features {
                max-width: 1000px;
                margin: 80px auto;
                padding: 0 20px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 40px;
            }
            .feature {
                text-align: center;
                padding: 30px;
            }
            .feature h3 { color: #667eea; margin: 20px 0 10px; }
            
            .pricing { 
                max-width: 1200px; 
                margin: 80px auto; 
                padding: 0 20px; 
            }
            .pricing h2 { 
                text-align: center; 
                font-size: 36px; 
                margin-bottom: 50px; 
            }
            
            .plans { 
                display: flex; 
                gap: 30px; 
                justify-content: center; 
                flex-wrap: wrap; 
            }
            
            .plan { 
                background: white; 
                border: 2px solid #e0e0e0; 
                border-radius: 15px; 
                padding: 40px; 
                width: 320px; 
                box-shadow: 0 5px 20px rgba(0,0,0,0.1); 
            }
            .plan.featured { 
                border-color: #667eea; 
                transform: scale(1.05); 
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
            }
            
            .plan h3 { font-size: 24px; margin-bottom: 10px; }
            .price { 
                font-size: 48px; 
                font-weight: bold; 
                color: #667eea; 
                margin: 20px 0; 
            }
            .price span { font-size: 20px; }
            
            .plan ul { 
                list-style: none; 
                text-align: left; 
                margin: 30px 0; 
            }
            .plan li { 
                padding: 10px 0; 
                border-bottom: 1px solid #f0f0f0; 
            }
            .plan li:before { 
                content: "✓ "; 
                color: #667eea; 
                font-weight: bold; 
            }
            
            .plan button { 
                background: #667eea; 
                color: white; 
                width: 100%; 
                padding: 15px; 
                border: none; 
                border-radius: 8px; 
                font-size: 16px; 
                cursor: pointer; 
                font-weight: bold; 
            }
            .plan button:hover { background: #5568d3; }
            
            .trial-badge {
                background: #ffd700;
                color: #333;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                display: inline-block;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>🎯 Competitor Intelligence Pro</h1>
            <p>Find your competitors AND your customers in one powerful platform</p>
            <p style="font-size: 16px; margin-top: 20px;">Automated competitor analysis + lead generation from Reddit & LinkedIn</p>
            <a href="#pricing" class="cta">Start Free Trial →</a>
        </div>

        <div class="features">
            <div class="feature">
                <div style="font-size: 48px;">🔍</div>
                <h3>Competitor Analysis</h3>
                <p>Discover who you're competing against with AI-powered insights</p>
            </div>
            <div class="feature">
                <div style="font-size: 48px;">📧</div>
                <h3>Lead Generation</h3>
                <p>Find potential customers actively looking for your services</p>
            </div>
            <div class="feature">
                <div style="font-size: 48px;">📊</div>
                <h3>Detailed Reports</h3>
                <p>Get CSV exports with 60+ data points per competitor</p>
            </div>
        </div>

        <div class="pricing" id="pricing">
            <h2>Simple Pricing</h2>
            
            <div class="plans">
                <div class="plan">
                    <div class="trial-badge">FREE TRIAL</div>
                    <h3>Trial</h3>
                    <div class="price">$0</div>
                    <ul>
                        <li>2 competitor analyses</li>
                        <li>15 leads generated</li>
                        <li>All features unlocked</li>
                        <li>No credit card required</li>
                    </ul>
                    <form action="/start-trial" method="POST">
                        <button type="submit">Start Free Trial</button>
                    </form>
                </div>

                <div class="plan">
                    <h3>Pro</h3>
                    <div class="price">$49<span>/mo</span></div>
                    <ul>
                        <li>50 analyses per month</li>
                        <li>250 leads per month</li>
                        <li>CSV exports</li>
                        <li>AI insights included</li>
                        <li>Email support</li>
                    </ul>
                    <form action="/checkout" method="POST">
                        <input type="hidden" name="plan" value="pro">
                        <button type="submit">Subscribe Now</button>
                    </form>
                </div>

                <div class="plan featured">
                    <h3>Enterprise</h3>
                    <div class="price">$199<span>/mo</span></div>
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
                        <button type="submit">Subscribe Now</button>
                    </form>
                </div>
            </div>
        </div>

        <div style="background: #f5f5f5; padding: 40px 20px; text-align: center; margin-top: 80px;">
            <p style="color: #666;">© 2024 Competitor Intelligence Pro. All rights reserved.</p>
        </div>
    </body>
    </html>
    """


# ===========================
# Start Trial (No Payment)
# ===========================

@app.route('/start-trial', methods=['POST'])
def start_trial():
    """Start free trial - no payment required"""
    get_user()  # Creates user session
    return redirect('/dashboard?welcome=true')


# ===========================
# Dashboard
# ===========================

@app.route('/dashboard')
def dashboard():
    user_id, user_data = get_user()
    
    plan = request.args.get('plan') or user_data.get('plan', 'trial')
    welcome = request.args.get('welcome') == 'true'
    success = request.args.get('success') == 'true'
    
    # Update plan if payment successful
    if success and plan in ['pro', 'enterprise']:
        users[user_id]['plan'] = plan
        users[user_id]['analyses_used'] = 0
        users[user_id]['leads_used'] = 0
    
    # Get limits for user's plan
    if user_data['plan'] == 'trial':
        limits = TRIAL_LIMITS
    elif user_data['plan'] == 'pro':
        limits = PRO_LIMITS
    else:
        limits = ENTERPRISE_LIMITS
    
    analyses_remaining = limits['analyses'] - user_data['analyses_used']
    leads_remaining = limits['leads'] - user_data['leads_used']
    
    # Show upgrade prompt if trial exhausted
    show_upgrade = (user_data['plan'] == 'trial' and 
                    (analyses_remaining <= 0 or leads_remaining <= 0))
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Competitor Intelligence Pro</title>
        <style>
            body {{ font-family: Arial; margin: 0; background: #f5f7fa; }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 30px; 
            }}
            .header h1 {{ margin: 0; }}
            .header .plan-badge {{ 
                display: inline-block; 
                background: rgba(255,255,255,0.2); 
                padding: 5px 15px; 
                border-radius: 20px; 
                font-size: 14px; 
                margin-top: 10px;
            }}
            
            .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
            
            .alert {{ 
                padding: 20px; 
                border-radius: 8px; 
                margin-bottom: 30px; 
            }}
            .alert.success {{ background: #d4edda; color: #155724; }}
            .alert.warning {{ background: #fff3cd; color: #856404; }}
            .alert.upgrade {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                text-align: center;
            }}
            .alert a {{ color: white; text-decoration: underline; }}
            
            .stats {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin-bottom: 40px; 
            }}
            .stat {{ 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            }}
            .stat h3 {{ margin: 0 0 10px 0; color: #666; font-size: 14px; }}
            .stat .number {{ font-size: 36px; font-weight: bold; color: #667eea; }}
            .stat .label {{ color: #999; margin-top: 5px; font-size: 14px; }}
            
            .card {{ 
                background: white; 
                padding: 40px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                margin-bottom: 30px; 
            }}
            .card h2 {{ margin-top: 0; }}
            
            input[type="text"] {{ 
                width: 100%; 
                padding: 15px; 
                border: 2px solid #e0e0e0; 
                border-radius: 5px; 
                font-size: 16px; 
                margin-bottom: 20px; 
                box-sizing: border-box;
            }}
            
            button {{ 
                background: #667eea; 
                color: white; 
                padding: 15px 40px; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 16px; 
                font-weight: bold;
            }}
            button:hover {{ background: #5568d3; }}
            button:disabled {{ 
                background: #ccc; 
                cursor: not-allowed; 
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Dashboard</h1>
            <div class="plan-badge">{user_data['plan'].upper()} PLAN</div>
        </div>

        <div class="container">
            {'<div class="alert success">✅ Welcome! Your free trial has started. No credit card required.</div>' if welcome else ''}
            {'<div class="alert success">✅ Payment successful! Your subscription is now active.</div>' if success else ''}
            
            {f'<div class="alert upgrade">⚠️ Trial Exhausted! <a href="/#pricing">Upgrade to Pro ($49/mo)</a> to continue using the platform.</div>' if show_upgrade else ''}
            
            <div class="stats">
                <div class="stat">
                    <h3>ANALYSES THIS MONTH</h3>
                    <div class="number">{user_data['analyses_used']}</div>
                    <div class="label">{analyses_remaining} remaining</div>
                </div>
                <div class="stat">
                    <h3>LEADS GENERATED</h3>
                    <div class="number">{user_data['leads_used']}</div>
                    <div class="label">{leads_remaining} remaining</div>
                </div>
                <div class="stat">
                    <h3>PLAN</h3>
                    <div class="number" style="font-size: 24px;">{user_data['plan'].title()}</div>
                    <div class="label">Active</div>
                </div>
            </div>

            <div class="card">
                <h2>🔍 Run Competitor Analysis</h2>
                <form action="/run-analysis" method="POST">
                    <input type="text" name="query" placeholder="e.g., injury attorney Ventura CA" required {'disabled' if analyses_remaining <= 0 else ''}>
                    <button type="submit" {'disabled' if analyses_remaining <= 0 else ''}>
                        {'Upgrade to Continue' if analyses_remaining <= 0 else 'Start Analysis'}
                    </button>
                </form>
                {f'<p style="color: #856404; margin-top: 10px;">⚠️ No analyses remaining. <a href="/#pricing">Upgrade now</a></p>' if analyses_remaining <= 0 else ''}
            </div>
        </div>
    </body>
    </html>
    """


# ===========================
# Run Analysis
# ===========================

@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    user_id, user_data = get_user()
    
    # Check usage limit
    if not check_usage_limit(user_data, 'analysis'):
        return redirect('/dashboard?error=limit_reached')
    
    query = request.form.get('query')
    
    # Run your competitor profiler
    try:
        # Use subprocess to call your existing script
        result = subprocess.run([
            'python', 'final_competitor_profiler_complete.py'
        ], input=f"{query}\n20\n", text=True, capture_output=True, timeout=300)
        
        # Increment usage
        users[user_id]['analyses_used'] += 1
        
        # Redirect to results
        return redirect('/results?file=competitors_final_profile.csv')
    
    except Exception as e:
        print(f"Error: {e}")
        return f"Error running analysis: {e}", 500


# ===========================
# Results Page
# ===========================

@app.route('/results')
def results():
    filename = request.args.get('file', 'competitors_final_profile.csv')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analysis Complete</title>
        <style>
            body {{ font-family: Arial; margin: 0; background: #f5f7fa; }}
            .container {{ max-width: 800px; margin: 100px auto; padding: 40px; background: white; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); text-align: center; }}
            h1 {{ color: #667eea; }}
            .success-icon {{ font-size: 80px; margin-bottom: 20px; }}
            button {{ background: #667eea; color: white; padding: 15px 40px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }}
            button:hover {{ background: #5568d3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✅</div>
            <h1>Analysis Complete!</h1>
            <p>Your competitor analysis is ready.</p>
            <a href="/download/{filename}"><button>Download CSV Report</button></a>
            <a href="/dashboard"><button style="background: #28a745;">Run Another Analysis</button></a>
        </div>
    </body>
    </html>
    """


@app.route('/download/<filename>')
def download(filename):
    """Download results file"""
    from flask import send_file
    return send_file(filename, as_attachment=True)


# ===========================
# Run Server
# ===========================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Competitor Intelligence Pro - Live Launch")
    print("=" * 60)
    print("Server: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)
