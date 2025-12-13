"""
Test script to verify login functionality works correctly.
Run this after starting the backend server.
"""

import sys
import io
import requests
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:8000"

def test_health():
    """Test if the API is running"""
    print("=" * 50)
    print("Testing API Health Check...")
    print("=" * 50)
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✓ API is running")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("\nPlease make sure the backend is running:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
        return False

def test_login(email, password):
    """Test login with email and password"""
    print("\n" + "=" * 50)
    print(f"Testing Login: {email}")
    print("=" * 50)

    try:
        payload = {
            "email": email,
            "password": password
        }

        response = requests.post(
            f"{API_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Login successful!")
            print(f"  Token: {data['access_token'][:50]}...")
            print(f"  User: {data['user']['email']}")
            print(f"  Role: {data['user']['role']}")
            return data['access_token']
        else:
            print(f"✗ Login failed")
            print(f"  Error: {response.text}")
            return None

    except Exception as e:
        print(f"✗ Error during login: {e}")
        return None

def test_me(token):
    """Test /auth/me endpoint with token"""
    print("\n" + "=" * 50)
    print("Testing /auth/me endpoint...")
    print("=" * 50)

    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(f"{API_URL}/auth/me", headers=headers)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Successfully retrieved user info")
            print(f"  Email: {data['email']}")
            print(f"  Role: {data['role']}")
            return True
        else:
            print(f"✗ Failed to retrieve user info")
            print(f"  Error: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n")
    print("╔════════════════════════════════════════════════╗")
    print("║   HugHigh Login API Test Script               ║")
    print("╚════════════════════════════════════════════════╝")
    print()

    # Test health check
    if not test_health():
        print("\n⚠ Backend is not running. Please start it first.")
        return

    # Test accounts
    test_accounts = [
        ("student1@example.com", "password123", "Student"),
        ("teacher1@example.com", "password123", "Teacher"),
    ]

    print("\n")
    print("=" * 50)
    print("Running Login Tests...")
    print("=" * 50)

    for email, password, role in test_accounts:
        token = test_login(email, password)
        if token:
            test_me(token)

    print("\n")
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    print("✓ If all tests passed, the backend is working correctly")
    print("✓ You can now use the frontend to login")
    print()
    print("Test accounts:")
    print("  student1@example.com / password123")
    print("  teacher1@example.com / password123")
    print()

if __name__ == "__main__":
    main()
