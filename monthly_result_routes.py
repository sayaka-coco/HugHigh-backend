from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, MonthlyResult
from schemas import MonthlyResultResponse
from auth import get_current_user

router = APIRouter(prefix="/monthly-results", tags=["monthly-results"])


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
