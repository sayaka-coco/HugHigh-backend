"""
Check Google OAuth user setup
"""

import sys
import io
from database import SessionLocal
from models import User, UserGoogleAccount

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = SessionLocal()

# Check sayacoco0326@gmail.com user
user = db.query(User).filter(User.email == 'sayacoco0326@gmail.com').first()
if user:
    print('OK - ユーザーが見つかりました')
    print(f'  Email: {user.email}')
    print(f'  Name: {user.name}')
    print(f'  Role: {user.role}')
    print(f'  Has password: {user.hashed_password is not None}')

    # Check Google account link
    google_account = db.query(UserGoogleAccount).filter(UserGoogleAccount.user_id == user.id).first()
    if google_account:
        print('  OK - Google account linked')
        print(f'     Google Email: {google_account.google_email}')
        print(f'     Google Sub: {google_account.google_sub}')
    else:
        print('  Note - Google account NOT linked yet')
        print('         (will be linked on first Google login)')
else:
    print('Error - ユーザーが見つかりません')

db.close()
