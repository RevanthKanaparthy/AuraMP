#!/usr/bin/env python
"""Test script to verify database login works"""
import requests

# Test data
test_cases = [
    {
        "username": "testuser",
        "password": "testpassword",
        "expected_status": 200,
        "message": "Test with correct credentials"
    },
    {
        "username": "testuser",
        "password": "wrongpassword",
        "expected_status": 401,
        "message": "Test with incorrect password"
    },
    {
        "username": "nosuchuser",
        "password": "password",
        "expected_status": 401,
        "message": "Test with non-existent user"
    }
]

for test in test_cases:
    response = requests.post(
        "http://localhost:8000/token",
        data={"username": test["username"], "password": test["password"]}
    )
    if response.status_code == test["expected_status"]:
        print(f"✓ {test['message']} passed")
    else:
        print(f"✗ {test['message']} failed. Expected {test['expected_status']}, got {response.status_code}")
