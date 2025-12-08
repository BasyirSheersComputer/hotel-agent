import psycopg2
import sys

def check_postgres():
    try:
        # Default credentials from docker-compose.db.yml
        conn = psycopg2.connect(
            dbname="hotel_agent",
            user="postgres",
            password="password",
            host="localhost",
            port="5432",
            connect_timeout=3
        )
        print("SUCCESS: Connected to PostgreSQL.")
        conn.close()
        return True
    except Exception as e:
        print(f"FAILURE: Could not connect to PostgreSQL. {e}")
        return False

if __name__ == "__main__":
    check_postgres()
