import requests
import os

# Backend URL
BASE_URL = "http://localhost:8000"

def test_checkout():
    # Login to get token (if needed, but for now we might mock or use a known user)
    # Actually, let's assume we can hit it if we have a valid token or if we mock it.
    # The current auth setup might require a valid user. 
    # Let's try to just hit the endpoint. If 401, we know it's protected.
    
    # We'll use a hardcoded token if we have one, or try to register/login quickly.
    # For now, let's try to verify the keys are loaded first (already done).
    
    # Let's try to create a checkout session.
    # We need a token.
    # Let's use the 'verify_token' bypass if possible, or just generate a raw request.
    pass

import stripe
from dotenv import load_dotenv
load_dotenv("h:/Source/repos/hotel-agent/backend/.env")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
price_id = os.getenv("STRIPE_PRICE_ID_PRO")

try:
    print(f"Testing Stripe Connection...")
    print(f"Price ID: {price_id}")
    
    # Create a session manually to verify keys work
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url="http://localhost:3000/success",
        cancel_url="http://localhost:3000/cancel",
    )
    print(f"SUCCESS: Generated Session URL: {session.url}")
except Exception as e:
    print(f"ERROR: {e}")
