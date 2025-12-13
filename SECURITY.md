# セキュリティに関する重要な注意事項

## 🔒 機密情報の管理

このリポジトリには**機密情報は一切含まれていません**。

### ⚠️ 絶対にコミットしてはいけないファイル

以下のファイルは`.gitignore`により、Gitリポジトリから**完全に除外**されています:

1. **`.env`** - 環境変数ファイル（**最重要**）
   - JWT SECRET_KEY（暗号化キー）
   - Google OAuth Client Secret
   - その他の機密設定
   - **このファイルを公開すると重大なセキュリティリスクがあります**

2. **`app.db`** - SQLiteデータベースファイル
   - ユーザーのハッシュ化されたパスワード
   - 個人情報
   - 監査ログ

3. **`venv/`** - Python仮想環境
   - 大容量のため除外
   - `requirements.txt`から再作成可能

4. **`__pycache__/`** - Pythonキャッシュ
   - 自動生成されるファイル

## ✅ 安全な使用方法

### 初回セットアップ

```bash
# 1. .env.exampleをコピー
cp .env.example .env

# 2. .envファイルを編集して実際の値を設定
# SECRET_KEYを強力なランダム値に変更
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 3. Google OAuth設定（オプション）
# https://console.cloud.google.com/ で取得
```

### SECRET_KEYの重要性

**SECRET_KEY**は以下の目的で使用されます:
- JWTトークンの署名・検証
- セッションの暗号化

**要件:**
- 最低32文字以上のランダムな文字列
- 推測不可能であること
- 本番環境では必ず変更すること
- **絶対に公開しないこと**

**生成方法:**
```python
import secrets
print(secrets.token_urlsafe(32))
# 例: kX9sT2mP4nQ8vL3wR5yH7jK1bN6cZ9fG4dS8aE2xW
```

### Google OAuth Secretの取扱い

**GOOGLE_CLIENT_SECRET**:
- Google Cloud Consoleから取得
- クライアントIDと異なり、**完全に秘密にする必要があります**
- フロントエンドには**絶対に含めないこと**
- バックエンドでのみ使用

## 📋 セキュリティチェックリスト

コミット前に必ず確認:

- [ ] `.env`ファイルがコミットされていない
- [ ] `app.db`がコミットされていない
- [ ] `venv/`が除外されている
- [ ] SECRET_KEYが含まれていない
- [ ] Google Client Secretが含まれていない
- [ ] パスワードやAPIキーが含まれていない

### 確認コマンド

```bash
# Gitに追跡されているファイルを確認
git ls-files

# .envや.dbファイルが含まれていないことを確認
git ls-files | grep -E "\\.env|\\.db"
# 何も表示されなければOK
```

## 🛡️ 本番環境での対策

### 1. 環境変数の設定

本番環境では、ファイルではなく環境変数として設定:

```bash
# 例: Heroku
heroku config:set SECRET_KEY="your-production-secret-key"
heroku config:set GOOGLE_CLIENT_SECRET="your-client-secret"

# 例: AWS
# AWS Systems Manager Parameter Storeを使用

# 例: Docker
# docker-compose.ymlで環境変数を設定（.envは含めない）
```

### 2. SECRET_KEYの定期変更

- 定期的に変更（推奨: 3-6ヶ月ごと）
- 漏洩の疑いがある場合は即座に変更
- 変更後は全ユーザーの再ログインが必要

### 3. データベースのセキュリティ

- 本番環境ではSQLiteではなくPostgreSQLやMySQLを使用
- データベースへのアクセスを制限
- 定期的なバックアップ

## 🚨 セキュリティインシデント発生時

もし機密情報を誤ってコミットした場合:

### 1. Git履歴から完全に削除

```bash
# 注意: この操作は不可逆です
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# または BFG Repo-Cleanerを使用
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### 2. 強制プッシュ

```bash
git push origin --force --all
git push origin --force --tags
```

### 3. 機密情報の無効化

- SECRET_KEYを即座に変更
- Google OAuth Credentialsを無効化・再生成
- データベースパスワードを変更
- 全ユーザーにログアウトを強制

### 4. 影響範囲の調査

- アクセスログを確認
- 不正アクセスの有無をチェック
- 必要に応じてインシデント報告

## 📞 問題報告

セキュリティ上の問題を発見した場合:

1. **公開Issueには書かない**
2. プライベートな方法で報告（例: メール）
3. 詳細な情報を提供（再現手順など）

## ✅ 推奨事項

- [ ] `.gitignore`の内容を理解する
- [ ] コミット前に`git status`で確認
- [ ] 定期的にセキュリティ監査を実施
- [ ] 依存パッケージを最新に保つ
- [ ] ログを監視する
