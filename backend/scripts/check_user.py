
import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:password@localhost:5432/hotel_agent")
    cur = conn.cursor()
    cur.execute("SELECT email, password_hash FROM users WHERE email='test_hash@example.com'")
    row = cur.fetchone()
    if row:
        print(f"User Found: {row[0]}")
        print(f"Hash: {row[1]}")
    else:
        print("User NOT Found")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
