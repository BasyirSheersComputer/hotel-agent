"""
Diagnose .env file formatting
Check for hidden characters, quotes, spaces, etc.
"""
import os

print("="*70)
print("DIAGNOSING .ENV FILE")
print("="*70)

# Read the .env file directly
env_path = 'backend/.env'
print(f"\nReading file: {env_path}")

with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}\n")

for i, line in enumerate(lines, 1):
    if 'OPENAI_API_KEY' in line:
        print(f"Line {i} (OPENAI_API_KEY):")
        print(f"  Raw line: {repr(line)}")
        print(f"  Length: {len(line)} characters")
        
        # Parse the key
        if '=' in line:
            key_part = line.split('=', 1)[1]
            key_part = key_part.strip()
            
            # Check for quotes
            if key_part.startswith('"') and key_part.endswith('"'):
                print(f"  ⚠️  Key is wrapped in double quotes")
                key_part = key_part[1:-1]
            elif key_part.startswith("'") and key_part.endswith("'"):
                print(f"  ⚠️  Key is wrapped in single quotes")
                key_part = key_part[1:-1]
            
            print(f"  Extracted key: {key_part[:35]}...{key_part[-25:]}")
            print(f"  Key length: {len(key_part)}")
            
            # Check for whitespace
            if key_part != key_part.strip():
                print(f"  ⚠️  Key has leading/trailing whitespace")
            
            # Check for newlines
            if '\n' in key_part or '\r' in key_part:
                print(f"  ⚠️  Key contains newline characters")
            
            # Test this exact key
            print(f"\n  Testing this exact key with OpenAI...")
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_part)
                models = client.models.list()
                print(f"  ✅ SUCCESS: Key works!")
            except Exception as e:
                print(f"  ❌ FAILED: {str(e)[:100]}")

print("\n" + "="*70)

# Now test with dotenv
print("\nTesting with python-dotenv:")
from dotenv import load_dotenv
load_dotenv(env_path)
dotenv_key = os.getenv('OPENAI_API_KEY')
print(f"  Key from dotenv: {dotenv_key[:35] if dotenv_key else 'NOT FOUND'}...{dotenv_key[-25:] if dotenv_key else ''}")
print(f"  Length: {len(dotenv_key) if dotenv_key else 0}")

if dotenv_key:
    print(f"\n  Testing dotenv key with OpenAI...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=dotenv_key)
        models = client.models.list()
        print(f"  ✅ SUCCESS: Key works!")
    except Exception as e:
        print(f"  ❌ FAILED: {str(e)[:100]}")

print("="*70)
