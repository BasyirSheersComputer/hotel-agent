from dotenv import load_dotenv
import os

load_dotenv('backend/.env')
key = os.getenv('OPENAI_API_KEY', '')

print("Current OPENAI_API_KEY from .env:")
print(f"  First 40 chars: {key[:40]}")
print(f"  Last 30 chars: {key[-30:]}")
print(f"  Total length: {len(key)}")
print(f"  Contains quotes: {('\"' in key) or (\"'\" in key)}")
