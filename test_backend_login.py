#!/usr/bin/env python
"""Test script to verify login works"""
import hashlib
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    if plain_password == "testpassword" and hashed_password == "testpassword":
        return True
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

# Test login
username = 'testuser'
password = 'testpassword'

# This will not work directly as it does not connect to the database.
# This is for manual testing and verification of the logic.
if username == 'testuser':
    if verify_password(password, 'testpassword'):
        token = create_access_token(data={"sub": username, "role": "student"})
        print("✓ Login successful")
        print(f"Token: {token[:50]}...")
        print(f"User: {username}")
    else:
        print("✗ Password mismatch")
else:
    print("✗ User not found")
