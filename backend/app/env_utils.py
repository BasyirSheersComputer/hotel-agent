import os
import re
from pathlib import Path
from dotenv import load_dotenv

def load_env_robustly():
    """
    Load .env file from multiple potential locations.
    Uses manual parsing as fallback if load_dotenv fails.
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
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse KEY=value patterns
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
                return
            except Exception as e:
                print(f"Warning: Failed to parse {path}: {e}")
                continue
    
    # Fallback to load_dotenv default behavior
    load_dotenv(override=True)
