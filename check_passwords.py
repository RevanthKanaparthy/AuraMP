import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    # Connect to database
    try:
        conn = psycopg2.connect(
            dbname="mvsr_rag",
            user="mvsr_user",
            password="Aura2451",
            host="localhost"
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"Database connection failed: {e}")
        return

    # Check current password hashes
    cursor.execute("SELECT username, password_hash FROM users")
    users = cursor.fetchall()

    print("Current password hashes in database:")
    for user in users:
        print(f"  {user['username']}: {user['password_hash']}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
