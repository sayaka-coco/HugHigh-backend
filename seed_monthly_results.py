"""
Seed script to create sample monthly results for testing.
Creates October result as history, November should be finalized via dashboard.
"""
import uuid
from database import SessionLocal
from models import User, MonthlyResult

def seed_monthly_results():
    db = SessionLocal()

    try:
        # Get a student user (role = 0)
        student = db.query(User).filter(User.role == 0).first()

        if not student:
            print("No student user found. Please create a student user first.")
            return

        print(f"Creating monthly results for student: {student.email}")

        # Delete existing monthly results for this student
        db.query(MonthlyResult).filter(MonthlyResult.user_id == student.id).delete()
        db.commit()

        # Create October 2024 result as history
        # November will be finalized via dashboard with real questionnaire data
        monthly_data = [
            {
                "year": 2024,
                "month": 10,
                "level": 4,
                "skills": {
                    "戦略的計画力": 63,  # Average Q1 score: (3+4+3+5)/4 = 3.75 -> (3.75-1)/4*100 = 69
                    "課題設定・構想力": 75,  # Extract rate: 3/3 = 100% (3 conducted, 3 could extract)
                    "巻き込む力": 75,  # Total interviews: 6 (3 conducted + 3 received) / 8 max = 75%
                    "対話する力": 83,  # Extract: 3/3=100%, Speak: 2/3=67% -> avg 83%
                    "実行する力": 63,  # Same as strategic planning
                    "完遂する力": 100,  # All questionnaires completed
                    "謙虚である力": 72  # AI evaluated from gratitude messages
                },
                "ai_comment": "10月は全体的に良い成長を見せました。特に「対話する力」と「巻き込む力」が高く、インタビュー活動に積極的に取り組めていました。「戦略的計画力」と「実行する力」をさらに伸ばすことで、より効果的な行動ができるようになるでしょう。"
            },
        ]

        for data in monthly_data:
            result = MonthlyResult(
                id=str(uuid.uuid4()),
                user_id=student.id,
                year=data["year"],
                month=data["month"],
                level=data["level"],
                skills=data["skills"],
                ai_comment=data["ai_comment"]
            )
            db.add(result)

        db.commit()
        print(f"Successfully created {len(monthly_data)} monthly results")

        # Display summary
        print("\nMonthly results created:")
        for data in monthly_data:
            print(f"  [OK] {data['year']}/{data['month']:02d}: Level {data['level']}")
            print(f"       Skills: {data['skills']}")

        print("\nNote: November 2024 result should be finalized via dashboard.")
        print("      December 2024 is the current month (in progress).")

    except Exception as e:
        print(f"Error creating monthly results: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding monthly results...")
    seed_monthly_results()
