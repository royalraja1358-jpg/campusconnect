from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token,
    get_current_active_user
)
from app.core.config import settings
from app.models.user import User, StudentProfile, PasswordReset
from app.schemas.schemas import (
    LoginRequest, TokenResponse, ForgotPasswordRequest,
    ResetPasswordRequest, ChangePasswordRequest
)
from app.utils.email import send_password_reset_email

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reg_no == req.reg_no).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = create_access_token({"sub": user.reg_no})
    profile = user.profile

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "reg_no": user.reg_no,
            "name": user.name,
            "email": user.email,
            "profile_pic": user.profile_pic,
            "semester": profile.semester if profile else 6,
            "section": profile.section if profile else "ChE-6A",
            "cgpa": profile.cgpa if profile else 0.0,
        }
    }


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter((User.email == req.email) | (User.reg_no == req.email))
        .first()
    )
    # Always return 200 to prevent email enumeration
    if not user:
        return {"message": "If that account exists, a reset link was sent."}

    # Delete any existing tokens
    db.query(PasswordReset).filter(PasswordReset.user_id == user.id).delete()

    token = secrets.token_urlsafe(48)
    pr = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )
    db.add(pr)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    send_password_reset_email(user.email, user.name, reset_link)

    return {"message": "If that account exists, a reset link was sent."}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    pr = db.query(PasswordReset).filter(
        PasswordReset.token == req.token,
        PasswordReset.is_used == False
    ).first()
    if not pr or pr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token invalid or expired")

    user = db.query(User).filter(User.id == pr.user_id).first()
    user.password_hash = hash_password(req.new_password)
    pr.is_used = True
    db.commit()
    return {"message": "Password reset successful"}


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    current_user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_active_user)):
    return {
        "reg_no": current_user.reg_no,
        "name": current_user.name,
        "email": current_user.email,
        "profile_pic": current_user.profile_pic,
        "is_admin": current_user.is_admin,
    }
