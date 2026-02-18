from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Mark, Attendance, Subject

router = APIRouter(prefix="/api/performance", tags=["Performance"])

ATTENDANCE_THRESHOLD = 75.0


def _generate_ai_suggestions(att_data: list, marks_data: list) -> List[str]:
    suggestions = []

    for sub in att_data:
        pct = sub["percentage"]
        name = sub["subject_name"]
        code = sub["subject_code"]
        if pct < 75:
            need = sub["classes_needed"]
            suggestions.append(
                f"{code} {name}: Attendance critical at {pct:.1f}%. "
                f"Attend next {need} classes without absence to reach 75%."
            )
        elif pct < 85:
            suggestions.append(
                f"{code} {name}: Attendance borderline at {pct:.1f}%. "
                f"Avoid missing any more classes this semester."
            )

    for m in marks_data:
        total = m["internal"] + m["midterm"]
        if total < 35:
            suggestions.append(
                f"{m['code']} {m['name']}: Internal score {total:.0f}/60 is low. "
                f"Focus on this subject for end-semester."
            )
        elif total >= 50:
            suggestions.append(
                f"{m['code']} {m['name']}: Strong performance ({total:.0f}/60). "
                f"Maintain momentum in end-semester exams."
            )

    if not suggestions:
        suggestions.append("Great work! Keep maintaining your attendance and academic performance.")

    return suggestions


@router.get("")
def get_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6

    # Attendance data
    subjects = db.query(Subject).filter(Subject.semester == semester).all()
    att_data = []
    risk_subjects = []

    for sub in subjects:
        records = db.query(Attendance).filter(
            Attendance.student_id == current_user.id,
            Attendance.subject_id == sub.id
        ).all()
        total = len(records)
        present = sum(1 for r in records if r.status == "present")
        pct = round(present / total * 100, 1) if total else 0.0

        need = 0
        if pct < ATTENDANCE_THRESHOLD and total > 0:
            # classes needed = (0.75*T - P) / (1-0.75) = (0.75T-P)/0.25
            need = max(0, int((0.75 * total - present) / 0.25) + 1)

        att_data.append({
            "subject_code": sub.code,
            "subject_name": sub.name,
            "percentage": pct,
            "present": present,
            "total": total,
            "classes_needed": need,
        })
        if pct < ATTENDANCE_THRESHOLD:
            risk_subjects.append({
                "subject_code": sub.code,
                "subject_name": sub.name,
                "percentage": pct,
                "classes_needed": need,
            })

    # Marks data
    marks = db.query(Mark).filter(
        Mark.student_id == current_user.id,
        Mark.semester == semester
    ).all()
    marks_data = [{
        "code": m.subject.code,
        "name": m.subject.name,
        "internal": m.internal_marks,
        "midterm": m.midterm_marks,
        "grade": m.grade,
        "sgpa": m.sgpa,
    } for m in marks]

    # Semester SGPAs
    all_marks = db.query(Mark).filter(Mark.student_id == current_user.id).all()
    sem_sgpa_map = {}
    for m in all_marks:
        if m.sgpa and m.semester not in sem_sgpa_map:
            sem_sgpa_map[m.semester] = m.sgpa
    semester_sgpas = [{"semester": s, "sgpa": v} for s, v in sorted(sem_sgpa_map.items())]

    # Overall attendance
    total_all = sum(s["total"] for s in att_data)
    present_all = sum(s["present"] for s in att_data)
    overall_att = round(present_all / total_all * 100, 1) if total_all else 0.0

    # AI suggestions
    suggestions = _generate_ai_suggestions(att_data, marks_data)

    return {
        "cgpa": profile.cgpa if profile else 0.0,
        "overall_attendance": overall_att,
        "class_rank": 18,
        "total_students": 60,
        "semester_sgpas": semester_sgpas,
        "attendance_by_subject": att_data,
        "marks_by_subject": marks_data,
        "risk_subjects": risk_subjects,
        "ai_suggestions": suggestions,
    }
