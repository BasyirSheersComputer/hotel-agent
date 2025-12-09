import os
import stripe
from app.config.settings import DEMO_MODE

# Load keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
# Demo Price IDs (Replace with real ones in prod)
PRICE_ID_PRO = os.getenv("STRIPE_PRICE_ID_PRO", "price_mock_pro")
PRICE_ID_ENTERPRISE = os.getenv("STRIPE_PRICE_ID_ENTERPRISE", "price_mock_enterprise")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

class BillingService:
    @staticmethod
    def get_checkout_url(org_id: str, plan_id: str, success_url: str, cancel_url: str):
        """
        Generate Stripe Checkout URL.
        If NO API Key, returns a Mock URL (for dev).
        """
        if not STRIPE_SECRET_KEY:
            # MOCK MODE
            return f"{success_url}?session_id=mock_session_{plan_id}"
            
        print(f"BillingService: Creating checkout for {org_id} plan {plan_id}")
        
        price_id = PRICE_ID_PRO if plan_id == "pro" else PRICE_ID_ENTERPRISE
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                client_reference_id=str(org_id),
                metadata={
                    "org_id": str(org_id),
                    "plan": plan_id
                }
            )
            return session.url
        except Exception as e:
            print(f"Stripe Error: {e}")
            raise e

    @staticmethod
    def get_portal_url(stripe_customer_id: str, return_url: str):
        """
        Generate Customer Portal URL.
        """
        if not STRIPE_SECRET_KEY:
            return return_url # Mock return
            
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url
        )
        return session.url

    @staticmethod
    def handle_webhook(payload, sig_header):
        """
        Verify and parse webhook payload.
        """
        if not STRIPE_SECRET_KEY:
            # In mock mode, payload IS the event dict
            return payload
            
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        return event
