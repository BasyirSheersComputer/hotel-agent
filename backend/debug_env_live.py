import os
from dotenv import load_dotenv

load_dotenv("h:/Source/repos/hotel-agent/backend/.env")

key = os.getenv("STRIPE_SECRET_KEY")
print(f"Stripe Key Length: {len(key) if key else 0}")
print(f"Stripe Key Prefix: {key[:7] if key else 'None'}")

openai_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI Key Length: {len(openai_key) if openai_key else 0}")
print(f"OpenAI Key Prefix: {openai_key[:7] if openai_key else 'None'}")
