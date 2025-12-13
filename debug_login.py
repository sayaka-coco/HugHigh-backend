"""
Debug script to test login
"""

import sys
import io
from database import SessionLocal
from models import User
from auth import verify_password

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = SessionLocal()

# Check all users
print("=" * 50)
print("全ユーザー確認")
print("=" * 50)
users = db.query(User).all()
for user in users:
    print(f"\nEmail: {user.email}")
    print(f"  Role: {user.role}")
    print(f"  Active: {user.is_active}")
    print(f"  Has password: {user.hashed_password is not None}")

# Test student1
print("\n" + "=" * 50)
print("student1@example.com テスト")
print("=" * 50)
student1 = db.query(User).filter(User.email == 'student1@example.com').first()
if student1:
    print(f"✅ ユーザーが見つかりました")
    print(f"Email: {student1.email}")
    print(f"Role: {student1.role}")
    print(f"Active: {student1.is_active}")
    print(f"\nパスワード検証テスト:")
    result = verify_password("password123", student1.hashed_password)
    print(f"  入力: password123")
    print(f"  検証結果: {result}")
else:
    print("❌ ユーザーが見つかりません")

db.close()
