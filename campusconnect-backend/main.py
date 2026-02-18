from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, Base

# Import all models so SQLAlchemy creates the tables
from app.models.user import (
    User, StudentProfile, Subject, Staff, TimetableEntry,
    Attendance, Mark, Assignment, AssignmentSubmission,
    Exam, LeaveApplication, Feedback, Notification,
    Announcement, Message, Reminder, HostelComplaint,
    LostFound, FeeDetail, CanteenShop, MenuItem, CartItem,
    CanteenOrder, PasswordReset, BusRoute, LibraryBook, LibraryBorrow
)

from app.routers import (
    auth, profile, attendance, marks, timetable,
    assignments, exams, feedback, leave, notifications,
    messages, performance, misc
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    # Create upload directories
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "assignments"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "profiles"), exist_ok=True)
    print("✅ CampusConnect backend started")
    yield
    print("👋 CampusConnect backend stopped")


app = FastAPI(
    title="CampusConnect API",
    description="Backend for CampusConnect student portal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ───────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "null",  # for local file:// opens
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static files (uploaded files) ──────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ─── Routers ────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(attendance.router)
app.include_router(marks.router)
app.include_router(timetable.router)
app.include_router(assignments.router)
app.include_router(exams.router)
app.include_router(feedback.router)
app.include_router(leave.router)
app.include_router(notifications.router)
app.include_router(messages.router)
app.include_router(performance.router)
app.include_router(misc.router)


@app.get("/")
def root():
    return {
        "app": "CampusConnect API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
