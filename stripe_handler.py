"""
stripe_handler.py

Separate Stripe payment handler
Import this into your main app.py
"""

import os
import stripe
from flask import request, redirect, jsonify

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Price IDs from Stripe Dashboard
STRIPE_PRICES = {
    'pro': os.getenv('STRIPE_PRO_PRICE_ID', 'price_YOUR_PRO_ID'),
    'enterprise': os.getenv('STRIPE_ENTERPRISE_PRICE_ID', 'price_YOUR_ENTERPRISE_ID')
}


def create_checkout_session(plan, user_id, success_url, cancel_url):
    """
    Create Stripe checkout session
    
    Args:
        plan: 'pro' or 'enterprise'
        user_id: User identifier
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment canceled
    
    Returns:
        Stripe checkout session URL
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICES[plan],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=user_id,
            metadata={
                'plan': plan,
                'user_id': user_id
            }
        )
        
        return session.url
    
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        raise


def handle_webhook(payload, sig_header):
    """
    Handle Stripe webhook events
    
    Args:
        payload: Request body
        sig_header: Stripe-Signature header
    
    Returns:
        dict with event data or None if invalid
    """
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Invalid payload
        return None
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return None
    
    return event


def process_webhook_event(event, users_dict):
    """
    Process webhook event and update user
    
    Args:
        event: Stripe event object
        users_dict: Dictionary of users to update
    
    Returns:
        bool: True if processed successfully
    """
    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        plan = session.get('metadata', {}).get('plan', 'pro')
        
        if user_id and user_id in users_dict:
            users_dict[user_id]['plan'] = plan
            users_dict[user_id]['analyses_used'] = 0
            users_dict[user_id]['leads_used'] = 0
            users_dict[user_id]['subscription_id'] = session.get('subscription')
            
            print(f"✅ User {user_id} upgraded to {plan}")
            return True
    
    # Handle subscription cancelled
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Find user by subscription_id and downgrade to trial
        for user_id, user_data in users_dict.items():
            if user_data.get('subscription_id') == subscription['id']:
                users_dict[user_id]['plan'] = 'trial'
                users_dict[user_id]['analyses_used'] = 0
                users_dict[user_id]['leads_used'] = 0
                print(f"⚠️ User {user_id} subscription cancelled")
                return True
    
    return False


# Flask route wrappers (import these in app.py)

def add_stripe_routes(app, users):
    """
    Add Stripe routes to Flask app
    
    Usage in app.py:
        from stripe_handler import add_stripe_routes
        add_stripe_routes(app, users)
    """
    
    @app.route('/checkout', methods=['POST'])
    def checkout():
        """Create Stripe checkout"""
        plan = request.form.get('plan', 'pro')
        user_id = request.form.get('user_id') or 'guest'
        
        try:
            checkout_url = create_checkout_session(
                plan=plan,
                user_id=user_id,
                success_url=request.host_url + f'dashboard?success=true&plan={plan}',
                cancel_url=request.host_url + '?canceled=true'
            )
            
            return redirect(checkout_url, code=303)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle Stripe webhooks"""
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        
        event = handle_webhook(payload, sig_header)
        
        if not event:
            return 'Invalid signature', 400
        
        # Process event
        success = process_webhook_event(event, users)
        
        return jsonify({'status': 'success' if success else 'ignored'})
    
    
    return app
