"""
Seed script to populate the database with test data.

This creates 5 test users:
- 2 students with email/password login
- 1 teacher with email/password login
- 1 student with Google account
- 1 teacher with Google account
"""

import sys
import io
import uuid
from database import SessionLocal, engine, Base
from models import User, UserGoogleAccount
from auth import get_password_hash

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create tables
Base.metadata.create_all(bind=engine)


def seed_database():
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already contains {existing_users} users. Skipping seed.")
            return

        # Test users data
        users_data = [
            {
                "id": str(uuid.uuid4()),
                "email": "student1@example.com",
                "password": "password123",
                "name": "田中太郎",
                "class_name": "1-A",
                "role": 0,  # Student
                "has_google": False
            },
            {
                "id": str(uuid.uuid4()),
                "email": "student2@example.com",
                "password": "password123",
                "name": "鈴木花子",
                "class_name": "1-B",
                "role": 0,  # Student
                "has_google": False
            },
            {
                "id": str(uuid.uuid4()),
                "email": "teacher1@example.com",
                "password": "password123",
                "name": "佐藤先生",
                "class_name": None,
                "role": 1,  # Teacher
                "has_google": False
            },
            {
                "id": str(uuid.uuid4()),
                "email": "admin@example.com",
                "password": "admin123",
                "name": "管理者",
                "class_name": None,
                "role": 2,  # Admin
                "has_google": False
            },
            {
                "id": str(uuid.uuid4()),
                "email": "student3.google@example.com",
                "password": None,  # Google-only user
                "name": "Google学生",
                "class_name": "2-A",
                "role": 0,  # Student
                "has_google": True,
                "google_sub": "google_sub_student_001",
                "profile_picture": "https://example.com/student3.jpg"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "teacher2.google@example.com",
                "password": None,  # Google-only user
                "name": "Google先生",
                "class_name": None,
                "role": 1,  # Teacher
                "has_google": True,
                "google_sub": "google_sub_teacher_001",
                "profile_picture": "https://example.com/teacher2.jpg"
            }
        ]

        # Create users
        for user_data in users_data:
            # Create user
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]) if user_data["password"] else None,
                name=user_data.get("name"),
                class_name=user_data.get("class_name"),
                role=user_data["role"],
                is_active=True
            )
            db.add(user)

            # Create Google account if needed
            if user_data["has_google"]:
                google_account = UserGoogleAccount(
                    user_id=user_data["id"],
                    google_sub=user_data["google_sub"],
                    google_email=user_data["email"],
                    profile_picture_url=user_data.get("profile_picture")
                )
                db.add(google_account)

        db.commit()

        print("✅ Database seeded successfully!")
        print("\n📋 Test User Credentials:")
        print("\n--- Email/Password Login Users ---")
        print("Student 1:")
        print("  Email: student1@example.com")
        print("  Password: password123")
        print("  Role: Student (0)")
        print()
        print("Student 2:")
        print("  Email: student2@example.com")
        print("  Password: password123")
        print("  Role: Student (0)")
        print()
        print("Teacher 1:")
        print("  Email: teacher1@example.com")
        print("  Password: password123")
        print("  Role: Teacher (1)")
        print()
        print("Admin:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("  Role: Admin (2)")
        print()
        print("\n--- Google OAuth Users (for testing) ---")
        print("Student 3:")
        print("  Email: student3.google@example.com")
        print("  Google Sub: google_sub_student_001")
        print("  Role: Student (0)")
        print()
        print("Teacher 2:")
        print("  Email: teacher2.google@example.com")
        print("  Google Sub: google_sub_teacher_001")
        print("  Role: Teacher (1)")
        print()

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
