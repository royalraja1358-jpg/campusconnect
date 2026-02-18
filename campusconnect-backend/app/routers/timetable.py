from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, TimetableEntry, Subject
from app.schemas.schemas import DayTimetableOut, TimetableEntryOut

router = APIRouter(prefix="/api/timetable", tags=["Timetable"])

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


@router.get("", response_model=List[DayTimetableOut])
def get_full_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6

    subjects = db.query(Subject).filter(Subject.semester == semester).all()
    sub_ids = [s.id for s in subjects]

    entries = db.query(TimetableEntry).filter(
        TimetableEntry.subject_id.in_(sub_ids)
    ).order_by(TimetableEntry.day_of_week, TimetableEntry.start_time).all()

    days = []
    for day_idx in range(6):
        day_entries = [e for e in entries if e.day_of_week == day_idx]
        days.append(DayTimetableOut(
            day=day_idx,
            day_name=DAY_NAMES[day_idx],
            entries=[TimetableEntryOut(
                subject_code=e.subject.code,
                subject_name=e.subject.name,
                start_time=e.start_time,
                end_time=e.end_time,
                room=e.room,
                entry_type=e.entry_type,
            ) for e in day_entries]
        ))
    return days


@router.get("/day/{day}")
def get_day_timetable(
    day: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6
    subjects = db.query(Subject).filter(Subject.semester == semester).all()
    sub_ids = [s.id for s in subjects]

    entries = db.query(TimetableEntry).filter(
        TimetableEntry.subject_id.in_(sub_ids),
        TimetableEntry.day_of_week == day
    ).order_by(TimetableEntry.start_time).all()

    return DayTimetableOut(
        day=day,
        day_name=DAY_NAMES[day] if day < 6 else "Unknown",
        entries=[TimetableEntryOut(
            subject_code=e.subject.code,
            subject_name=e.subject.name,
            start_time=e.start_time,
            end_time=e.end_time,
            room=e.room,
            entry_type=e.entry_type,
        ) for e in entries]
    )


@router.get("/today")
def get_today_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import date
    day = date.today().weekday()  # 0=Mon, 6=Sun
    if day >= 6:
        return {"day": day, "day_name": "Sunday", "entries": []}
    return get_day_timetable(day, db, current_user)
