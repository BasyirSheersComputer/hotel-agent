
import sys
import os
import psycopg2
# Add parent dir to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.services.auth_service import AuthService
    
    # 1. Test Hash Verification
    pw = "demo"
    hash_str = "$pbkdf2-sha256$29000$4RzDGMOYE2JsDUEo5Rzj/A$SIwoopGM.EZlV9m0X200NNDwwr06RfFcsr/CBUAz3D7g"
    print(f"Testing Verify: {AuthService.verify_password(pw, hash_str)}")

    # 2. Check DB
    conn = psycopg2.connect("postgresql://postgres:password@localhost:5432/hotel_agent")
    cur = conn.cursor()
    cur.execute("SELECT email, password_hash FROM users WHERE email='demo@resort-genius.com'")
    row = cur.fetchone()
    if row:
        print(f"User Found in DB: {row[0]}")
        db_hash = row[1]
        print(f"DB Hash Matches: {db_hash == hash_str}")
    else:
        print("User NOT Found in DB")
    conn.close()

except Exception as e:
    print(f"Error: {e}")
