import os
import re
from pathlib import Path
from dotenv import load_dotenv

from google.cloud import secretmanager
import warnings

SECRET_RESOURCE_ID = "projects/319072304914/secrets/hotel-agent-secret-001/versions/latest"

def load_gcp_secrets():
    """
    Load secrets from Google Cloud Secret Manager.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": SECRET_RESOURCE_ID})
        payload = response.payload.data.decode("utf-8-sig")
        
        print(f"Loaded secrets from GCP: {SECRET_RESOURCE_ID}")
        
        # Parse like .env
        for line in payload.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")
                
    except Exception as e:
        print(f"Warning: Could not load GCP secrets: {e}")

def load_env_robustly():
    """
    Load .env file from multiple potential locations.
    """
    
    current_file = Path(__file__).resolve()
    
    # Potential paths to check:
    backend_env = current_file.parent.parent / '.env'
    cwd_backend_env = Path.cwd() / 'backend' / '.env'
    cwd_env = Path.cwd() / '.env'
    
    paths_to_check = [backend_env, cwd_backend_env, cwd_env]
    
    for path in paths_to_check:
        if path.exists() and path.is_file():
            # Read and parse file manually for robustness
            try:
                with open(path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # Parse KEY=value patterns
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")
                
                print(f"Loaded .env from {path}")
            except Exception as e:
                print(f"Warning: Failed to parse {path}: {e}")
                continue
    
    # Fallback to load_dotenv default behavior
    load_dotenv(override=True)
    
    # Load GCP secrets LAST to ensure they override local .env
    load_gcp_secrets()

def get_direct_env_value(key_name: str) -> str | None:
    """
    Directly read a key from the .env file, bypassing os.environ.
    This ensures we get the exact value in the file, ignoring shell variables.
    """
    current_file = Path(__file__).resolve()
    # Prioritize backend/.env
    paths_to_check = [
        current_file.parent.parent / '.env',
        Path.cwd() / 'backend' / '.env',
        Path.cwd() / '.env'
    ]

    for path in paths_to_check:
        if path.exists() and path.is_file():
            try:
                with open(path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == key_name:
                            return v.strip().strip('"').strip("'")
            except Exception as e:
                print(f"Error reading {path}: {e}")
                continue
    
    # Fallback to os.getenv if not found in file
    return os.environ.get(key_name)
