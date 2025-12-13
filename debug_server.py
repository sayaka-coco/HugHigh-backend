"""
Debug script to test the FastAPI server and login endpoint
"""

import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import traceback
from fastapi.testclient import TestClient

try:
    # Import the app
    from main import app

    print("=" * 60)
    print("FastAPI Application Debug Test")
    print("=" * 60)
    print()

    # Create test client
    client = TestClient(app)

    # Test 1: Health check
    print("Test 1: Health Check")
    print("-" * 60)
    try:
        response = client.get("/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Health check passed")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        traceback.print_exc()
    print()

    # Test 2: Root endpoint
    print("Test 2: Root Endpoint")
    print("-" * 60)
    try:
        response = client.get("/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Root endpoint passed")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
        traceback.print_exc()
    print()

    # Test 3: Login with correct credentials
    print("Test 3: Login with Correct Credentials")
    print("-" * 60)
    try:
        login_data = {
            "email": "student1@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful")
            print(f"  Token: {data['access_token'][:50]}...")
            print(f"  User: {data['user']['email']}")
            print(f"  Role: {data['user']['role']}")
        else:
            print(f"✗ Login failed")
            print(f"  Response: {response.text}")

    except Exception as e:
        print(f"✗ Login test failed with exception: {e}")
        traceback.print_exc()
    print()

    # Test 4: Login with wrong password
    print("Test 4: Login with Wrong Password")
    print("-" * 60)
    try:
        login_data = {
            "email": "student1@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 401:
            print(f"✓ Correctly rejected wrong password")
        else:
            print(f"✗ Unexpected response for wrong password")
            print(f"  Response: {response.text}")

    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        traceback.print_exc()
    print()

    print("=" * 60)
    print("Debug Test Complete")
    print("=" * 60)

except Exception as e:
    print(f"✗ Failed to load application: {e}")
    traceback.print_exc()
