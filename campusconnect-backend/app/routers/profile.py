from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os, shutil, uuid

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User, StudentProfile
from app.schemas.schemas import ProfileUpdate, ProfileOut

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    p = current_user.profile
    return ProfileOut(
        reg_no=current_user.reg_no,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        profile_pic=current_user.profile_pic,
        dob=p.dob if p else None,
        gender=p.gender if p else None,
        father_name=p.father_name if p else None,
        batch=p.batch if p else None,
        address=p.address if p else None,
        program=p.program if p else None,
        academic_session=p.academic_session if p else None,
        section=p.section if p else None,
        semester=p.semester if p else None,
        blood_group=p.blood_group if p else None,
        hostel_room=p.hostel_room if p else None,
        hod=p.hod if p else None,
        cgpa=p.cgpa if p else None,
    )


@router.patch("")
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if data.name:
        current_user.name = data.name
    if data.phone:
        current_user.phone = data.phone

    p = current_user.profile
    if not p:
        p = StudentProfile(user_id=current_user.id)
        db.add(p)

    if data.dob is not None:       p.dob = data.dob
    if data.gender is not None:    p.gender = data.gender
    if data.father_name is not None: p.father_name = data.father_name
    if data.address is not None:   p.address = data.address
    if data.hostel_room is not None: p.hostel_room = data.hostel_room
    if data.blood_group is not None: p.blood_group = data.blood_group

    db.commit()
    return {"message": "Profile updated"}


@router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only JPEG/PNG/WEBP allowed")
    if file.size and file.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    ext = file.filename.rsplit(".", 1)[-1]
    fname = f"{current_user.reg_no}_{uuid.uuid4().hex[:8]}.{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, "profiles")
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, fname)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    current_user.profile_pic = f"/uploads/profiles/{fname}"
    db.commit()
    return {"profile_pic": current_user.profile_pic}
