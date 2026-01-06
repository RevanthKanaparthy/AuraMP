import requests
import pytest

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def admin_token():
    """Fixture to get an admin token."""
    response = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def faculty_token():
    """Fixture to get a faculty token."""
    response = requests.post(f"{BASE_URL}/token", data={"username": "faculty1", "password": "fac123"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_login_admin():
    """Test admin login."""
    response = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_faculty():
    """Test faculty login."""
    response = requests.post(f"{BASE_URL}/token", data={"username": "faculty1", "password": "fac123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid():
    """Test invalid login."""
    response = requests.post(f"{BASE_URL}/token", data={"username": "invalid", "password": "invalid"})
    assert response.status_code == 401



def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "llm_health" in data
    assert "database_status" in data

def test_upload_document(admin_token):
    """Test document upload endpoint."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    with open("test_upload.xlsx", "rb") as f:
        files = {"file": ("test_upload.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"department": "CSE", "category": "research"}
        response = requests.post(f"{BASE_URL}/api/upload", headers=headers, files=files, data=data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "uploaded"
    assert "filename" in data

def test_query_rag(admin_token):
    """Test query RAG endpoint."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"query": "What is AI?"}
    response = requests.post(f"{BASE_URL}/api/query", headers=headers, json=data)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
