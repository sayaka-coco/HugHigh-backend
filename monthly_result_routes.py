from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import uuid

from database import get_db
from models import User, MonthlyResult, Questionnaire
from schemas import MonthlyResultResponse
from auth import get_current_user

router = APIRouter(prefix="/monthly-results", tags=["monthly-results"])


def calculate_skills_from_questionnaires(questionnaires: list, humility_score: int = 0) -> dict:
    """Calculate skill scores from questionnaire answers."""
    if not questionnaires:
        return {
            "戦略的計画力": 0,
            "課題設定・構想力": 0,
            "巻き込む力": 0,
            "対話する力": 0,
            "実行する力": 0,
            "完遂する力": 0,
            "謙虚である力": humility_score,
        }

    total_q1_score = 0
    q1_count = 0
    interview_conducted_count = 0
    interview_received_count = 0
    could_extract_count = 0
    could_speak_count = 0
    extract_attempt_count = 0
    speak_attempt_count = 0

    for q in questionnaires:
        answers = q.answers
        if not answers:
            continue

        # Q1: 計画通りに行動できたか (1-5)
        if answers.get("q1") is not None:
            total_q1_score += answers["q1"]
            q1_count += 1

        # Q3: インタビュー
        if answers.get("q3_didConduct"):
            interview_conducted_count += 1
            if answers.get("q3_couldExtract") is not None:
                extract_attempt_count += 1
                if answers["q3_couldExtract"]:
                    could_extract_count += 1

        if answers.get("q3_didReceive"):
            interview_received_count += 1
            if answers.get("q3_couldSpeak") is not None:
                speak_attempt_count += 1
                if answers["q3_couldSpeak"]:
                    could_speak_count += 1

    # スコア計算 (0-100)
    strategic_planning = round(((total_q1_score / q1_count) - 1) / 4 * 100) if q1_count > 0 else 0
    execution = round(((total_q1_score / q1_count) - 1) / 4 * 100) if q1_count > 0 else 0

    max_interviews = len(questionnaires) * 2
    total_interviews = interview_conducted_count + interview_received_count
    involvement = round((total_interviews / max_interviews) * 100) if max_interviews > 0 else 0

    extract_rate = could_extract_count / extract_attempt_count if extract_attempt_count > 0 else 0
    speak_rate = could_speak_count / speak_attempt_count if speak_attempt_count > 0 else 0
    dialogue_attempts = extract_attempt_count + speak_attempt_count
    dialogue = round(((extract_rate + speak_rate) / 2) * 100) if dialogue_attempts > 0 else 0

    problem_setting = round((could_extract_count / extract_attempt_count) * 100) if extract_attempt_count > 0 else 0

    # 完遂する力は全体のアンケート完了率で計算
    completion = 100  # 確定時は全て完了しているはず

    return {
        "戦略的計画力": strategic_planning,
        "課題設定・構想力": problem_setting,
        "巻き込む力": involvement,
        "対話する力": dialogue,
        "実行する力": execution,
        "完遂する力": completion,
        "謙虚である力": humility_score,
    }


def calculate_level(skills: dict) -> int:
    """Calculate overall level from skill scores (average / 20 + 1, max 5)."""
    scores = list(skills.values())
    avg_score = sum(scores) / len(scores) if scores else 0
    level = int(avg_score / 20) + 1
    return min(level, 5)


def generate_ai_comment(skills: dict) -> str:
    """Generate AI comment based on skills."""
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    top_skill = sorted_skills[0] if sorted_skills else None
    bottom_skill = sorted_skills[-1] if sorted_skills else None

    if not top_skill or top_skill[1] == 0:
        return "アンケートへの回答を続けることで、より詳細な分析ができるようになります。"

    comment = f"今月は「{top_skill[0]}」が最も高いスコア（{top_skill[1]}点）でした。"

    if bottom_skill and bottom_skill[1] < top_skill[1]:
        comment += f" 「{bottom_skill[0]}」を伸ばすことで、さらにバランスの良い成長が期待できます。"

    return comment


@router.get("", response_model=list[MonthlyResultResponse])
def get_monthly_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all monthly results for the current user.
    Students can only see their own, teachers can see all.
    """
    if current_user.role == 0:  # Student
        results = db.query(MonthlyResult).filter(
            MonthlyResult.user_id == current_user.id
        ).order_by(MonthlyResult.year.desc(), MonthlyResult.month.desc()).all()
    else:  # Teacher or Admin
        results = db.query(MonthlyResult).order_by(
            MonthlyResult.year.desc(), MonthlyResult.month.desc()
        ).all()

    return results


@router.get("/{result_id}", response_model=MonthlyResultResponse)
def get_monthly_result(
    result_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific monthly result by ID."""
    result = db.query(MonthlyResult).filter(
        MonthlyResult.id == result_id
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monthly result not found"
        )

    # Check permissions
    if current_user.role == 0 and result.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return result


@router.post("/finalize", response_model=MonthlyResultResponse)
def finalize_monthly_result(
    year: Optional[int] = None,
    month: Optional[int] = None,
    humility_score: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalize and save the monthly result for the current user.
    If year/month not specified, uses the current month.
    """
    # Default to current month if not specified
    now = datetime.utcnow()
    target_year = year if year else now.year
    target_month = month if month else now.month

    # Check if already finalized for this month
    existing = db.query(MonthlyResult).filter(
        MonthlyResult.user_id == current_user.id,
        MonthlyResult.year == target_year,
        MonthlyResult.month == target_month
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{target_year}年{target_month}月の結果は既に確定済みです"
        )

    # Get completed questionnaires for the target month
    questionnaires = db.query(Questionnaire).filter(
        Questionnaire.user_id == current_user.id,
        Questionnaire.status == "completed"
    ).all()

    # Filter questionnaires for the target month
    monthly_questionnaires = [
        q for q in questionnaires
        if q.created_at.year == target_year and q.created_at.month == target_month
    ]

    if not monthly_questionnaires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{target_year}年{target_month}月のアンケートがありません"
        )

    # Calculate skills
    skills = calculate_skills_from_questionnaires(monthly_questionnaires, humility_score)
    level = calculate_level(skills)
    ai_comment = generate_ai_comment(skills)

    # Create monthly result
    monthly_result = MonthlyResult(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        year=target_year,
        month=target_month,
        level=level,
        skills=skills,
        ai_comment=ai_comment
    )

    db.add(monthly_result)
    db.commit()
    db.refresh(monthly_result)

    return monthly_result


@router.get("/current", response_model=Optional[MonthlyResultResponse])
def get_current_month_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the monthly result for the current month if it exists.
    Returns null if not yet finalized.
    """
    now = datetime.utcnow()

    result = db.query(MonthlyResult).filter(
        MonthlyResult.user_id == current_user.id,
        MonthlyResult.year == now.year,
        MonthlyResult.month == now.month
    ).first()

    return result
