import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "mvsr_rag"
DB_USER = "postgres"
DB_PASSWORD = "admin123"  # Update this if different

def update_database_schema():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Drop the existing constraint
        cursor.execute("ALTER TABLE documents DROP CONSTRAINT documents_category_check;")

        # Add the new constraint with 'test' included
        cursor.execute("""
            ALTER TABLE documents ADD CONSTRAINT documents_category_check
            CHECK (category IN ('research', 'patent', 'publication', 'project', 'proposal', 'test'));
        """)

        print("Database schema updated successfully. 'test' category added to allowed categories.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error updating database schema: {e}")

if __name__ == "__main__":
    update_database_schema()
