import psycopg2
import bcrypt
import os
from urllib.parse import urlparse

# --- DATABASE CONFIGURATION ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    DB_CONFIG = {
        "dbname": parsed.path.lstrip('/'),
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": str(parsed.port)
    }
else:
    DB_CONFIG = {
        "dbname": os.environ.get("DB_NAME", "mvsr_rag"),
        "user": os.environ.get("DB_USER", "mvsr_user"),
        "password": os.environ.get("DB_PASSWORD", "Aura2451"),
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": os.environ.get("DB_PORT", "5432")
    }

def hash_password(password: str) -> str:
    """Hashes the password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def reset_admin_password():
    """Connects to the database and resets the admin password."""
    new_password = "admin"  # You can change this to a more secure password
    username_to_update = "admin"

    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        hashed_password = hash_password(new_password)
        
        print(f"Updating password for user: {username_to_update}...")
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (hashed_password, username_to_update)
        )
        
        # Check if the update was successful
        if cur.rowcount == 0:
            print(f"Error: User '{username_to_update}' not found in the database.")
            print("You may need to load the database schema first.")
        else:
            conn.commit()
            print(f"Successfully reset the password for '{username_to_update}' to '{new_password}'.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    reset_admin_password()
