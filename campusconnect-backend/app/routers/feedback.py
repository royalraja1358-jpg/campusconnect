from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Feedback, Subject
from app.schemas.schemas import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.get("", response_model=List[FeedbackOut])
def get_my_feedbacks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    feedbacks = db.query(Feedback).filter(
        Feedback.student_id == current_user.id
    ).all()
    return [FeedbackOut(
        id=f.id,
        subject_code=f.subject.code,
        subject_name=f.subject.name,
        teaching_rating=f.teaching_rating,
        content_rating=f.content_rating,
        remarks=f.remarks,
        submitted_at=f.submitted_at,
    ) for f in feedbacks]


@router.post("")
def submit_feedback(
    data: List[FeedbackCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    for item in data:
        sub = db.query(Subject).filter(Subject.id == item.subject_id).first()
        if not sub:
            raise HTTPException(404, f"Subject {item.subject_id} not found")

        existing = db.query(Feedback).filter(
            Feedback.student_id == current_user.id,
            Feedback.subject_id == item.subject_id,
            Feedback.semester == item.semester
        ).first()

        if existing:
            existing.teaching_rating = item.teaching_rating
            existing.content_rating = item.content_rating
            existing.remarks = item.remarks
        else:
            db.add(Feedback(
                student_id=current_user.id,
                subject_id=item.subject_id,
                teaching_rating=item.teaching_rating,
                content_rating=item.content_rating,
                remarks=item.remarks,
                semester=item.semester,
            ))
    db.commit()
    return {"message": "Feedback submitted"}
