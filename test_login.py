import bcrypt
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Test mock users
mock_users = {
    'admin': {
        'username': 'admin',
        'password': hash_password('admin123'),
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
