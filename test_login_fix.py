#!/usr/bin/env python
import requests

# Test login with mock users
def test_login(username, password):
    url = "http://localhost:8000/token"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, data=data)
    print(f"Login test for {username}: Status {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['user']['name']} ({result['user']['role']})")
    else:
        print(f"Failed: {response.text}")
    print()

if __name__ == "__main__":
    print("Testing login functionality...")
    test_login("admin", "admin123")
    test_login("faculty1", "fac123")
    test_login("invalid", "invalid")
