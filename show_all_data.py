"""
Show all data in the database
"""

import sys
import io
from database import SessionLocal
from models import User, UserGoogleAccount, AuditLog

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = SessionLocal()

print("\n" + "=" * 70)
print("📊 データベース内のすべてのデータ")
print("=" * 70)

# ========== ユーザーテーブル ==========
print("\n【ユーザー（User）テーブル】")
print("-" * 70)
users = db.query(User).all()
print(f"合計: {len(users)}件\n")

role_names = {0: "生徒", 1: "教員", 2: "管理者"}

for idx, user in enumerate(users, 1):
    print(f"{idx}. Email: {user.email}")
    print(f"   ID: {user.id}")
    print(f"   ロール: {role_names.get(user.role, '不明')} (role={user.role})")
    print(f"   有効: {'はい' if user.is_active else 'いいえ'}")
    print(f"   パスワード: {'あり' if user.hashed_password else 'なし'}")
    print(f"   作成日時: {user.created_at}")
    print()

# ========== Google アカウント ==========
print("\n【Google アカウント（UserGoogleAccount）テーブル】")
print("-" * 70)
google_accounts = db.query(UserGoogleAccount).all()
print(f"合計: {len(google_accounts)}件\n")

if google_accounts:
    for idx, account in enumerate(google_accounts, 1):
        user = account.user
        print(f"{idx}. Google Email: {account.google_email}")
        print(f"   Google Sub: {account.google_sub}")
        print(f"   リンクユーザー: {user.email if user else 'なし'}")
        print(f"   プロフィール画像: {'あり' if account.profile_picture_url else 'なし'}")
        print()
else:
    print("(Google アカウントはリンクされていません)\n")

# ========== 監査ログ ==========
print("\n【監査ログ（AuditLog）テーブル】")
print("-" * 70)
audit_logs = db.query(AuditLog).all()
print(f"合計: {len(audit_logs)}件\n")

if audit_logs:
    # 最新20件を表示
    recent_logs = audit_logs[-20:] if len(audit_logs) > 20 else audit_logs
    for idx, log in enumerate(recent_logs, 1):
        user = log.user
        print(f"{idx}. {log.timestamp} - {user.email if user else '(ユーザー削除済み)'}")
        print(f"   アクション: {log.action}")
        print(f"   IPアドレス: {log.ip_address if log.ip_address else 'なし'}")
        print()
else:
    print("(監査ログはまだ記録されていません)\n")

print("=" * 70)

db.close()
