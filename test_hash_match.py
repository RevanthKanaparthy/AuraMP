from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test what password matches the admin hash
admin_hash = "$2b$12$fp5ig69D9wKRESWKN7fxZu0QPa46dZzrzXaaUA0JEI1Ly11ljPkhu"

test_passwords = ["admin", "admin123", "password", "admin123!", "Aura2451", "mvsr_user"]

print("Testing password matches for admin hash...")
for pwd in test_passwords:
    if pwd_context.verify(pwd, admin_hash):
        print(f"✓ Password '{pwd}' matches the admin hash!")
        break
else:
    print("✗ None of the test passwords match the admin hash")

# Also test the faculty hash
faculty_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYNv3sBhUqm"
faculty_passwords = ["fac123", "faculty", "faculty123", "password"]

print("\nTesting password matches for faculty hash...")
for pwd in faculty_passwords:
    if pwd_context.verify(pwd, faculty_hash):
        print(f"✓ Password '{pwd}' matches the faculty hash!")
        break
else:
    print("✗ None of the test passwords match the faculty hash")
