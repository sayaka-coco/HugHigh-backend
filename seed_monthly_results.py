"""
Seed script to create sample monthly results for testing.
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

        # Create monthly results for the past 4 months
        monthly_data = [
            {
                "year": 2024,
                "month": 12,
                "level": 4,
                "skills": {
                    "戦略的計画力": 58,
                    "課題設定・構想力": 65,
                    "巻き込む力": 45,
                    "対話する力": 52,
                    "実行する力": 72,
                    "完遂する力": 68,
                    "謙虚である力": 55
                },
                "ai_comment": "あなたは「実行する力」と「完遂する力」が特に高く、決めたことを着実にやり遂げる力があります。一方で「巻き込む力」を伸ばすことで、チームでの活動がさらに効果的になるでしょう。周囲の人に協力を求めることを意識してみてください。"
            },
            {
                "year": 2024,
                "month": 11,
                "level": 4,
                "skills": {
                    "戦略的計画力": 56,
                    "課題設定・構想力": 63,
                    "巻き込む力": 45,
                    "対話する力": 50,
                    "実行する力": 70,
                    "完遂する力": 66,
                    "謙虚である力": 54
                },
                "ai_comment": "前月と比較して、多くの能力が向上しています。特に「課題設定・構想力」と「実行する力」が成長しており、目標達成に向けた行動が効果的になっています。引き続き、チームメンバーとの協力を意識していきましょう。"
            },
            {
                "year": 2024,
                "month": 10,
                "level": 3,
                "skills": {
                    "戦略的計画力": 52,
                    "課題設定・構想力": 60,
                    "巻き込む力": 42,
                    "対話する力": 48,
                    "実行する力": 65,
                    "完遂する力": 62,
                    "謙虚である力": 51
                },
                "ai_comment": "安定した成長を続けています。「実行する力」が際立っており、計画を実際の行動に移す能力が高いです。今後は「対話する力」を意識的に高めることで、より円滑なコミュニケーションが可能になるでしょう。"
            },
            {
                "year": 2024,
                "month": 9,
                "level": 4,
                "skills": {
                    "戦略的計画力": 54,
                    "課題設定・構想力": 62,
                    "巻き込む力": 48,
                    "対話する力": 51,
                    "実行する力": 68,
                    "完遂する力": 64,
                    "謙虚である力": 53
                },
                "ai_comment": "今月は「巻き込む力」が特に向上しました。チームメンバーとの協力が効果的に行えるようになってきています。この調子で、周囲と積極的に関わっていくことを続けてください。"
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

    except Exception as e:
        print(f"Error creating monthly results: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding monthly results...")
    seed_monthly_results()
