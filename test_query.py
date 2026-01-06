import requests
import json

# Test login
login_url = "http://localhost:8000/token"
query_url = "http://localhost:8000/api/query"

# Login as admin
login_data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post(login_url, data=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Query for research papers
    query_data = {
        "query": "what are the research papers available?",
        "top_k": 5
    }

    query_response = requests.post(query_url, json=query_data, headers=headers)
    if query_response.status_code == 200:
        result = query_response.json()
        print("Response:", result["response"])
        print("Sources:", result["sources"])
    else:
        print("Query failed:", query_response.status_code, query_response.text)
else:
    print("Login failed:", response.status_code, response.text)
