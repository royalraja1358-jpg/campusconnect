from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Attendance, Subject, TimetableEntry
from app.schemas.schemas import AttendanceOut, AttendanceDetailOut, AttendanceRecordOut

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


def _pct(present: int, total: int) -> float:
    return round((present / total * 100), 1) if total else 0.0


@router.get("", response_model=List[AttendanceOut])
def get_attendance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6

    subjects = db.query(Subject).filter(Subject.semester == semester).all()
    result = []

    for sub in subjects:
        records = db.query(Attendance).filter(
            Attendance.student_id == current_user.id,
            Attendance.subject_id == sub.id
        ).all()
        total = len(records)
        present = sum(1 for r in records if r.status == "present")

        # Get timing from timetable
        tt = db.query(TimetableEntry).filter(
            TimetableEntry.subject_id == sub.id
        ).first()
        timing = f"{tt.start_time}–{tt.end_time}" if tt else None

        result.append(AttendanceOut(
            subject_code=sub.code,
            subject_name=sub.name,
            staff_no=sub.staff.staff_no if sub.staff else None,
            staff_name=sub.staff.name if sub.staff else None,
            timing=timing,
            present=present,
            total=total,
            percentage=_pct(present, total),
        ))
    return result


@router.get("/overall")
def get_overall_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6
    subjects = db.query(Subject).filter(Subject.semester == semester).all()
    total_all = 0
    present_all = 0
    for sub in subjects:
        records = db.query(Attendance).filter(
            Attendance.student_id == current_user.id,
            Attendance.subject_id == sub.id
        ).all()
        total_all += len(records)
        present_all += sum(1 for r in records if r.status == "present")
    return {
        "overall_percentage": _pct(present_all, total_all),
        "total_classes": total_all,
        "present": present_all,
        "absent": total_all - present_all,
    }


@router.get("/{subject_code}", response_model=AttendanceDetailOut)
def get_attendance_detail(
    subject_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sub = db.query(Subject).filter(Subject.code == subject_code).first()
    if not sub:
        from fastapi import HTTPException
        raise HTTPException(404, "Subject not found")

    records = db.query(Attendance).filter(
        Attendance.student_id == current_user.id,
        Attendance.subject_id == sub.id
    ).order_by(Attendance.date).all()

    total = len(records)
    present = sum(1 for r in records if r.status == "present")

    tt = db.query(TimetableEntry).filter(TimetableEntry.subject_id == sub.id).first()
    timing = f"{tt.start_time}–{tt.end_time}" if tt else None

    rec_out = [
        AttendanceRecordOut(date=r.date, status=r.status, class_no=i+1)
        for i, r in enumerate(records)
    ]
    return AttendanceDetailOut(
        subject_code=sub.code,
        subject_name=sub.name,
        staff_no=sub.staff.staff_no if sub.staff else None,
        timing=timing,
        present=present,
        absent=total - present,
        total=total,
        percentage=_pct(present, total),
        records=rec_out,
    )
