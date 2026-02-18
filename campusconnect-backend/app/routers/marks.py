from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Mark, Subject
from app.schemas.schemas import SemesterMarkOut, MarkOut

router = APIRouter(prefix="/api/marks", tags=["Marks"])


@router.get("", response_model=List[SemesterMarkOut])
def get_all_marks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    marks = db.query(Mark).filter(Mark.student_id == current_user.id)\
               .order_by(Mark.semester.desc()).all()

    # Group by semester
    sem_map: dict = {}
    for m in marks:
        s = m.semester
        if s not in sem_map:
            sem_map[s] = {"sgpa": None, "marks": []}
        sem_map[s]["sgpa"] = m.sgpa
        sem_map[s]["marks"].append(MarkOut(
            subject_code=m.subject.code,
            subject_name=m.subject.name,
            internal_marks=m.internal_marks,
            midterm_marks=m.midterm_marks,
            end_sem_marks=m.end_sem_marks,
            grade=m.grade,
        ))

    result = []
    for sem in sorted(sem_map.keys(), reverse=True):
        result.append(SemesterMarkOut(
            semester=sem,
            sgpa=sem_map[sem]["sgpa"],
            marks=sem_map[sem]["marks"],
        ))
    return result


@router.get("/semester/{sem}", response_model=SemesterMarkOut)
def get_marks_by_semester(
    sem: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    marks = db.query(Mark).filter(
        Mark.student_id == current_user.id,
        Mark.semester == sem
    ).all()

    mark_out = [MarkOut(
        subject_code=m.subject.code,
        subject_name=m.subject.name,
        internal_marks=m.internal_marks,
        midterm_marks=m.midterm_marks,
        end_sem_marks=m.end_sem_marks,
        grade=m.grade,
    ) for m in marks]

    sgpa = marks[0].sgpa if marks else None
    return SemesterMarkOut(semester=sem, sgpa=sgpa, marks=mark_out)


@router.get("/cgpa")
def get_cgpa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    return {"cgpa": profile.cgpa if profile else 0.0}
