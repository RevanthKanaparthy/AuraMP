#!/usr/bin/env python3
"""
Generate proper bcrypt hashes for user passwords
"""
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

# Generate hashes for test users
users = [
    ("admin", "admin123"),
    ("faculty1", "fac123"),
    ("faculty2", "fac123"),
    ("student1", "stu123")
]

print("Generated bcrypt hashes:")
for username, password in users:
    hashed = hash_password(password)
    print(f"('{username}', '{hashed}', ...),")
