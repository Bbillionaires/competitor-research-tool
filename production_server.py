# ==========================================
# PRODUCTION WEB SERVER WITH PAYMENT SYSTEM
# Flask + Stripe + User Authentication
# ==========================================

"""
TECH STACK:
- Flask: Web framework
- SQLite/PostgreSQL: Database
- Stripe: Payment processing
- Flask-Login: User authentication
- Tailwind: Dark space UI

FOLDER STRUCTURE:
competitor-intelligence/
├── app.py                 # Main Flask app
├── database_manager.py    # From previous artifact
├── smart_profiler.py      # Enhanced profiler
├── requirements.txt       # Python dependencies
├── .env                   # Secret keys
├── templates/
│   ├── index.html        # Landing page
│   ├── dashboard.html    # Space UI dashboard
│   ├── login.html        # Login page
│   └── pricing.html      # Pricing plans
└── static/
    ├── css/
    └── js/
"""

# ==========================================
# FILE 1: app.py (Main Flask Application)
# ==========================================

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import os
from datetime import datetime, timedelta
from database_manager import CompetitorDatabase

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database
db = CompetitorDatabase()

# ==========================================
# User Model
# ==========================================

class User(UserMixin):
    def __init__(self, id, email, plan='free', stripe_customer_id=None):
        self.id = id
        self.email = email
        self.plan = plan
        self.stripe_customer_id = stripe_customer_id
    
    def get_plan_limits(self):
        """Get limits based on subscription plan"""
        limits = {
            'free': {
                'searches_per_month': 1,
                'competitors_per_search': 10,
                'data_retention_days': 7,
                'api_access': False
            },
            'pro': {
                'searches_per_month': 10,
                'competitors_per_search': 50,
                'data_retention_days': 30,
                'api_access': False
            },
            'business': {
                'searches_per_month': 100,
                'competitors_per_search': 200,
                'data_retention_days': 90,
                'api_access': True
            },
            'enterprise': {
                'searches_per_month': 'unlimited',
                'competitors_per_search': 'unlimited',
                'data_retention_days': 365,
                'api_access': True
            }
        }
        return limits.get(self.plan, limits['free'])

@login_manager.user_loader
def load_user(user_id):
    # Load user from database
    # This is simplified - implement full user database
    return User(id=user_id, email=f"user{user_id}@example.com", plan='free')


# ==========================================
# Routes
# ==========================================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - Space UI"""
    # Get user's recent searches
    competitors = db.get_all_competitors(limit=50)
    
    return render_template('dashboard.html', 
                         user=current_user,
                         competitors=competitors,
                         stripe_key=STRIPE_PUBLISHABLE_KEY)


@app.route('/api/search', methods=['POST'])
@login_required
def api_search():
    """Run competitor search"""
    data = request.get_json()
    query = data.get('query')
    force_refresh = data.get('force_refresh', False)
    
    # Check user limits
    limits = current_user.get_plan_limits()
    
    # TODO: Check if user has searches remaining this month
    
    # Run search (async in production)
    from smart_profiler import process_competitor_smart, google_cse_search
    
    urls = google_cse_search(query, max_results=limits['competitors_per_search'])
    
    results = []
    for url in urls:
        row = process_competitor_smart(url, query, db, force_refresh)
        if row:
            results.append(row)
    
    return jsonify({
        'success': True,
        'competitors': results,
        'count': len(results)
    })


@app.route('/api/competitor/<domain>')
@login_required
def api_get_competitor(domain):
    """Get single competitor details"""
    competitor = db.get_competitor(domain, max_age_days=30)
    
    if competitor:
        return jsonify({'success': True, 'data': competitor})
    else:
        return jsonify({'success': False, 'error': 'Not found'}), 404


@app.route('/pricing')
def pricing():
    """Pricing page"""
    plans = {
        'pro': {
            'name': 'Pro',
            'price': 99,
            'stripe_price_id': os.getenv('STRIPE_PRICE_ID_PRO'),
            'features': [
                '10 searches per month',
                '50 competitors per search',
                'All 74 data points',
                '30-day data retention',
                'Priority support'
            ]
        },
        'business': {
            'name': 'Business',
            'price': 299,
            'stripe_price_id': os.getenv('STRIPE_PRICE_ID_BUSINESS'),
            'features': [
                '100 searches per month',
                '200 competitors per search',
                'Advanced analytics',
                '90-day data retention',
                'API access',
                'White-label reports',
                '24/7 support'
            ]
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': 999,
            'stripe_price_id': os.getenv('STRIPE_PRICE_ID_ENTERPRISE'),
            'features': [
                'Unlimited searches',
                'Unlimited competitors',
                'Custom integrations',
                '1-year data retention',
                'Full API access',
                'Dedicated account manager',
                'Custom features'
            ]
        }
    }
    
    return render_template('pricing.html', plans=plans, stripe_key=STRIPE_PUBLISHABLE_KEY)


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    data = request.get_json()
    price_id = data.get('price_id')
    
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('pricing', _external=True),
        )
        
        return jsonify({'sessionId': checkout_session.id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/subscription-success')
@login_required
def subscription_success():
    """Handle successful subscription"""
    session_id = request.args.get('session_id')
    
    if session_id:
        # Verify session and update user plan
        session = stripe.checkout.Session.retrieve(session_id)
        
        # TODO: Update user's plan in database
        
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('pricing'))


@app.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook handler"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Update user subscription
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Downgrade user to free
    
    return jsonify({'success': True})


@app.route('/api/usage')
@login_required
def api_usage():
    """Get current API usage stats"""
    usage_stats = {
        'google_places': db.get_api_usage('google_places'),
        'openpagerank': db.get_api_usage('openpagerank'),
        'hunter_io': db.get_api_usage('hunter_io'),
        'pagespeed_insights': db.get_api_usage('pagespeed_insights'),
    }
    
    return jsonify(usage_stats)


# ==========================================
# FILE 2: requirements.txt
# ==========================================

"""
Create file: requirements.txt

Flask==3.0.0
flask-login==0.6.3
stripe==7.0.0
python-dotenv==1.0.0
beautifulsoup4==4.12.2
requests==2.31.0
papaparse==5.4.1
gunicorn==21.2.0
"""


# ==========================================
# FILE 3: .env (Environment Variables)
# ==========================================

"""
Create file: .env

# Flask
FLASK_SECRET_KEY=your-super-secret-key-here-change-this
FLASK_ENV=production

# Stripe (Get from stripe.com/dashboard)
STRIPE_SECRET_KEY=sk_live_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Stripe Price IDs (created in Stripe Dashboard)
STRIPE_PRICE_ID_PRO=price_pro_monthly_id
STRIPE_PRICE_ID_BUSINESS=price_business_monthly_id
STRIPE_PRICE_ID_ENTERPRISE=price_enterprise_monthly_id

# API Keys (same as before)
GOOGLE_CSE_API_KEY=your_key
GOOGLE_CSE_ID=your_id
GOOGLE_PLACES_API_KEY=your_key
GOOGLE_PAGESPEED_API_KEY=your_key
HUNTER_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
OPENPAGERANK_API_KEY=your_key

# Database
DATABASE_URL=sqlite:///competitors.db
# For production: DATABASE_URL=postgresql://user:pass@host/dbname
"""


# ==========================================
# DEPLOYMENT INSTRUCTIONS
# ==========================================

"""
LOCAL TESTING:
1. Install dependencies: pip install -r requirements.txt
2. Set up .env file with your keys
3. Run: python app.py
4. Visit: http://localhost:5000

PRODUCTION DEPLOYMENT (Recommended: Railway.app or Render.com):

1. Railway.app (Easiest):
   - Connect GitHub repo
   - Add environment variables
   - Auto-deploys on push
   - $5/month

2. Render.com (Free tier available):
   - Connect GitHub repo
   - Add environment variables
   - Free tier with limitations

3. AWS/DigitalOcean (Most control):
   - Set up EC2/Droplet
   - Install dependencies
   - Configure nginx + gunicorn
   - $10-50/month depending on traffic

STRIPE SETUP:
1. Create account at stripe.com
2. Create products for each plan in Dashboard
3. Copy Price IDs to .env
4. Set up webhook endpoint: /webhook
5. Test with test mode keys first
"""


# ==========================================
# RUN COMMAND
# ==========================================

if __name__ == '__main__':
    # Development
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    # Production (use gunicorn instead)
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app