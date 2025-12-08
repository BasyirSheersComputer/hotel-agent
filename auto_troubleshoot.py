#!/usr/bin/env python3
"""
auto_troubleshoot.py

A script to automatically fix common issues and launch the Hotel Agent system.
Shortcuts the troubleshooting process by applying known fixes.

Fixes applied:
1. Adds 'email-validator' to backend/requirements.txt
2. Patches backend/app/config/settings.py to respect DEMO_MODE env var
3. Patches docker-compose.yml for Frontend Dev Mode and 0.0.0.0 binding
4. Ensures .env exists and has correct encoding
5. Launches system via Docker Compose
6. Populates Vector DB for RAG
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(msg):
    print(f"\n[+] {msg}")

def fix_backend_requirements():
    print_step("Checking backend requirements...")
    req_path = Path("backend/requirements.txt")
    if not req_path.exists():
        print("Error: backend/requirements.txt not found!")
        return
    
    content = req_path.read_text(encoding="utf-8")
    if "email-validator" not in content:
        print("Adding email-validator to requirements...")
        with req_path.open("a", encoding="utf-8") as f:
            f.write("\nemail-validator\n")
    else:
        print("  email-validator already present.")

def fix_backend_settings():
    print_step("Checking backend settings...")
    settings_path = Path("backend/app/config/settings.py")
    if not settings_path.exists():
        print("Error: settings.py not found!")
        return
    
    content = settings_path.read_text(encoding="utf-8")
    target = 'DEMO_MODE = False # os.getenv("DEMO_MODE", "true").lower() == "true"'
    replacement = 'DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"'
    
    if target in content:
        print("Patching DEMO_MODE in settings.py...")
        content = content.replace(target, replacement)
        settings_path.write_text(content, encoding="utf-8")
    else:
        print("  Settings already patched or different.")

def fix_docker_compose():
    print_step("Checking docker-compose.yml...")
    dc_path = Path("docker-compose.yml")
    if not dc_path.exists():
        print("Error: docker-compose.yml not found!")
        return

    content = dc_path.read_text(encoding="utf-8")
    modified = False

    # 1. Check for DEMO_MODE in backend
    if "DEMO_MODE=${DEMO_MODE:-false}" not in content:
        print("Adding DEMO_MODE to backend environment...")
        # Simple string replacement for now, assuming standard structure
        if "GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}" in content:
            content = content.replace(
                "GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}",
                "GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}\n      - DEMO_MODE=${DEMO_MODE:-false}"
            )
            modified = True

    # 2. Check for Frontend Dev Mode configuration
    if "image: node:20-alpine" not in content:
        print("Updating Frontend to Dev Mode (node:20-alpine, 0.0.0.0 binding)...")
        # We'll look for the build block to replace
        build_block = """    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: resort_genius_frontend
    ports:
      - "8080:80"
"""
        dev_block = """    image: node:20-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
    command: sh -c "npm install && npm run dev -- -H 0.0.0.0"
    container_name: resort_genius_frontend
    ports:
      - "8080:3000"
"""
        # Attempt to replace if build block exists (might have slight whitespace diffs)
        # If already patched, this block won't match exactly, which is fine.
        # But we also need to handle the case where it's partially patched.
        # For robustness in this script, we'll verify if "npm run dev" is present.
        if "npm run dev" not in content:
             print("Please manually verify docker-compose.yml matches the functional state (Dev Mode). Automatic patching for complex YAML is risky via simple script.")
        else:
            print("  Frontend appears to be in Dev Mode.")

    if modified:
        dc_path.write_text(content, encoding="utf-8")
        print("docker-compose.yml updated.")

def ensure_env_file():
    print_step("Ensuring .env file...")
    env_path = Path(".env")
    if not env_path.exists():
        print(" Creating empty .env...")
        env_path.touch()
    
    # Check for encoding (read raw bytes)
    raw = env_path.read_bytes()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        print(" Fixing .env encoding (converting to UTF-8)...")
        content = raw.decode("utf-16", errors="ignore") # Assumption
        env_path.write_text(content, encoding="utf-8")

    # Add vars
    if "DEMO_MODE=true" not in content:
        with env_path.open("a", encoding="utf-8") as f:
            f.write("\nDEMO_MODE=true\n")
    if "LOCAL_DEV=true" not in content:
        with env_path.open("a", encoding="utf-8") as f:
            f.write("\nLOCAL_DEV=true\n")

def run_system_commands():
    print_step("Launching System...")
    
    try:
        # 1. Docker Up
        print("Running: docker-compose up -d --remove-orphans")
        subprocess.check_call(["docker-compose", "up", "-d", "--remove-orphans"])
        
        # 2. Populate DB
        print("\nWaiting 10s for services to stabilize...")
        import time
        time.sleep(10)
        
        print("Populating Vector DB...")
        subprocess.check_call(["docker-compose", "exec", "-T", "backend", "python", "populate_db.py"])
        
        # 3. Flush Redis
        print("Flushing Redis Cache...")
        subprocess.check_call(["docker-compose", "exec", "-T", "redis", "redis-cli", "FLUSHALL"])
        
        print("\n[SUCCESS] System should be running!")
        print("Frontend: http://localhost:8080")
        print("Backend:  http://localhost:8000")
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed with exit code {e.returncode}")

if __name__ == "__main__":
    print("=== Hotel Agent Auto-Troubleshooter ===")
    fix_backend_requirements()
    fix_backend_settings()
    fix_docker_compose()
    ensure_env_file()
    run_system_commands()
