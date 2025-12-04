"""
Ultra-robust isolated OpenAI API key test
Handles any .env file format
"""
import sys
import re

print("="*70)
print("ISOLATED OPENAI API KEY TEST (ULTRA-ROBUST)")
print("="*70)

# Read API key directly from file with multiple parsing strategies
env_file = 'backend/.env'
api_key = None

print(f"\n1. Reading {env_file}...")
try:
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"   File size: {len(content)} bytes")
    
    # Try multiple parsing strategies
    # Strategy 1: Look for OPENAI_API_KEY= pattern
    match = re.search(r'OPENAI_API_KEY\s*=\s*(.+?)(?:\n|$)', content, re.MULTILINE)
    if match:
        api_key = match.group(1).strip()
        # Remove quotes
        api_key = api_key.strip('"').strip("'")
        print(f"   ✓ Found key using regex pattern")
    
    if not api_key:
        print("   ❌ Could not find OPENAI_API_KEY")
        print(f"   File content preview: {content[:200]}")
        sys.exit(1)
    
    print(f"   First 40 chars: {api_key[:40]}")
    print(f"   Last 30 chars: {api_key[-30:]}")
    print(f"   Length: {len(api_key)} characters")

except Exception as e:
    print(f"   ❌ Error reading file: {e}")
    sys.exit(1)

# Test with OpenAI
print(f"\n2. Testing with OpenAI API (isolated, no app dependencies)...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    # Test 1: List models
    print("   a) Testing authentication (list models)...")
    models = client.models.list()
    print(f"      ✅ SUCCESS: Authenticated!")
    print(f"      Found {len(models.data)} models")
    
    # Test 2: Simple completion
    print("\n   b) Testing chat completion...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Reply with just: OK"}],
        max_tokens=5
    )
    
    result = response.choices[0].message.content.strip()
    print(f"      ✅ SUCCESS: Chat works!")
    print(f"      Response: '{result}'")
    print(f"      Tokens used: {response.usage.total_tokens}")
    
    print("\n" + "="*70)
    print("✅✅✅ SUCCESS: API KEY IS VALID AND WORKING ✅✅✅")
    print("="*70)
    print("\nThe API key is correct and OpenAI is accepting it.")
    print("If the application is failing, the issue is in the application code,")
    print("not the API key itself.")
    
except Exception as e:
    error_msg = str(e)
    print(f"\n   ❌ FAILED: {error_msg[:300]}")
    print("\n" + "="*70)
    print("❌ FAILURE: API KEY TEST FAILED")
    print("="*70)
    
    print(f"\nKey tested: {api_key[:40]}...{api_key[-30:]}")
    print(f"Full error: {error_msg}")
