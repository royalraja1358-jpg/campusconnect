from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import date, datetime
from enum import Enum

# ─── Auth ───────────────────────────────────────────────────

class LoginRequest(BaseModel):
    reg_no: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)

# ─── Profile ────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    father_name: Optional[str] = None
    address: Optional[str] = None
    hostel_room: Optional[str] = None
    blood_group: Optional[str] = None

class ProfileOut(BaseModel):
    reg_no: str
    name: str
    email: str
    phone: Optional[str]
    profile_pic: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    father_name: Optional[str]
    batch: Optional[str]
    address: Optional[str]
    program: Optional[str]
    academic_session: Optional[str]
    section: Optional[str]
    semester: Optional[int]
    blood_group: Optional[str]
    hostel_room: Optional[str]
    hod: Optional[str]
    cgpa: Optional[float]

    class Config:
        orm_mode= True

# ─── Attendance ─────────────────────────────────────────────

class AttendanceOut(BaseModel):
    subject_code: str
    subject_name: str
    staff_no: Optional[str]
    staff_name: Optional[str]
    timing: Optional[str]
    present: int
    total: int
    percentage: float

class AttendanceRecordOut(BaseModel):
    date: date
    status: str
    class_no: int

class AttendanceDetailOut(BaseModel):
    subject_code: str
    subject_name: str
    staff_no: Optional[str]
    timing: Optional[str]
    present: int
    absent: int
    total: int
    percentage: float
    records: List[AttendanceRecordOut]

# ─── Marks ──────────────────────────────────────────────────

class MarkOut(BaseModel):
    subject_code: str
    subject_name: str
    internal_marks: float
    midterm_marks: float
    end_sem_marks: Optional[float]
    grade: Optional[str]

class SemesterMarkOut(BaseModel):
    semester: int
    sgpa: Optional[float]
    marks: List[MarkOut]

# ─── Timetable ──────────────────────────────────────────────

class TimetableEntryOut(BaseModel):
    subject_code: str
    subject_name: str
    start_time: str
    end_time: str
    room: Optional[str]
    entry_type: str

class DayTimetableOut(BaseModel):
    day: int
    day_name: str
    entries: List[TimetableEntryOut]

# ─── Assignments ────────────────────────────────────────────

class AssignmentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    subject_code: str
    subject_name: str
    staff_name: Optional[str]
    due_date: Optional[date]
    file_url: Optional[str]
    submitted: bool
    submission_url: Optional[str]
    submitted_at: Optional[datetime]
    status: Optional[str]

class AssignmentCreate(BaseModel):
    subject_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None

# ─── Exams ──────────────────────────────────────────────────

class ExamOut(BaseModel):
    id: int
    subject_code: str
    subject_name: str
    exam_type: str
    date: Optional[date]
    start_time: Optional[str]
    end_time: Optional[str]
    room_no: Optional[str]
    max_marks: int

# ─── Leave ──────────────────────────────────────────────────

class LeaveCreate(BaseModel):
    leave_type: str
    from_date: date
    to_date: date
    reason: str

class LeaveOut(BaseModel):
    id: int
    leave_type: str
    from_date: date
    to_date: date
    reason: str
    status: str
    applied_at: datetime

    class Config:
        orm_mode = True

# ─── Feedback ───────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    subject_id: int
    teaching_rating: int = Field(ge=1, le=5)
    content_rating: int = Field(ge=1, le=5)
    remarks: Optional[str] = None
    semester: int

class FeedbackOut(BaseModel):
    id: int
    subject_code: str
    subject_name: str
    teaching_rating: int
    content_rating: int
    remarks: Optional[str]
    submitted_at: datetime

# ─── Notifications ──────────────────────────────────────────

class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    notif_type: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True

# ─── Announcements ──────────────────────────────────────────

class AnnouncementOut(BaseModel):
    id: int
    title: str
    body: str
    category: str
    posted_by: str
    created_at: datetime

    class Config:
        orm_mode = True

# ─── Messages ───────────────────────────────────────────────

class MessageCreate(BaseModel):
    receiver_id: Optional[int] = None
    group_name: Optional[str] = None
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    receiver_id: Optional[int]
    group_name: Optional[str]
    content: str
    is_read: bool
    sent_at: datetime

# ─── Reminders ──────────────────────────────────────────────

class ReminderCreate(BaseModel):
    title: str
    remind_type: str
    remind_at: datetime

class ReminderOut(BaseModel):
    id: int
    title: str
    remind_type: str
    remind_at: datetime
    is_done: bool

    class Config:
        orm_mode = True

# ─── Hostel ─────────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    category: str
    room_no: str
    description: str

class ComplaintOut(BaseModel):
    id: int
    category: str
    room_no: str
    description: str
    status: str
    ticket_no: str
    created_at: datetime

    class Config:
        orm_mode = True

# ─── Lost & Found ───────────────────────────────────────────

class LostFoundCreate(BaseModel):
    item_name: str
    description: str
    status: str   # lost / found
    location: str
    contact: str

class LostFoundOut(BaseModel):
    id: int
    item_name: str
    description: str
    status: str
    location: str
    contact: str
    posted_by: str
    is_resolved: bool
    created_at: datetime

# ─── Fee ────────────────────────────────────────────────────

class FeeOut(BaseModel):
    fee_type: str
    amount: float
    is_paid: bool
    paid_at: Optional[datetime]
    receipt_no: Optional[str]
    due_date: Optional[date]

# ─── Canteen ────────────────────────────────────────────────

class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    is_available: bool
    category: Optional[str]

class ShopOut(BaseModel):
    id: int
    name: str
    block: str
    emoji: str
    is_open: bool
    menu_items: Optional[List[MenuItemOut]] = []

class OrderCreate(BaseModel):
    shop_id: int
    items: List[dict]   # [{menu_item_id, quantity}]

class OrderOut(BaseModel):
    id: int
    shop_id: int
    items: Any
    total: float
    status: str
    ordered_at: datetime

# ─── Canteen Cart ───────────────────────────────────────────

class CartAddRequest(BaseModel):
    menu_item_id: int
    quantity: int = 1

# ─── Performance ────────────────────────────────────────────

class PerformanceOut(BaseModel):
    cgpa: float
    overall_attendance: float
    class_rank: Optional[int]
    total_students: int
    semester_sgpas: List[dict]
    risk_subjects: List[dict]
    ai_suggestions: List[str]

# ─── Staff / Teacher Leave ──────────────────────────────────

class StaffOut(BaseModel):
    id: int
    staff_no: str
    name: str
    dept: str
    designation: Optional[str]
    is_on_leave: bool
    subjects: List[str]

# ─── Bus ────────────────────────────────────────────────────

class BusRouteOut(BaseModel):
    id: int
    route_no: str
    name: str
    stops: List[str]
    eta_minutes: int
    status: str

# ─── Library ────────────────────────────────────────────────

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    accession_no: str
    available: int

class BorrowOut(BaseModel):
    id: int
    title: str
    author: str
    accession_no: str
    borrowed_at: date
    due_date: date
    returned_at: Optional[date]
    fine: float
