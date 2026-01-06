import requests

# Login as admin
login_url = "http://localhost:8000/token"
login_data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post(login_url, data=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Delete the old document
    delete_url = "http://localhost:8000/api/documents/14"
    delete_response = requests.delete(delete_url, headers=headers)
    if delete_response.status_code == 200:
        print("Document deleted successfully")
    else:
        print("Delete failed:", delete_response.status_code, delete_response.text)

    # Re-upload the Excel file
    upload_url = "http://localhost:8000/api/upload"
    files = {"file": open("uploads/Journals-Conferences-Books-Book Chapters 2024-25 (1).xlsx", "rb")}
    data = {"department": "GENERAL", "category": "research"}

    upload_response = requests.post(upload_url, files=files, data=data, headers=headers)
    if upload_response.status_code == 200:
        result = upload_response.json()
        print("Document uploaded successfully, doc_id:", result["doc_id"])
    else:
        print("Upload failed:", upload_response.status_code, upload_response.text)
else:
    print("Login failed:", response.status_code, response.text)
