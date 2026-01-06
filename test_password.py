import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Test the mock user hash
mock_hash = hash_password('admin123')

test_passwords = ['admin123', 'fac123', 'admin', 'faculty', 'password', '123456']

print("Testing mock user password hash...")
for pwd in test_passwords:
    if verify_password(pwd, mock_hash):
        print(f"✅ Password match found: '{pwd}'")
        break
else:
    print("❌ No password match found in test list")
    print(f"Hash: {mock_hash}")
