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
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

# Test mock users
mock_users = {
    'admin': {
        'username': 'admin',
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'name': 'Administrator',
        'department': 'Admin'
    }
}

# Test login
username = 'admin'
password = 'admin123'

if username in mock_users:
    mock_user = mock_users[username]
    if verify_password(password, mock_user['password']):
        token = create_access_token(data={"sub": mock_user["username"], "role": mock_user["role"]})
        print("✓ Login successful")
        print(f"Token: {token[:50]}...")
        print(f"User: {mock_user['name']}")
    else:
        print("✗ Password mismatch")
else:
    print("✗ User not found")
