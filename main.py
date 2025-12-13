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
    UserUpdateRequest
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
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
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
        created_at=current_user.created_at
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
