#!/usr/bin/env python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

# Test password hashing
if __name__ == "__main__":
    print("Testing password hashing...")

    # Hash the passwords
    admin_hash = hash_password("admin123")
    faculty_hash = hash_password("fac123")

    print(f"Admin hash: {admin_hash}")
    print(f"Faculty hash: {faculty_hash}")

    # Test verification
    print(f"Admin verify: {verify_password('admin123', admin_hash)}")
    print(f"Faculty verify: {verify_password('fac123', faculty_hash)}")

    # Test with the hardcoded hashes from the code
    hardcoded_admin = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lWZQXyzO'
    hardcoded_faculty = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8lWZQXyzO'

    print(f"Hardcoded admin verify: {verify_password('admin123', hardcoded_admin)}")
    print(f"Hardcoded faculty verify: {verify_password('fac123', hardcoded_faculty)}")
