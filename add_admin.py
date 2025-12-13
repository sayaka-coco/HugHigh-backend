"""
Script to add an admin user to the database.
"""

import sys
import io
import uuid
from database import SessionLocal
from models import User
from auth import get_password_hash

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def add_admin():
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print(f"✅ Admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            return

        # Create admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role=2,  # Admin
            is_active=True
        )
        db.add(admin_user)
        db.commit()

        print("✅ Admin user created successfully!")
        print("\n📋 Admin Credentials:")
        print("   Email: admin@example.com")
        print("   Password: admin123")
        print("   Role: Admin (2)")
        print("\n⚠️  Please change the password after first login in production!")

    except Exception as e:
        print(f"❌ Error adding admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_admin()
