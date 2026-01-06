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

    # Update the Excel file (assuming doc_id is 14 from previous output)
    update_url = "http://localhost:8000/api/documents/14"
    files = {"file": open("uploads/Journals-Conferences-Books-Book Chapters 2024-25 (1).xlsx", "rb")}
    data = {"reason": "Updated text extraction for better LLM parsing"}

    update_response = requests.put(update_url, files=files, data=data, headers=headers)
    if update_response.status_code == 200:
        print("Document updated successfully")
    else:
        print("Update failed:", update_response.status_code, update_response.text)
else:
    print("Login failed:", response.status_code, response.text)
