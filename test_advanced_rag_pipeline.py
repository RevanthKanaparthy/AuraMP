import requests
import pytest
import os
import time

BASE_URL = "http://localhost:8000"
TEST_FILE = "test_upload.docx"
UPLOAD_DIR = "uploads"

# Ensure the test file exists
if not os.path.exists(TEST_FILE):
    with open(TEST_FILE, "w") as f:
        f.write("This is a test document about artificial intelligence and machine learning.")

@pytest.fixture(scope="module")
def admin_token():
    """Fixture to get an admin token."""
    # Retry logic to wait for the server to start
    for _ in range(5):
        try:
            response = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
            if response.status_code == 200:
                return response.json()["access_token"]
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    pytest.fail("Could not connect to the backend server.")


def test_upload_document_for_pipeline(admin_token):
    """Test document upload endpoint."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    filepath = os.path.join(UPLOAD_DIR, os.path.basename(TEST_FILE))
    
    # Ensure the file is in the upload directory for the backend to find
    if not os.path.exists(filepath):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(TEST_FILE, "rb") as src, open(filepath, "wb") as dst:
            dst.write(src.read())

    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(TEST_FILE), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"department": "CSE", "category": "research"}
        response = requests.post(f"{BASE_URL}/api/upload", headers=headers, files=files, data=data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "uploaded"
    assert data["filename"] == os.path.basename(TEST_FILE)

def test_advanced_rag_pipeline(admin_token):
    """Test the complete advanced RAG pipeline."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"query": "What is artificial intelligence?"}
    
    # Allow time for embedding to happen
    time.sleep(5)

    response = requests.post(f"{BASE_URL}/api/query", headers=headers, json=data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "answer" in data
    assert "sources" in data
    
    # Check if the answer is reasonable
    assert "error" not in data["answer"].lower()
    assert len(data["answer"]) > 10

    # Check if the correct source is identified
    assert os.path.basename(TEST_FILE) in data["sources"]

if __name__ == "__main__":
    pytest.main([__file__])
