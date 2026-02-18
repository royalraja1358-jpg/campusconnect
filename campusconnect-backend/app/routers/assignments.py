from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import os, shutil, uuid

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User, Assignment, AssignmentSubmission, Subject
from app.schemas.schemas import AssignmentOut

router = APIRouter(prefix="/api/assignments", tags=["Assignments"])


def _submission(db, assignment_id, student_id):
    return db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == student_id
    ).first()


@router.get("", response_model=List[AssignmentOut])
def get_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6
    subjects = db.query(Subject).filter(Subject.semester == semester).all()
    sub_ids = [s.id for s in subjects]

    assignments = db.query(Assignment).filter(
        Assignment.subject_id.in_(sub_ids)
    ).order_by(Assignment.due_date).all()

    result = []
    for a in assignments:
        sub = _submission(db, a.id, current_user.id)
        result.append(AssignmentOut(
            id=a.id,
            title=a.title,
            description=a.description,
            subject_code=a.subject.code,
            subject_name=a.subject.name,
            staff_name=a.subject.staff.name if a.subject.staff else None,
            due_date=a.due_date,
            file_url=a.file_url,
            submitted=sub is not None,
            submission_url=sub.file_url if sub else None,
            submitted_at=sub.submitted_at if sub else None,
            status=sub.status if sub else None,
        ))
    return result


@router.post("/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(404, "Assignment not found")

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(413, f"File too large (max {settings.MAX_UPLOAD_MB}MB)")

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    fname = f"{current_user.reg_no}_a{assignment_id}_{uuid.uuid4().hex[:8]}.{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "assignments")
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, fname)

    with open(path, "wb") as f:
        f.write(content)

    existing = _submission(db, assignment_id, current_user.id)
    today = date.today()
    status = "late" if assignment.due_date and today > assignment.due_date else "submitted"

    if existing:
        existing.file_url = f"/uploads/assignments/{fname}"
        existing.status = status
    else:
        sub = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            file_url=f"/uploads/assignments/{fname}",
            status=status,
        )
        db.add(sub)

    db.commit()
    return {"message": "Submitted successfully", "status": status, "file": fname}


@router.get("/{assignment_id}/download")
def download_assignment_file(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment or not assignment.file_url:
        raise HTTPException(404, "File not found")

    path = assignment.file_url.lstrip("/")
    if not os.path.exists(path):
        raise HTTPException(404, "File not on disk")
    return FileResponse(path, filename=os.path.basename(path))
