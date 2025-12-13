from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from database import get_db
from models import User, TalentResult
from schemas import TalentResultResponse, TalentResultCreate
from auth import get_current_user

router = APIRouter(prefix="/talent-result", tags=["talent-result"])


@router.get("", response_model=TalentResultResponse | None)
def get_talent_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the talent result for the current user."""
    result = db.query(TalentResult).filter(
        TalentResult.user_id == current_user.id
    ).first()

    return result


@router.post("", response_model=TalentResultResponse)
def create_or_update_talent_result(
    talent_data: TalentResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update talent result for the current user."""
    # Check if result already exists
    existing_result = db.query(TalentResult).filter(
        TalentResult.user_id == current_user.id
    ).first()

    if existing_result:
        # Update existing result
        existing_result.talent_type = talent_data.talent_type
        existing_result.talent_name = talent_data.talent_name
        existing_result.description = talent_data.description
        existing_result.keywords = talent_data.keywords
        existing_result.strengths = talent_data.strengths
        existing_result.next_steps = talent_data.next_steps

        db.commit()
        db.refresh(existing_result)
        return existing_result
    else:
        # Create new result
        new_result = TalentResult(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            talent_type=talent_data.talent_type,
            talent_name=talent_data.talent_name,
            description=talent_data.description,
            keywords=talent_data.keywords,
            strengths=talent_data.strengths,
            next_steps=talent_data.next_steps
        )

        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        return new_result
