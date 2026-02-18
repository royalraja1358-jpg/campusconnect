from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, LeaveApplication, Notification
from app.schemas.schemas import LeaveCreate, LeaveOut

router = APIRouter(prefix="/api/leave", tags=["Leave"])


@router.get("", response_model=List[LeaveOut])
def get_leave_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(LeaveApplication).filter(
        LeaveApplication.student_id == current_user.id
    ).order_by(LeaveApplication.applied_at.desc()).all()


@router.post("", response_model=LeaveOut)
def apply_leave(
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if data.to_date < data.from_date:
        raise HTTPException(400, "To date must be after from date")

    leave = LeaveApplication(
        student_id=current_user.id,
        leave_type=data.leave_type,
        from_date=data.from_date,
        to_date=data.to_date,
        reason=data.reason,
        status="pending",
    )
    db.add(leave)

    # Create notification
    notif = Notification(
        user_id=current_user.id,
        title="Leave Application Submitted",
        body=f"Your {data.leave_type} application ({data.from_date} to {data.to_date}) has been submitted.",
        notif_type="leave",
    )
    db.add(notif)
    db.commit()
    db.refresh(leave)
    return leave


@router.delete("/{leave_id}")
def cancel_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    leave = db.query(LeaveApplication).filter(
        LeaveApplication.id == leave_id,
        LeaveApplication.student_id == current_user.id
    ).first()
    if not leave:
        raise HTTPException(404, "Leave application not found")
    if leave.status != "pending":
        raise HTTPException(400, "Only pending applications can be cancelled")
    db.delete(leave)
    db.commit()
    return {"message": "Leave application cancelled"}
