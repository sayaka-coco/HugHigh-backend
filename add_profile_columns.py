"""
Migration script to add profile columns to users table.
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    # Add profile_image column if not exists
    if 'profile_image' not in columns:
        print("Adding profile_image column...")
        cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
        print("  Done!")
    else:
        print("profile_image column already exists")

    # Add hobbies column if not exists
    if 'hobbies' not in columns:
        print("Adding hobbies column...")
        cursor.execute("ALTER TABLE users ADD COLUMN hobbies VARCHAR(50)")
        print("  Done!")
    else:
        print("hobbies column already exists")

    # Add current_focus column if not exists
    if 'current_focus' not in columns:
        print("Adding current_focus column...")
        cursor.execute("ALTER TABLE users ADD COLUMN current_focus JSON")
        print("  Done!")
    else:
        print("current_focus column already exists")

    conn.commit()
    conn.close()
    print("\nMigration completed successfully!")


if __name__ == "__main__":
    migrate()
