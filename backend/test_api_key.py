"""
Test if OpenAI API key works
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("=" * 60)
print("TESTING OPENAI API KEY")
print("=" * 60)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("\nERROR: No API key found!")
    exit(1)

print(f"\nKey loaded: {api_key[:10]}...{api_key[-5:]}")
print(f"Length: {len(api_key)}")

print("\nTesting API connection...")
try:
    client = OpenAI(api_key=api_key)
    # Try a simple test
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="test"
    )
    print("✓ API key is VALID!")
    print(f"✓ Successfully created embedding (dim: {len(response.data[0].embedding)})")
except Exception as e:
    print(f"✗ API key test FAILED!")
    print(f"Error: {e}")

print("\n" + "=" * 60)
