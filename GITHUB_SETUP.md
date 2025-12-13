# GitHub リポジトリからのセットアップ手順

## 📦 リポジトリ情報

- **リポジトリURL:** https://github.com/sayaka-coco/RFP-ask_test-back.git
- **ブランチ:** main

## 🚀 クローンとセットアップ

### 手順1: リポジトリのクローン

```bash
git clone https://github.com/sayaka-coco/RFP-ask_test-back.git
cd RFP-ask_test-back
```

### 手順2: 仮想環境の作成

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 手順3: 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 手順4: 環境変数の設定（重要）

`.env.example`をコピーして`.env`を作成:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

`.env`ファイルを編集:

```bash
# 1. SECRET_KEYを生成して設定
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 出力された値をSECRET_KEYに設定

# 2. Google OAuth設定（オプション）
# https://console.cloud.google.com/ で取得
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
```

**⚠️ 重要:** `.env`ファイルは絶対にGitにコミットしないでください！

### 手順5: データベースの初期化

```bash
python seed_data.py
```

テストアカウントが作成されます:
- student1@example.com / password123
- student2@example.com / password123
- teacher1@example.com / password123

### 手順6: サーバーの起動

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

または、簡単に起動:

```bash
# Windows
start.bat

# macOS/Linux
chmod +x start.sh
./start.sh
```

## ✅ 動作確認

### 1. Health Check

ブラウザで以下にアクセス:
```
http://localhost:8000/health
```

正常な場合:
```json
{"status":"healthy"}
```

### 2. API ドキュメント

```
http://localhost:8000/docs
```

Swagger UIでAPIの仕様を確認できます。

### 3. ログインテスト

```bash
python test_login.py
```

すべてのテストが✓になればOKです。

## 🔐 セキュリティ

**このリポジトリには機密情報は含まれていません。**

除外されているファイル:
- `.env` - SECRET_KEY、Google Client Secretなど
- `app.db` - ユーザーデータベース
- `venv/` - Python仮想環境
- `__pycache__/` - Pythonキャッシュ

詳細は [SECURITY.md](SECURITY.md) を参照してください。

## 📁 プロジェクト構造

```
RFP-ask_test-back/
├── main.py              # FastAPIアプリケーション
├── models.py            # データベースモデル
├── schemas.py           # Pydanticスキーマ
├── auth.py              # 認証ロジック
├── database.py          # DB接続設定
├── seed_data.py         # テストデータ作成
├── test_login.py        # ログインテスト
├── requirements.txt     # Python依存パッケージ
├── .env.example         # 環境変数テンプレート
├── .env                 # 環境変数（Git除外）
├── .gitignore           # Git除外設定
├── README.md            # プロジェクト説明
├── SECURITY.md          # セキュリティ情報
└── GITHUB_SETUP.md      # このファイル
```

## 🌐 API エンドポイント

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| GET | `/` | API情報 | 不要 |
| GET | `/health` | ヘルスチェック | 不要 |
| POST | `/auth/login` | メール/パスワードログイン | 不要 |
| POST | `/auth/google` | Googleログイン | 不要 |
| POST | `/auth/logout` | ログアウト | 必要 |
| GET | `/auth/me` | 現在のユーザー情報 | 必要 |

## 🧪 テストアカウント

| 役割 | メールアドレス | パスワード | ロール |
|-----|--------------|-----------|--------|
| 生徒 | student1@example.com | password123 | 0 |
| 生徒 | student2@example.com | password123 | 0 |
| 先生 | teacher1@example.com | password123 | 1 |

## 🛠️ トラブルシューティング

### "ModuleNotFoundError"

```bash
# 仮想環境が有効化されているか確認
# (venv)が表示されていることを確認

# 依存パッケージを再インストール
pip install -r requirements.txt
```

### "Database is locked"

```bash
# データベースファイルを削除して再作成
del app.db  # Windows
# rm app.db  # macOS/Linux

python seed_data.py
```

### ポート8000が使用中

```bash
# 別のポートで起動
uvicorn main:app --reload --port 8001
```

## 🚀 本番デプロイ

### 環境変数の設定

本番環境では`.env`ファイルではなく、環境変数として設定:

```bash
# Heroku
heroku config:set SECRET_KEY="your-production-secret-key"

# AWS
# Systems Manager Parameter Storeを使用

# Docker
# docker-compose.ymlで環境変数を設定
```

### データベース

本番環境ではPostgreSQLやMySQLを使用することを推奨:

```python
# database.py を変更
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

## 📞 サポート

問題が解決しない場合は、GitHubのIssuesで報告してください。

**セキュリティ上の問題は公開Issueには書かないでください。**
