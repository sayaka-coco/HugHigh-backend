from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for Google-only users
    name = Column(String, nullable=True)  # User's full name
    class_name = Column(String, nullable=True)  # Class name for students (e.g., "1-A")
    role = Column(Integer, nullable=False)  # 0: Student, 1: Teacher, 2: Admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    google_account = relationship("UserGoogleAccount", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    questionnaires = relationship("Questionnaire", back_populates="user")
    monthly_results = relationship("MonthlyResult", back_populates="user")
    talent_result = relationship("TalentResult", back_populates="user", uselist=False)


class UserGoogleAccount(Base):
    __tablename__ = "user_google_accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    google_sub = Column(String, unique=True, nullable=False, index=True)  # Google's subject ID
    google_email = Column(String, nullable=False)
    profile_picture_url = Column(String, nullable=True)
    linked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="google_account")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # e.g., "login", "logout", "login_failed"
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    week = Column(Integer, nullable=False)  # Week number
    title = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(String, default="pending", nullable=False)  # "pending" or "completed"
    answers = Column(JSON, nullable=True)  # JSON field for answers
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="questionnaires")


class MonthlyResult(Base):
    __tablename__ = "monthly_results"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    year = Column(Integer, nullable=False)  # Year (e.g., 2024)
    month = Column(Integer, nullable=False)  # Month (1-12)
    level = Column(Integer, nullable=False)  # Overall level
    skills = Column(JSON, nullable=False)  # Skills data: {"戦略的計画力": 58, "課題設定・構想力": 65, ...}
    ai_comment = Column(Text, nullable=True)  # AI generated comment
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="monthly_results")


class TalentResult(Base):
    __tablename__ = "talent_results"

    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    talent_type = Column(String, nullable=False)  # e.g., "未来を創造する革新者"
    talent_name = Column(String, nullable=False)  # e.g., "構想力"
    description = Column(Text, nullable=False)  # Talent description
    keywords = Column(JSON, nullable=False)  # Keywords: ["戦略", "アイデア", "ビジョン", "リーダーシップ"]
    strengths = Column(JSON, nullable=False)  # Strengths list
    next_steps = Column(JSON, nullable=False)  # Next steps list
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="talent_result")
