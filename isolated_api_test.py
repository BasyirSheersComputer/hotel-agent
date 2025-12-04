"""
Completely isolated OpenAI API key test
No dependencies on application code, dotenv, or any other modules
"""
import sys

# Read the .env file manually
print("="*70)
print("ISOLATED OPENAI API KEY TEST")
print("="*70)

# Read API key directly from file
env_file = 'backend/.env'
api_key = None

print(f"\n1. Reading {env_file} manually...")
with open(env_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('OPENAI_API_KEY='):
            api_key = line.split('=', 1)[1]
            # Remove quotes if present
            api_key = api_key.strip('"').strip("'")
            break

if not api_key:
    print("❌ ERROR: Could not find OPENAI_API_KEY in .env file")
    sys.exit(1)

print(f"   ✓ Found key")
print(f"   First 40 chars: {api_key[:40]}")
print(f"   Last 30 chars: {api_key[-30:]}")
print(f"   Length: {len(api_key)} characters")
has_quotes = ('"' in api_key) or ("'" in api_key)
print(f"   Has quotes: {has_quotes}")

# Test with OpenAI
print(f"\n2. Testing with OpenAI API...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    # Test 1: List models
    print("   Testing authentication...")
    models = client.models.list()
    print(f"   ✅ Authentication successful!")
    print(f"   Found {len(models.data)} models")
    
    # Test 2: Simple completion
    print("\n   Testing chat completion...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'working' in one word"}],
        max_tokens=5
    )
    
    result = response.choices[0].message.content.strip()
    print(f"   ✅ Chat completion successful!")
    print(f"   Response: '{result}'")
    print(f"   Tokens: {response.usage.total_tokens}")
    
    print("\n" + "="*70)
    print("✅ SUCCESS: API KEY IS VALID AND WORKING")
    print("="*70)
    
except Exception as e:
    error_msg = str(e)
    print(f"\n   ❌ FAILED: {error_msg[:200]}")
    print("\n" + "="*70)
    print("❌ FAILURE: API KEY TEST FAILED")
    print("="*70)
    
    if "401" in error_msg or "Incorrect API key" in error_msg:
        print("\n⚠️  Authentication Error Details:")
        print(f"   The key being tested: {api_key[:40]}...{api_key[-30:]}")
        print(f"   Error: {error_msg}")
        print("\n   This means OpenAI's servers are rejecting this specific key.")
    else:
        print(f"\n   Full error: {e}")
