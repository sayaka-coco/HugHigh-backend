# HugHigh Backend API_1

FastAPI を使用した認証バックエンド

## 🚀 クイックスタート

### 0. リポジトリのクローン（初回のみ）

```bash
git clone https://github.com/sayaka-coco/RFP-ask_test-back.git
cd RFP-ask_test-back
```

## セットアップ

### 1. 仮想環境の作成と有効化

```bash
# 仮想環境の作成
python -m venv venv

# 有効化 (Windows)
venv\Scripts\activate

# 有効化 (macOS/Linux)
source venv/bin/activate
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env`を作成:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

`.env` ファイルを編集し、必要な設定を行ってください:

```bash
# SECRET_KEYを強力なランダム値に変更
SECRET_KEY=your-secret-key-here

# Google OAuth（オプション）
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**重要:** `.env`ファイルは機密情報を含むため、Gitにコミットされません。

**SECRET_KEYの生成:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. データベースの初期化

```bash
python seed_data.py
```

### 5. サーバーの起動

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

サーバーは http://localhost:8000 で起動します。

## API ドキュメント

起動後、以下のURLでSwagger UIにアクセスできます:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## テストアカウント

- 生徒1: student1@example.com / password123
- 生徒2: student2@example.com / password123
- 先生1: teacher1@example.com / password123

## ファイル構成

- `main.py` - FastAPI アプリケーションとエンドポイント
- `models.py` - SQLAlchemy データベースモデル
- `schemas.py` - Pydantic スキーマ（リクエスト/レスポンス）
- `auth.py` - 認証ロジック（JWT、パスワードハッシュ化）
- `database.py` - データベース接続設定
- `seed_data.py` - テストデータ作成スクリプト
- `requirements.txt` - 必要なPythonパッケージ
