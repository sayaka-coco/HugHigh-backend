"""
Seed script to create sample questionnaires for testing.
Run this after creating users to add questionnaires.
"""
import uuid
from datetime import datetime
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

        # Delete existing questionnaires for this student
        db.query(Questionnaire).filter(Questionnaire.user_id == student.id).delete()
        db.commit()

        # Create questionnaires for October, November, and December 2024
        questionnaires_data = [
            # === October 2024 (10月) - 4 weeks ===
            {
                "week": 1,
                "title": "第1週 週次アンケート",
                "deadline": datetime(2024, 10, 7, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 3,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "1", "studentName": "鈴木花子", "message": "初日からいろいろ教えてくれてありがとう！"}
                    ],
                    "q2_targetStudent": "鈴木花子",
                    "q2_targetStudentId": "1",
                    "q2_message": "初日からいろいろ教えてくれてありがとう！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "佐藤さんに好きな科目についてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "相手の好みを聞くことで、その人の性格も見えてきました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": False,
                    "q3_receiveContent": "",
                    "q3_couldSpeak": None,
                    "q3_speakingInsight": "",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 10, 6, 15, 30, 0),
                "created_at": datetime(2024, 10, 1, 9, 0, 0)
            },
            {
                "week": 2,
                "title": "第2週 週次アンケート",
                "deadline": datetime(2024, 10, 14, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 4,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "2", "studentName": "田中太郎", "message": "グループワークで助けてくれてありがとう！"}
                    ],
                    "q2_targetStudent": "田中太郎",
                    "q2_targetStudentId": "2",
                    "q2_message": "グループワークで助けてくれてありがとう！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "高橋さんに将来の夢についてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "深く質問することで、相手の本当の想いを引き出せました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": True,
                    "q3_receiveContent": "山田さんから趣味についてインタビューを受けました。",
                    "q3_couldSpeak": True,
                    "q3_speakingInsight": "自分のことを話すのが思ったより楽しかったです。",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 10, 13, 18, 0, 0),
                "created_at": datetime(2024, 10, 8, 9, 0, 0)
            },
            {
                "week": 3,
                "title": "第3週 週次アンケート",
                "deadline": datetime(2024, 10, 21, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 3,
                    "q2_hasGratitude": False,
                    "q2_gratitudeTargets": [],
                    "q2_targetStudent": "",
                    "q2_targetStudentId": "",
                    "q2_message": "",
                    "q3_didInterview": True,
                    "q3_didConduct": False,
                    "q3_conductContent": "",
                    "q3_couldExtract": None,
                    "q3_extractedInsight": "",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": True,
                    "q3_receiveContent": "佐藤さんから学校生活についてインタビューを受けました。",
                    "q3_couldSpeak": False,
                    "q3_speakingInsight": "",
                    "q3_speakingChallenge": "緊張してうまく話せませんでした。次は準備してから臨みたいです。"
                },
                "submitted_at": datetime(2024, 10, 20, 14, 30, 0),
                "created_at": datetime(2024, 10, 15, 9, 0, 0)
            },
            {
                "week": 4,
                "title": "第4週 週次アンケート",
                "deadline": datetime(2024, 10, 28, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 5,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "3", "studentName": "伊藤さくら", "message": "ノートを貸してくれて本当に助かりました！"},
                        {"studentId": "1", "studentName": "鈴木花子", "message": "いつも相談に乗ってくれてありがとう！"}
                    ],
                    "q2_targetStudent": "伊藤さくら",
                    "q2_targetStudentId": "3",
                    "q2_message": "ノートを貸してくれて本当に助かりました！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "鈴木さんに部活動についてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "部活への情熱を聞いて、自分も頑張ろうと思えました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": True,
                    "q3_receiveContent": "鈴木さんから私の目標についてインタビューを受けました。",
                    "q3_couldSpeak": True,
                    "q3_speakingInsight": "目標を言葉にすることで、より明確になりました。",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 10, 27, 16, 45, 0),
                "created_at": datetime(2024, 10, 22, 9, 0, 0)
            },
            # === November 2024 (11月) - 4 weeks ===
            {
                "week": 5,
                "title": "第5週 週次アンケート",
                "deadline": datetime(2024, 11, 4, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 4,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "2", "studentName": "田中太郎", "message": "発表の練習に付き合ってくれてありがとう！"}
                    ],
                    "q2_targetStudent": "田中太郎",
                    "q2_targetStudentId": "2",
                    "q2_message": "発表の練習に付き合ってくれてありがとう！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "山田さんに最近の挑戦についてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "挑戦する姿勢の大切さを学びました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": False,
                    "q3_receiveContent": "",
                    "q3_couldSpeak": None,
                    "q3_speakingInsight": "",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 11, 3, 17, 0, 0),
                "created_at": datetime(2024, 11, 1, 9, 0, 0)
            },
            {
                "week": 6,
                "title": "第6週 週次アンケート",
                "deadline": datetime(2024, 11, 11, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 3,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "4", "studentName": "渡辺健太", "message": "テスト勉強を一緒にしてくれてありがとう！"},
                        {"studentId": "1", "studentName": "鈴木花子", "message": "いつも励ましてくれてありがとう！"}
                    ],
                    "q2_targetStudent": "渡辺健太",
                    "q2_targetStudentId": "4",
                    "q2_message": "テスト勉強を一緒にしてくれてありがとう！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "高橋さんに休日の過ごし方についてインタビューしました。",
                    "q3_couldExtract": False,
                    "q3_extractedInsight": "",
                    "q3_extractionChallenge": "時間が足りず、深掘りできませんでした。次回はもっと時間を確保します。",
                    "q3_didReceive": True,
                    "q3_receiveContent": "田中さんから将来の夢についてインタビューを受けました。",
                    "q3_couldSpeak": True,
                    "q3_speakingInsight": "夢を語ることで、自分のモチベーションが上がりました。",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 11, 10, 19, 30, 0),
                "created_at": datetime(2024, 11, 5, 9, 0, 0)
            },
            {
                "week": 7,
                "title": "第7週 週次アンケート",
                "deadline": datetime(2024, 11, 18, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 4,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "5", "studentName": "小林美咲", "message": "プレゼン資料のアドバイスありがとう！すごく良くなった！"}
                    ],
                    "q2_targetStudent": "小林美咲",
                    "q2_targetStudentId": "5",
                    "q2_message": "プレゼン資料のアドバイスありがとう！すごく良くなった！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "佐藤さんに学校での好きな時間についてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "昼休みの友達との時間が大切だという話を聞いて、共感しました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": True,
                    "q3_receiveContent": "佐藤さんから私の強みについてインタビューを受けました。",
                    "q3_couldSpeak": True,
                    "q3_speakingInsight": "自分の強みを言語化できて自信がつきました。",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 11, 17, 15, 0, 0),
                "created_at": datetime(2024, 11, 12, 9, 0, 0)
            },
            {
                "week": 8,
                "title": "第8週 週次アンケート",
                "deadline": datetime(2024, 11, 25, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 5,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "2", "studentName": "田中太郎", "message": "月末の振り返りを一緒にしてくれてありがとう！"},
                        {"studentId": "3", "studentName": "伊藤さくら", "message": "いつも笑顔で元気をくれてありがとう！"},
                        {"studentId": "1", "studentName": "鈴木花子", "message": "1ヶ月間支えてくれてありがとう！"}
                    ],
                    "q2_targetStudent": "田中太郎",
                    "q2_targetStudentId": "2",
                    "q2_message": "月末の振り返りを一緒にしてくれてありがとう！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "クラス全員に今月の成長についてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "みんなそれぞれ成長していて、刺激を受けました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": True,
                    "q3_receiveContent": "複数の人から今月の振り返りインタビューを受けました。",
                    "q3_couldSpeak": True,
                    "q3_speakingInsight": "自分の成長を振り返ることで、来月への意欲が高まりました。",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 11, 24, 18, 30, 0),
                "created_at": datetime(2024, 11, 19, 9, 0, 0)
            },
            # === December 2024 (12月) - current month ===
            {
                "week": 9,
                "title": "第9週 週次アンケート",
                "deadline": datetime(2024, 12, 9, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 4,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "1", "studentName": "鈴木花子", "message": "新しい月も一緒に頑張ろうね！"}
                    ],
                    "q2_targetStudent": "鈴木花子",
                    "q2_targetStudentId": "1",
                    "q2_message": "新しい月も一緒に頑張ろうね！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "田中さんに新年の目標についてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "目標を共有することで、お互いの意識が高まることがわかりました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": False,
                    "q3_receiveContent": "",
                    "q3_couldSpeak": None,
                    "q3_speakingInsight": "",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 12, 8, 16, 0, 0),
                "created_at": datetime(2024, 12, 3, 9, 0, 0)
            },
            {
                "week": 10,
                "title": "第10週 週次アンケート",
                "deadline": datetime(2024, 12, 16, 23, 59, 59),
                "status": "completed",
                "answers": {
                    "q1": 4,
                    "q2_hasGratitude": True,
                    "q2_gratitudeTargets": [
                        {"studentId": "2", "studentName": "田中太郎", "message": "プロジェクトのリーダーシップありがとう！"},
                        {"studentId": "4", "studentName": "渡辺健太", "message": "資料作成手伝ってくれてありがとう！"}
                    ],
                    "q2_targetStudent": "田中太郎",
                    "q2_targetStudentId": "2",
                    "q2_message": "プロジェクトのリーダーシップありがとう！",
                    "q3_didInterview": True,
                    "q3_didConduct": True,
                    "q3_conductContent": "高橋さんに今年の振り返りについてインタビューしました。",
                    "q3_couldExtract": True,
                    "q3_extractedInsight": "1年間の成長を聞いて、自分も頑張ろうと思いました。",
                    "q3_extractionChallenge": "",
                    "q3_didReceive": True,
                    "q3_receiveContent": "山田さんから今年達成したことについてインタビューを受けました。",
                    "q3_couldSpeak": True,
                    "q3_speakingInsight": "達成したことを振り返ると、自信がつきました。",
                    "q3_speakingChallenge": ""
                },
                "submitted_at": datetime(2024, 12, 14, 10, 0, 0),
                "created_at": datetime(2024, 12, 10, 9, 0, 0)
            },
            {
                "week": 11,
                "title": "第11週 週次アンケート",
                "deadline": datetime(2024, 12, 23, 23, 59, 59),
                "status": "pending",
                "answers": None,
                "submitted_at": None,
                "created_at": datetime(2024, 12, 17, 9, 0, 0)
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
            # Manually set created_at to specific date
            questionnaire.created_at = data["created_at"]
            db.add(questionnaire)

        db.commit()
        print(f"Successfully created {len(questionnaires_data)} questionnaires")

        # Display summary by month
        print("\nQuestionnaires created:")
        print("\n=== October 2024 ===")
        for data in questionnaires_data[:4]:
            status_mark = "[OK]" if data["status"] == "completed" else "[--]"
            print(f"  {status_mark} Week {data['week']}: {data['title']} ({data['status']})")

        print("\n=== November 2024 ===")
        for data in questionnaires_data[4:8]:
            status_mark = "[OK]" if data["status"] == "completed" else "[--]"
            print(f"  {status_mark} Week {data['week']}: {data['title']} ({data['status']})")

        print("\n=== December 2024 ===")
        for data in questionnaires_data[8:]:
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
