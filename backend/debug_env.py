"""
Debug script to check if .env is being loaded correctly
"""
import os
from app.env_utils import load_env_robustly

# Check if .env file exists
env_path = os.path.join(os.path.dirname(__file__), ".env")
print(f"\n1. .env file exists: {os.path.exists(env_path)}")
print(f"   Path: {env_path}")

# Load dotenv
load_env_robustly()

# Check if keys are loaded
openai_key = os.getenv("OPENAI_API_KEY")
maps_key = os.getenv("GOOGLE_MAPS_API_KEY")

print(f"\n2. OPENAI_API_KEY loaded: {openai_key is not None}")
if openai_key:
    print(f"   First 10 chars: {openai_key[:10]}...")
    print(f"   Last 5 chars: ...{openai_key[-5:]}")
    print(f"   Total length: {len(openai_key)}")
else:
    print("   KEY IS MISSING!")

print(f"\n3. GOOGLE_MAPS_API_KEY loaded: {maps_key is not None}")
if maps_key:
    print(f"   First 10 chars: {maps_key[:10]}...")
    print(f"   Total length: {len(maps_key)}")

print("\n" + "=" * 60)
