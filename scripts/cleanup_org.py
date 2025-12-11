import sqlite3
import os

db_path = "backend/resort_genius.db"
if not os.path.exists(db_path):
    print("DB not found")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

org_slug = "sunset-paradise"

print(f"Checking for org: {org_slug}")
cursor.execute("SELECT org_id FROM organizations WHERE slug = ?", (org_slug,))
row = cursor.fetchone()

if row:
    org_id = row[0]
    print(f"Found Org {org_id}. Deleting...")
    # Cascade delete should handle users etc, but let's be safe if SQLite FK support is off
    cursor.execute("DELETE FROM users WHERE org_id = ?", (org_id,))
    cursor.execute("DELETE FROM organizations WHERE org_id = ?", (org_id,))
    conn.commit()
    print("Deleted.")
else:
    print("Not found.")

conn.close()
