import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

from app.env_utils import load_gcp_secrets

def test_secrets():
    print("Testing GCP Secret Loading...")
    
    # 1. Force clear env vars to ensure we aren't reading local cache
    keys_to_check = ["OPENAI_API_KEY", "GOOGLE_MAPS_API_KEY", "STRIPE_SECRET_KEY"]
    for key in keys_to_check:
        if key in os.environ:
            del os.environ[key]
            
    # 2. Load Secrets
    try:
        load_gcp_secrets()
    except Exception as e:
        print(f"FAILED to load secrets: {e}")
        return

    # 3. Verify
    all_good = True
    for key in keys_to_check:
        val = os.environ.get(key)
        if val:
            masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
            print(f"✓ {key} loaded: {masked}")
        else:
            # STRIPE might not be in the secret yet, so optional warning
            if key == "STRIPE_SECRET_KEY":
                print(f"⚠ {key} not found (might be optional for now)")
            else:
                print(f"✗ {key} MISSING")
                all_good = False
    
    if all_good:
        print("\nSUCCESS: Critical secrets loaded from GCP.")
    else:
        print("\nFAILURE: Missing critical secrets.")

if __name__ == "__main__":
    test_secrets()
