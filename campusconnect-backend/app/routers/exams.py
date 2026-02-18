from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Exam, Subject
from app.schemas.schemas import ExamOut

router = APIRouter(prefix="/api/exams", tags=["Exams"])


@router.get("", response_model=List[ExamOut])
def get_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6

    exams = db.query(Exam).filter(Exam.semester == semester)\
               .order_by(Exam.date).all()

    return [ExamOut(
        id=e.id,
        subject_code=e.subject.code,
        subject_name=e.subject.name,
        exam_type=e.exam_type,
        date=e.date,
        start_time=e.start_time,
        end_time=e.end_time,
        room_no=e.room_no,
        max_marks=e.max_marks,
    ) for e in exams]
