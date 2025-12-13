"""
Test API endpoint directly
"""

import sys
import io
import requests
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("バックエンド API テスト")
print("=" * 60)

# Test login endpoint
print("\n📝 student1@example.com でログインテスト...\n")

try:
    response = requests.post(
        'http://127.0.0.1:8000/auth/login',
        json={
            'email': 'student1@example.com',
            'password': 'password123'
        },
        timeout=5
    )

    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンス:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code == 200:
        print("\n✅ ログイン成功！")
    else:
        print(f"\n❌ ログイン失敗 (ステータスコード: {response.status_code})")

except requests.exceptions.ConnectionError:
    print("❌ バックエンドサーバーに接続できません")
    print("   http://127.0.0.1:8000 が起動していることを確認してください")
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
