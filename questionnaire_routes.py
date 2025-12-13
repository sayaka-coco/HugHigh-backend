from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import User, Questionnaire
from schemas import QuestionnaireResponse, QuestionnaireSubmit
from auth import get_current_user

router = APIRouter(prefix="/questionnaires", tags=["questionnaires"])


@router.get("", response_model=list[QuestionnaireResponse])
def get_questionnaires(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all questionnaires for the current user.
    Students can only see their own, teachers can see all.
    """
    if current_user.role == 0:  # Student
        questionnaires = db.query(Questionnaire).filter(
            Questionnaire.user_id == current_user.id
        ).order_by(Questionnaire.week.desc()).all()
    else:  # Teacher or Admin
        questionnaires = db.query(Questionnaire).order_by(
            Questionnaire.week.desc()
        ).all()

    return questionnaires


@router.get("/{questionnaire_id}", response_model=QuestionnaireResponse)
def get_questionnaire(
    questionnaire_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific questionnaire by ID."""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()

    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )

    # Check permissions
    if current_user.role == 0 and questionnaire.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return questionnaire


@router.post("/{questionnaire_id}/submit", response_model=QuestionnaireResponse)
def submit_questionnaire(
    questionnaire_id: str,
    submission: QuestionnaireSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answers to a questionnaire."""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()

    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )

    # Check permissions
    if questionnaire.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own questionnaires"
        )

    # Check deadline
    if datetime.utcnow() > questionnaire.deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questionnaire deadline has passed"
        )

    # Update questionnaire
    questionnaire.answers = submission.answers.model_dump()
    questionnaire.status = "completed"
    questionnaire.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(questionnaire)

    return questionnaire


@router.put("/{questionnaire_id}", response_model=QuestionnaireResponse)
def update_questionnaire(
    questionnaire_id: str,
    submission: QuestionnaireSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update answers to a questionnaire (before deadline)."""
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == questionnaire_id
    ).first()

    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )

    # Check permissions
    if questionnaire.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own questionnaires"
        )

    # Check deadline
    if datetime.utcnow() > questionnaire.deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit after deadline"
        )

    # Update questionnaire
    questionnaire.answers = submission.answers.model_dump()
    questionnaire.status = "completed"
    if not questionnaire.submitted_at:
        questionnaire.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(questionnaire)

    return questionnaire
