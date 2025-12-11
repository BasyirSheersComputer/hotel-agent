import sqlite3
import os

db_path = "backend/resort_genius.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

email = "admin@sunset.com"
print(f"Checking for user: {email}")
cursor.execute("SELECT user_id, org_id, role, password_hash FROM users WHERE email = ?", (email,))
row = cursor.fetchone()

if row:
    print(f"User Found: {row}")
    cursor.execute("SELECT * FROM organizations WHERE org_id = ?", (row[1],))
    org = cursor.fetchone()
    print(f"Org: {org}")
    
    # Check Billing Account link
    # org[6] is stripe_customer_id, org[7] is billing_account_id? Need to check schema order or column names
    # SQLite schema
    cols = [description[0] for description in cursor.description]
    print(f"Org Columns: {cols}")
    billing_idx = cols.index('billing_account_id')
    status_idx = cols.index('subscription_status')
    
    print(f"Billing Account ID: {org[billing_idx]}")
    print(f"Subscription Status: {org[status_idx]}")
    
else:
    print("User Not Found.")

conn.close()
