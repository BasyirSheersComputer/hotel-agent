"""
Standalone OpenAI API Key Test
Tests the API key directly without any application dependencies
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv('backend/.env')

# Get the API key
api_key = os.getenv('OPENAI_API_KEY')

print("="*70)
print("STANDALONE OPENAI API KEY TEST")
print("="*70)

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY not found in .env file")
    exit(1)

print(f"✓ API Key loaded from .env")
print(f"  Starts with: {api_key[:35]}")
print(f"  Ends with: {api_key[-25:]}")
print(f"  Length: {len(api_key)} characters")
print()

# Test with OpenAI API directly
print("Testing API key with OpenAI servers...")
print("-"*70)

try:
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    # Simple test: List models (lightweight API call)
    print("1. Testing authentication (listing models)...")
    models = client.models.list()
    print(f"   ✅ SUCCESS: Authentication successful")
    print(f"   Available models: {len(models.data)} models found")
    
    # Test actual completion
    print("\n2. Testing chat completion...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'API key is working' in exactly 4 words"}
        ],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"   ✅ SUCCESS: Chat completion received")
    print(f"   Response: {result}")
    print(f"   Tokens used: {response.usage.total_tokens}")
    
    print("\n" + "="*70)
    print("✅ OPENAI API KEY IS VALID AND WORKING")
    print("="*70)
    
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    print("\n" + "="*70)
    print("❌ OPENAI API KEY TEST FAILED")
    print("="*70)
    print(f"\nError details: {e}")
    
    # Check if it's an authentication error
    if "401" in str(e) or "Incorrect API key" in str(e):
        print("\n⚠️  This is an authentication error.")
        print("The API key is being rejected by OpenAI's servers.")
        print("\nPlease verify:")
        print("  1. The key is active in your OpenAI dashboard")
        print("  2. Your account has available credits")
        print("  3. The key hasn't been revoked")
