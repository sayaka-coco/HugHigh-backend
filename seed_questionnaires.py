"""
Seed script to create sample questionnaires for testing.
Run this after creating users to add questionnaires.
"""
import uuid
from datetime import datetime, timedelta
from database import SessionLocal
from models import User, Questionnaire

def seed_questionnaires():
    db = SessionLocal()

    try:
        # Get a student user (role = 0)
        student = db.query(User).filter(User.role == 0).first()

        if not student:
            print("No student user found. Please create a student user first.")
            return

        print(f"Creating questionnaires for student: {student.email}")

        # Create questionnaires for multiple weeks
        questionnaires_data = [
            {
                "week": 12,
                "title": "第12週 週次アンケート",
                "deadline": datetime.utcnow() + timedelta(days=7),
                "status": "pending",
                "answers": None,
                "submitted_at": None
            },
            {
                "week": 11,
                "title": "第11週 週次アンケート",
                "deadline": datetime.utcnow() - timedelta(days=1),
                "status": "completed",
                "answers": {
                    "q1": 4,
                    "q2": "プロジェクトの資料を作成し、チームメンバーに共有しました。具体的な提案ができたため、次のステップに進めると感じました。",
                    "q3": "あった",
                    "q3_detail": "当初の計画では個人で進める予定でしたが、他のメンバーと協力した方が効率的だと気づき、役割分担を見直しました。",
                    "q4": "あった",
                    "q4_detail": "クラスメイトの田中さんと協力しました。データ分析を手伝ってもらい、より説得力のある資料が完成しました。",
                    "q5": "期限を守ることができず、チームに迷惑をかけてしまいました。時間管理が自分の弱みだと改めて感じました。"
                },
                "submitted_at": datetime.utcnow() - timedelta(days=1, hours=10)
            },
            {
                "week": 10,
                "title": "第10週 週次アンケート",
                "deadline": datetime.utcnow() - timedelta(days=8),
                "status": "completed",
                "answers": {
                    "q1": 3,
                    "q2": "調査活動を進め、必要な情報を集めることができました。",
                    "q3": "なかった",
                    "q3_detail": "",
                    "q4": "あった",
                    "q4_detail": "先生にアドバイスをいただき、研究の方向性が明確になりました。",
                    "q5": "情報の整理に時間がかかり、まとめる力が不足していると感じました。"
                },
                "submitted_at": datetime.utcnow() - timedelta(days=8, hours=5)
            },
            {
                "week": 9,
                "title": "第9週 週次アンケート",
                "deadline": datetime.utcnow() - timedelta(days=15),
                "status": "completed",
                "answers": {
                    "q1": 5,
                    "q2": "チーム全体で目標を達成することができ、自分の役割も果たせました。",
                    "q3": "あった",
                    "q3_detail": "作業の優先順位を見直し、重要なタスクから取り組むように変更しました。",
                    "q4": "あった",
                    "q4_detail": "チームメンバー全員で協力し、役割分担がうまくいきました。",
                    "q5": "プレゼンテーションの準備が不十分で、もっと練習が必要だと感じました。"
                },
                "submitted_at": datetime.utcnow() - timedelta(days=15, hours=8)
            },
        ]

        for data in questionnaires_data:
            questionnaire = Questionnaire(
                id=str(uuid.uuid4()),
                user_id=student.id,
                week=data["week"],
                title=data["title"],
                deadline=data["deadline"],
                status=data["status"],
                answers=data["answers"],
                submitted_at=data["submitted_at"]
            )
            db.add(questionnaire)

        db.commit()
        print(f"Successfully created {len(questionnaires_data)} questionnaires")

        # Display summary
        print("\nQuestionnaires created:")
        for data in questionnaires_data:
            status_mark = "[OK]" if data["status"] == "completed" else "[--]"
            print(f"  {status_mark} Week {data['week']}: {data['title']} ({data['status']})")

    except Exception as e:
        print(f"Error creating questionnaires: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding questionnaires...")
    seed_questionnaires()
