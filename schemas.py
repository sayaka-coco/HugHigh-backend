from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: int  # 0: Student, 1: Teacher, 2: Admin


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    name: Optional[str] = None
    class_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    # Profile fields
    profile_image: Optional[str] = None
    hobbies: Optional[str] = None
    current_focus: Optional[list[str]] = None

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """Schema for admin creating new users"""
    email: EmailStr
    password: str
    name: str
    role: int  # 0: Student, 1: Teacher, 2: Admin
    class_name: Optional[str] = None  # Only for students


class UserCreateGoogleRequest(BaseModel):
    """Schema for admin adding Google OAuth users"""
    email: EmailStr
    name: str
    role: int  # 0: Student, 1: Teacher, 2: Admin
    class_name: Optional[str] = None  # Only for students


class UserUpdateRequest(BaseModel):
    """Schema for admin updating user information"""
    name: Optional[str] = None
    role: Optional[int] = None
    class_name: Optional[str] = None
    is_active: Optional[bool] = None


class ProfileUpdateRequest(BaseModel):
    """Schema for user updating their own profile"""
    profile_image: Optional[str] = None  # Base64 encoded image
    hobbies: Optional[str] = None  # Max 50 characters
    current_focus: Optional[list[str]] = None  # Array of focus areas


# Login Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Google OAuth Schemas
class GoogleLoginRequest(BaseModel):
    credential: str  # Google ID token


class GoogleCallbackRequest(BaseModel):
    code: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[int] = None


# Audit Log Schemas
class AuditLogCreate(BaseModel):
    user_id: str
    action: str
    ip_address: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: str
    action: str
    ip_address: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


# Questionnaire Schemas
class GratitudeTarget(BaseModel):
    studentId: str
    studentName: str
    message: str


class QuestionnaireAnswers(BaseModel):
    # Q1: 計画通りに行動できたか
    q1: int
    # Q2: 感謝を伝えたい人
    q2_hasGratitude: bool
    q2_gratitudeTargets: Optional[list[GratitudeTarget]] = []
    # Legacy fields (for backward compatibility)
    q2_targetStudent: Optional[str] = ""
    q2_targetStudentId: Optional[str] = ""
    q2_message: Optional[str] = ""
    # Q3: インタビュー実施
    q3_didInterview: bool
    q3_didConduct: Optional[bool] = False
    q3_conductContent: Optional[str] = ""
    q3_couldExtract: Optional[bool] = None
    q3_extractedInsight: Optional[str] = ""
    q3_extractionChallenge: Optional[str] = ""
    q3_didReceive: Optional[bool] = False
    q3_receiveContent: Optional[str] = ""
    q3_couldSpeak: Optional[bool] = None
    q3_speakingInsight: Optional[str] = ""
    q3_speakingChallenge: Optional[str] = ""


class QuestionnaireResponse(BaseModel):
    id: str
    user_id: str
    week: int
    title: str
    deadline: datetime
    status: str  # 'pending' or 'completed'
    answers: Optional[dict] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionnaireSubmit(BaseModel):
    answers: QuestionnaireAnswers


# Monthly Result Schemas
class MonthlyResultResponse(BaseModel):
    id: str
    user_id: str
    year: int
    month: int
    level: int
    skills: dict  # {"戦略的計画力": 58, "課題設定・構想力": 65, ...}
    ai_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Talent Result Schemas
class TalentResultResponse(BaseModel):
    id: str
    user_id: str
    talent_type: str
    talent_name: str
    description: str
    keywords: list[str]
    strengths: list[str]
    next_steps: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TalentResultCreate(BaseModel):
    talent_type: str
    talent_name: str
    description: str
    keywords: list[str]
    strengths: list[str]
    next_steps: list[str]
