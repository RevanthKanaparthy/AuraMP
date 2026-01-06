import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_chatbot():
    # Step 1: Login to get token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    print("🔐 Logging in...")
    login_response = requests.post(f"{BACKEND_URL}/token", data=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return

    token_data = login_response.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("✅ Login successful")

    # Step 2: Check documents
    print("📄 Checking documents...")
    docs_response = requests.get(f"{BACKEND_URL}/api/documents", headers=headers)
    if docs_response.status_code == 200:
        docs = docs_response.json()["documents"]
        print(f"📊 Found {len(docs)} documents")
        for doc in docs:
            print(f"  - {doc['filename']} ({doc['department']}/{doc['category']})")
    else:
        print(f"❌ Failed to get documents: {docs_response.status_code}")

    # Step 3: Test query about CNN
    query_data = {
        "query": "What is a convolutional neural network?",
        "top_k": 5
    }

    print("🤖 Testing chatbot query...")
    query_response = requests.post(
        f"{BACKEND_URL}/api/query",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps(query_data)
    )

    if query_response.status_code == 200:
        result = query_response.json()
        print("✅ Query successful!")
        print(f"📝 Response: {result['response'][:200]}...")
        print(f"📚 Sources: {len(result['sources'])} found")
        if result['sources']:
            for source in result['sources']:
                print(f"  - {source['filename']}")
    else:
        print(f"❌ Query failed: {query_response.status_code} - {query_response.text}")

if __name__ == "__main__":
    test_chatbot()
