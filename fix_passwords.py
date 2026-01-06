import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt (truncate to 72 bytes for bcrypt limit)"""
    # bcrypt has a 72 byte limit, truncate if necessary
    truncated_password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)

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

    # Update user passwords
    users_to_update = [
        ('admin', 'admin123'),
        ('faculty1', 'fac123')
    ]

    for username, password in users_to_update:
        try:
            hashed_password = hash_password(password)
            cursor.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE username = %s
            """, (hashed_password, username))
            print(f"✅ Updated password for {username}")
        except Exception as e:
            print(f"❌ Failed to update {username}: {e}")

    # Also update mock users in the backend
    print("🔧 Mock users in backend will use the same hashes")

    conn.commit()
    cursor.close()
    conn.close()
    print("Password fix complete!")

if __name__ == "__main__":
    main()
