#!/usr/bin/env python3
"""Test script to check PostgreSQL connectivity"""

import psycopg2
from psycopg2.extras import RealDictCursor

def test_connection():
    # Try the config from backend_complete.py
    config1 = {
        "dbname": "mvsr_rag",
        "user": "mvsr_user",
        "password": "Aura2451",
        "host": "localhost",
        "port": "5432"
    }

    # Try the config from update_db_schema.py
    config2 = {
        "host": "localhost",
        "database": "mvsr_rag",
        "user": "postgres",
        "password": "admin123"
    }

    configs = [config1, config2]

    for i, config in enumerate(configs, 1):
        print(f"Testing config {i}: {config}")
        try:
            conn = psycopg2.connect(**config)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"✓ Connection successful: {version['version']}")
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")

    print("All connection attempts failed.")
    return False

if __name__ == "__main__":
    test_connection()
