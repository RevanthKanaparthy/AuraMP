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

# Test login
username = 'testuser'
password = 'testpassword'
hashed_password = hash_password(password)


# This will not work directly as it does not connect to the database.
# This is for manual testing and verification of the logic.
if username == 'testuser':
    if verify_password(password, hashed_password):
        token = create_access_token(data={"sub": username, "role": "student"})
        print("✓ Login successful")
        print(f"Token: {token[:50]}...")
        print(f"User: {username}")
    else:
        print("✗ Password mismatch")
else:
    print("✗ User not found")
