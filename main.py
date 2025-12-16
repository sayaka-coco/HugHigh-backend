from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database import get_db, engine, Base
from models import User, UserGoogleAccount, AuditLog
from schemas import (
    LoginRequest, LoginResponse, UserResponse,
    GoogleLoginRequest, Token, UserCreateRequest, UserCreateGoogleRequest,
    UserUpdateRequest, ProfileUpdateRequest
)
from auth import (
    verify_password, create_access_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
)
from questionnaire_routes import router as questionnaire_router
from monthly_result_routes import router as monthly_result_router
from talent_result_routes import router as talent_result_router

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HugHigh Login API", version="1.0.0")

# Include routers
app.include_router(questionnaire_router)
app.include_router(monthly_result_router)
app.include_router(talent_result_router)

# CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://hughigh-app-frontend.azurewebsites.net")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://hughigh-app-frontend.azurewebsites.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


def create_audit_log(db: Session, user_id: str, action: str, ip_address: str = None):
    """Helper function to create audit log entries."""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address
    )
    db.add(audit_log)
    db.commit()


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "HugHigh Login API",
        "version": "1.0.0",
        "endpoints": {
            "login": "/auth/login",
            "google_login": "/auth/google",
            "logout": "/auth/logout",
            "me": "/auth/me"
        }
    }


@app.post("/auth/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Email + Password login endpoint.

    - Verifies user credentials
    - Creates JWT access token
    - Logs the login action
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        # Log failed login attempt (without user_id since user not found)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not user.hashed_password or not verify_password(login_data.password, user.hashed_password):
        # Log failed login
        create_audit_log(db, user.id, "login_failed", request.client.host if request.client else None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    # Log successful login
    create_audit_log(db, user.id, "login", request.client.host if request.client else None)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            class_name=user.class_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@app.post("/auth/google", response_model=LoginResponse)
def google_login(
    google_data: GoogleLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Google OAuth login endpoint.

    - Verifies Google ID token
    - Creates or retrieves user account
    - Links Google account if not already linked
    - Creates JWT access token
    """
    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            google_data.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Extract Google user info
        google_sub = idinfo['sub']
        google_email = idinfo['email']
        google_name = idinfo.get('name', None)
        profile_picture = idinfo.get('picture', None)

        # Check if Google account already exists
        google_account = db.query(UserGoogleAccount).filter(
            UserGoogleAccount.google_sub == google_sub
        ).first()

        if google_account:
            # User already exists with this Google account
            user = google_account.user
            # Update user name from Google profile
            if google_name:
                user.name = google_name
                db.commit()
        else:
            # Check if user exists with this email (for linking)
            user = db.query(User).filter(User.email == google_email).first()

            if user:
                # Link existing user with Google account
                new_google_account = UserGoogleAccount(
                    user_id=user.id,
                    google_sub=google_sub,
                    google_email=google_email,
                    profile_picture_url=profile_picture
                )
                # Update user name from Google profile
                if google_name:
                    user.name = google_name
                db.add(new_google_account)
                db.commit()
            else:
                # User does not exist - reject login
                # Only admin can create new users
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User not registered. Please contact administrator to create an account."
                )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )

        # Log successful login
        create_audit_log(db, user.id, "google_login", request.client.host if request.client else None)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                class_name=user.class_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )

    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Google login: {str(e)}"
        )


@app.post("/auth/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint.

    - Logs the logout action
    - In JWT implementation, actual token invalidation happens client-side
    """
    # Log logout
    create_audit_log(db, current_user.id, "logout", request.client.host if request.client else None)

    return {"message": "Successfully logged out"}


@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    - Returns user details based on JWT token
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        class_name=current_user.class_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        profile_image=current_user.profile_image,
        hobbies=current_user.hobbies,
        current_focus=current_user.current_focus
    )


@app.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's own profile information.

    - Updates profile image, hobbies, and current focus areas
    - Any user can update their own profile
    """
    # Update profile fields
    if profile_data.profile_image is not None:
        current_user.profile_image = profile_data.profile_image
    if profile_data.hobbies is not None:
        # Validate max 50 characters
        if len(profile_data.hobbies) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="趣味・特技は50文字以内で入力してください"
            )
        current_user.hobbies = profile_data.hobbies
    if profile_data.current_focus is not None:
        current_user.current_focus = profile_data.current_focus

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        class_name=current_user.class_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        profile_image=current_user.profile_image,
        hobbies=current_user.hobbies,
        current_focus=current_user.current_focus
    )


@app.post("/admin/users/email", response_model=UserResponse)
def create_user_with_email(
    user_data: UserCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to create a new user with email/password authentication.

    - Only Admin (role=2) can access this endpoint
    - Creates a new user with the provided credentials
    - Logs the action in audit log
    """
    # Check if current user is admin
    if current_user.role != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Validate role
    if user_data.role not in [0, 1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 0 (Student), 1 (Teacher), or 2 (Admin)"
        )

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        name=user_data.name,
        class_name=user_data.class_name if user_data.role == 0 else None,
        role=user_data.role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log the action
    create_audit_log(
        db,
        current_user.id,
        f"create_user_email:{new_user.email}",
        request.client.host if request.client else None
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        class_name=new_user.class_name,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@app.post("/admin/users/google", response_model=UserResponse)
def create_user_with_google(
    user_data: UserCreateGoogleRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to create a new user for Google OAuth authentication.

    - Only Admin (role=2) can access this endpoint
    - Creates a new user account (no Google account link initially)
    - User will link Google account on first Google OAuth login
    - Logs the action in audit log
    """
    # Check if current user is admin
    if current_user.role != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Validate role
    if user_data.role not in [0, 1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 0 (Student), 1 (Teacher), or 2 (Admin)"
        )

    # Create new user (without password for Google-only auth)
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=None,  # No password for Google-only users
        name=user_data.name,
        class_name=user_data.class_name if user_data.role == 0 else None,
        role=user_data.role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log the action
    create_audit_log(
        db,
        current_user.id,
        f"create_user_google:{new_user.email}",
        request.client.host if request.client else None
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        class_name=new_user.class_name,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@app.get("/admin/users", response_model=list[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to list all users.

    - Only Admin (role=2) can access this endpoint
    - Returns all users in the system
    """
    # Check if current user is admin
    if current_user.role != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view users"
        )

    users = db.query(User).all()
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            class_name=user.class_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]


@app.get("/admin/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to get a specific user by ID.

    - Only Admin (role=2) can access this endpoint
    - Returns user details
    """
    # Check if current user is admin
    if current_user.role != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view user details"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        class_name=user.class_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


@app.put("/admin/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_data: UserUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to update user information.

    - Only Admin (role=2) can access this endpoint
    - Updates name, role, class_name, or is_active status
    - Cannot update the admin themselves
    - Logs the action in audit log
    """
    # Check if current user is admin
    if current_user.role != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update users"
        )

    # Prevent admin from updating themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update your own account this way"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.role is not None:
        if user_data.role not in [0, 1, 2]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        user.role = user_data.role
    if user_data.class_name is not None:
        user.class_name = user_data.class_name
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)

    # Log the action
    create_audit_log(
        db,
        current_user.id,
        f"update_user:{user.email}",
        request.client.host if request.client else None
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        class_name=user.class_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


@app.delete("/admin/users/{user_id}")
def delete_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to delete a user.

    - Only Admin (role=2) can access this endpoint
    - Cannot delete the admin themselves
    - Deletes user and associated records
    - Logs the action in audit log
    """
    # Check if current user is admin
    if current_user.role != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users"
        )

    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_email = user.email

    # Delete associated Google accounts
    db.query(UserGoogleAccount).filter(UserGoogleAccount.user_id == user_id).delete()

    # Delete associated audit logs
    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete()

    # Delete user
    db.delete(user)
    db.commit()

    # Log the action
    create_audit_log(
        db,
        current_user.id,
        f"delete_user:{user_email}",
        request.client.host if request.client else None
    )

    return {"message": f"User {user_email} deleted successfully"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Student Schema
from pydantic import BaseModel

class StudentResponse(BaseModel):
    id: str
    name: str
    email: str
    class_name: str | None = None


@app.get("/students", response_model=list[StudentResponse])
def get_students(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all students for team member selection.

    - Returns all active students
    - Excludes the current user from the list
    """
    # Get all students (role=0), excluding current user
    students = db.query(User).filter(
        User.role == 0,  # Students only
        User.id != current_user.id,
        User.is_active == True
    ).all()

    return [
        StudentResponse(
            id=user.id,
            name=user.name or user.email,
            email=user.email,
            class_name=user.class_name
        )
        for user in students
    ]


# OpenAI Evaluation for "謙虚である力"
from typing import Optional

# Optional OpenAI import - works without it installed
try:
    from openai import OpenAI
    import httpx
    _http_client = httpx.Client(proxy=None)
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    _http_client = None
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class GratitudeTargetInput(BaseModel):
    student_name: str
    message: str

class HumilityEvaluationRequest(BaseModel):
    gratitude_targets: list[GratitudeTargetInput] = []
    weakness: Optional[str] = None

class HumilityEvaluationResponse(BaseModel):
    total_score: int
    gratitude_count_score: int
    gratitude_content_score: int
    weakness_score: int
    details: dict


def evaluate_content_with_ai(content: str, content_type: str, max_score: int) -> int:
    """Use OpenAI to evaluate the specificity/quality of content."""
    if not content or not content.strip():
        return 0

    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        # Fallback if OpenAI not available or no API key - give partial score
        return max_score // 2

    try:
        client = OpenAI(api_key=OPENAI_API_KEY, http_client=_http_client)

        if content_type == "gratitude":
            prompt = f"""以下の感謝メッセージの具体性を評価してください。
評価基準:
- 具体的なエピソードや行動が書かれているか
- 感謝の理由が明確か
- 相手への気持ちが伝わる内容か

感謝メッセージ:
{content}

0から{max_score}点で評価し、数値のみを返してください。
- 0点: 空欄または意味のない内容
- 1-{max_score//3}点: 抽象的で具体性がない
- {max_score//3+1}-{max_score*2//3}点: ある程度具体的
- {max_score*2//3+1}-{max_score}点: 非常に具体的で心のこもった内容

数値のみ回答:"""
        else:  # weakness
            prompt = f"""以下の「自分の弱み」の記述の具体性を評価してください。
評価基準:
- 具体的な弱点が明確に書かれているか
- 改善の意識が見られるか
- 自己認識の深さが感じられるか

弱みの記述:
{content}

0から{max_score}点で評価し、数値のみを返してください。
- 0点: 空欄または意味のない内容
- 1-{max_score//3}点: 抽象的で具体性がない
- {max_score//3+1}-{max_score*2//3}点: ある程度具体的
- {max_score*2//3+1}-{max_score}点: 非常に具体的で自己分析ができている

数値のみ回答:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは教育評価の専門家です。指示に従って評価点数のみを返してください。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.3
        )

        result = response.choices[0].message.content.strip()
        # Extract number from response
        import re
        numbers = re.findall(r'\d+', result)
        if numbers:
            score = int(numbers[0])
            return min(score, max_score)  # Ensure it doesn't exceed max
        return max_score // 2  # Fallback

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return max_score // 2  # Fallback score


@app.post("/evaluate-humility", response_model=HumilityEvaluationResponse)
def evaluate_humility(
    request: HumilityEvaluationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate "謙虚である力" (Humility) score based on:
    - Gratitude targets from questionnaire (70%):
      - Count: 0=0pts, 1=5pts, 2=10pts, 3+=15pts
      - Content: Up to 55 points for specificity
    - Weakness description (30%): Up to 30 points for specificity

    Total: 100 points
    """

    # 1. Calculate gratitude count score (15 points max)
    gratitude_count = len(request.gratitude_targets)
    if gratitude_count == 0:
        gratitude_count_score = 0
    elif gratitude_count == 1:
        gratitude_count_score = 5
    elif gratitude_count == 2:
        gratitude_count_score = 10
    else:  # 3 or more
        gratitude_count_score = 15

    # 2. Calculate gratitude content score (55 points max)
    gratitude_content_score = 0
    if gratitude_count > 0:
        # Distribute 55 points across all messages
        points_per_message = 55 // max(gratitude_count, 1)
        for target in request.gratitude_targets:
            message_score = evaluate_content_with_ai(
                target.message,
                "gratitude",
                points_per_message
            )
            gratitude_content_score += message_score
        # Cap at 55
        gratitude_content_score = min(gratitude_content_score, 55)

    # 3. Calculate weakness score (30 points max)
    weakness_score = 0
    if request.weakness and request.weakness.strip():
        weakness_score = evaluate_content_with_ai(
            request.weakness,
            "weakness",
            30
        )

    # Total score
    total_score = gratitude_count_score + gratitude_content_score + weakness_score

    return HumilityEvaluationResponse(
        total_score=total_score,
        gratitude_count_score=gratitude_count_score,
        gratitude_content_score=gratitude_content_score,
        weakness_score=weakness_score,
        details={
            "gratitude_count": gratitude_count,
            "gratitude_messages": [t.message for t in request.gratitude_targets],
            "weakness_text": request.weakness or ""
        }
    )


# Skill Advice Generation API
class SkillAdviceRequest(BaseModel):
    skills: dict  # {"戦略的計画力": 75, "課題設定・構想力": 100, ...}


class SkillAdviceResponse(BaseModel):
    advice: dict  # {"戦略的計画力": "アドバイス文...", ...}


@app.post("/generate-skill-advice", response_model=SkillAdviceResponse)
def generate_skill_advice(
    request: SkillAdviceRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized advice for each skill based on the score using AI.
    """
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        # Fallback to static advice if OpenAI not available or no API key
        return SkillAdviceResponse(advice={
            skill: get_fallback_advice(skill, score)
            for skill, score in request.skills.items()
        })

    try:
        client = OpenAI(api_key=OPENAI_API_KEY, http_client=_http_client)

        # Build prompt with all skills
        skills_text = "\n".join([f"- {skill}: {score}点" for skill, score in request.skills.items()])

        prompt = f"""あなたは高校生の非認知能力を育成する教育コーチです。
以下の7つの力のスコア（100点満点）に対して、それぞれ個別にパーソナライズされたアドバイスを生成してください。

【生徒のスコア】
{skills_text}

【各スキルの説明】
- 戦略的計画力: 目標に向けて計画を立て、優先順位をつけて行動する力
- 課題設定・構想力: 問題を発見し、解決すべき課題を明確にする力
- 巻き込む力: 周囲の人を巻き込み、チームで成果を出す力
- 対話する力: 相手の話を傾聴し、自分の考えを伝える力
- 実行する力: 計画を実際の行動に移し、粘り強く取り組む力
- 完遂する力: 困難があっても最後までやり遂げる力
- 謙虚である力: 自分の弱さを認め、他者から学ぶ姿勢

【アドバイスのルール】
1. 各スキルに対して1-2文の短いアドバイスを書く
2. スコアが高い場合（70点以上）は褒めつつ次のステップを提案
3. スコアが中程度（40-69点）は具体的な改善ポイントを提案
4. スコアが低い場合（40点未満）は励ましと小さな一歩を提案
5. 同じような文言の繰り返しを避け、各スキルで異なる表現を使う
6. 高校生に語りかけるような親しみやすい口調で

【出力形式】
JSON形式で出力してください：
{{"戦略的計画力": "アドバイス...", "課題設定・構想力": "アドバイス...", ...}}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは高校生を支援する教育コーチです。JSON形式で回答してください。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        result = response.choices[0].message.content.strip()

        # Parse JSON from response
        import json
        import re

        # Try to extract JSON from the response
        json_match = re.search(r'\{[^{}]*\}', result, re.DOTALL)
        if json_match:
            advice_dict = json.loads(json_match.group())
            return SkillAdviceResponse(advice=advice_dict)

        # If JSON parsing fails, return fallback
        return SkillAdviceResponse(advice={
            skill: get_fallback_advice(skill, score)
            for skill, score in request.skills.items()
        })

    except Exception as e:
        print(f"OpenAI API error in generate_skill_advice: {e}")
        return SkillAdviceResponse(advice={
            skill: get_fallback_advice(skill, score)
            for skill, score in request.skills.items()
        })


def get_fallback_advice(skill: str, score: int) -> str:
    """Fallback advice when OpenAI is not available."""
    if score >= 70:
        return f"{skill}が順調に伸びています！この調子で続けていきましょう。"
    elif score >= 40:
        return f"{skill}を少しずつ伸ばしていきましょう。意識して取り組むことが大切です。"
    else:
        return f"{skill}はこれから伸ばせる分野です。小さな一歩から始めてみましょう。"
