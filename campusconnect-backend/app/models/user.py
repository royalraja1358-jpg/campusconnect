from sqlalchemy import (
    Column, Integer, String, Boolean, Float, DateTime, Date,
    ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    reg_no       = Column(String(20), unique=True, index=True, nullable=False)
    name         = Column(String(100), nullable=False)
    email        = Column(String(150), unique=True, index=True, nullable=False)
    phone        = Column(String(15))
    password_hash= Column(String(200), nullable=False)
    is_active    = Column(Boolean, default=True)
    is_admin     = Column(Boolean, default=False)
    profile_pic  = Column(String(300), default="")
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile      = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    attendances  = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    marks        = relationship("Mark", back_populates="student", cascade="all, delete-orphan")
    assignments  = relationship("AssignmentSubmission", back_populates="student", cascade="all, delete-orphan")
    leave_apps   = relationship("LeaveApplication", back_populates="student", cascade="all, delete-orphan")
    messages_sent= relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    reminders    = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    feedbacks    = relationship("Feedback", back_populates="student", cascade="all, delete-orphan")
    complaints   = relationship("HostelComplaint", back_populates="student", cascade="all, delete-orphan")
    lost_founds  = relationship("LostFound", back_populates="posted_by_user", cascade="all, delete-orphan")
    notifications= relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    cart_items   = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.id"), unique=True)
    dob             = Column(Date)
    gender          = Column(Enum(GenderEnum), default=GenderEnum.male)
    father_name     = Column(String(100))
    batch           = Column(String(20), default="2023-27")
    address         = Column(Text)
    program         = Column(String(100), default="B.Tech Chemical Engineering")
    academic_session= Column(String(30), default="2023-present")
    section         = Column(String(10), default="ChE-6A")
    semester        = Column(Integer, default=6)
    blood_group     = Column(String(5), default="B+")
    hostel_room     = Column(String(20))
    hod             = Column(String(100), default="Dr. Venkatesh")
    cgpa            = Column(Float, default=7.58)

    user = relationship("User", back_populates="profile")

class Subject(Base):
    __tablename__ = "subjects"

    id          = Column(Integer, primary_key=True)
    code        = Column(String(20), unique=True, nullable=False, index=True)
    name        = Column(String(200), nullable=False)
    semester    = Column(Integer, nullable=False)
    credits     = Column(Integer, default=4)
    staff_id    = Column(Integer, ForeignKey("staff.id"), nullable=True)
    is_lab      = Column(Boolean, default=False)

    staff       = relationship("Staff", back_populates="subjects")
    timetable   = relationship("TimetableEntry", back_populates="subject")
    attendances = relationship("Attendance", back_populates="subject")
    marks       = relationship("Mark", back_populates="subject")
    assignments = relationship("Assignment", back_populates="subject")
    exams       = relationship("Exam", back_populates="subject")
    feedbacks   = relationship("Feedback", back_populates="subject")

class Staff(Base):
    __tablename__ = "staff"

    id          = Column(Integer, primary_key=True)
    staff_no    = Column(String(10), unique=True, nullable=False)  # e.g. 2001
    name        = Column(String(100), nullable=False)
    email       = Column(String(150))
    dept        = Column(String(100), default="Chemical Engineering")
    designation = Column(String(100))
    is_on_leave = Column(Boolean, default=False)
    leave_date  = Column(Date, nullable=True)

    subjects    = relationship("Subject", back_populates="staff")

class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id          = Column(Integer, primary_key=True)
    subject_id  = Column(Integer, ForeignKey("subjects.id"))
    day_of_week = Column(Integer, nullable=False)   # 0=Mon .. 5=Sat
    start_time  = Column(String(10), nullable=False) # "09:00"
    end_time    = Column(String(10), nullable=False)  # "10:00"
    room        = Column(String(50))
    entry_type  = Column(String(20), default="Lec")  # Lec/Lab/Tut/Proj

    subject     = relationship("Subject", back_populates="timetable")

class Attendance(Base):
    __tablename__ = "attendances"

    id          = Column(Integer, primary_key=True)
    student_id  = Column(Integer, ForeignKey("users.id"))
    subject_id  = Column(Integer, ForeignKey("subjects.id"))
    date        = Column(Date, nullable=False)
    status      = Column(String(10), nullable=False)  # present/absent/od
    marked_by   = Column(Integer, ForeignKey("staff.id"), nullable=True)

    student     = relationship("User", back_populates="attendances")
    subject     = relationship("Subject", back_populates="attendances")

class Mark(Base):
    __tablename__ = "marks"

    id              = Column(Integer, primary_key=True)
    student_id      = Column(Integer, ForeignKey("users.id"))
    subject_id      = Column(Integer, ForeignKey("subjects.id"))
    semester        = Column(Integer, nullable=False)
    internal_marks  = Column(Float, default=0)   # out of 30
    midterm_marks   = Column(Float, default=0)   # out of 30
    end_sem_marks   = Column(Float, nullable=True)
    grade           = Column(String(5))
    sgpa            = Column(Float, nullable=True)

    student     = relationship("User", back_populates="marks")
    subject     = relationship("Subject", back_populates="marks")

class Assignment(Base):
    __tablename__ = "assignments"

    id          = Column(Integer, primary_key=True)
    subject_id  = Column(Integer, ForeignKey("subjects.id"))
    title       = Column(String(200), nullable=False)
    description = Column(Text)
    due_date    = Column(Date)
    file_url    = Column(String(500))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    subject     = relationship("Subject", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id              = Column(Integer, primary_key=True)
    assignment_id   = Column(Integer, ForeignKey("assignments.id"))
    student_id      = Column(Integer, ForeignKey("users.id"))
    file_url        = Column(String(500))
    submitted_at    = Column(DateTime(timezone=True), server_default=func.now())
    status          = Column(String(20), default="submitted")  # submitted/graded/late

    assignment  = relationship("Assignment", back_populates="submissions")
    student     = relationship("User", back_populates="assignments")

class Exam(Base):
    __tablename__ = "exams"

    id          = Column(Integer, primary_key=True)
    subject_id  = Column(Integer, ForeignKey("subjects.id"))
    exam_type   = Column(String(30), default="end_sem")  # end_sem/mid/internal
    date        = Column(Date)
    start_time  = Column(String(10))
    end_time    = Column(String(10))
    room_no     = Column(String(50))
    max_marks   = Column(Integer, default=100)
    semester    = Column(Integer)

    subject     = relationship("Subject", back_populates="exams")

class LeaveApplication(Base):
    __tablename__ = "leave_applications"

    id          = Column(Integer, primary_key=True)
    student_id  = Column(Integer, ForeignKey("users.id"))
    leave_type  = Column(String(50))
    from_date   = Column(Date)
    to_date     = Column(Date)
    reason      = Column(Text)
    status      = Column(String(20), default="pending")  # pending/approved/rejected
    applied_at  = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(Integer, ForeignKey("staff.id"), nullable=True)

    student     = relationship("User", back_populates="leave_apps")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id              = Column(Integer, primary_key=True)
    student_id      = Column(Integer, ForeignKey("users.id"))
    subject_id      = Column(Integer, ForeignKey("subjects.id"))
    teaching_rating = Column(Integer)   # 1–5
    content_rating  = Column(Integer)   # 1–5
    remarks         = Column(Text)
    semester        = Column(Integer)
    submitted_at    = Column(DateTime(timezone=True), server_default=func.now())

    student     = relationship("User", back_populates="feedbacks")
    subject     = relationship("Subject", back_populates="feedbacks")

class Notification(Base):
    __tablename__ = "notifications"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    title       = Column(String(200))
    body        = Column(Text)
    notif_type  = Column(String(30), default="general")  # attendance/marks/leave/general/fee
    is_read     = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    user        = relationship("User", back_populates="notifications")

class Announcement(Base):
    __tablename__ = "announcements"

    id          = Column(Integer, primary_key=True)
    title       = Column(String(200), nullable=False)
    body        = Column(Text)
    category    = Column(String(50), default="general")
    posted_by   = Column(String(100))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"

    id          = Column(Integer, primary_key=True)
    sender_id   = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null = group
    group_name  = Column(String(100), nullable=True)
    content     = Column(Text, nullable=False)
    is_read     = Column(Boolean, default=False)
    sent_at     = Column(DateTime(timezone=True), server_default=func.now())

    sender      = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")

class Reminder(Base):
    __tablename__ = "reminders"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    title       = Column(String(200))
    remind_type = Column(String(30))  # assignment/exam/fee/timetable/custom
    remind_at   = Column(DateTime(timezone=True))
    is_done     = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    user        = relationship("User", back_populates="reminders")

class HostelComplaint(Base):
    __tablename__ = "hostel_complaints"

    id          = Column(Integer, primary_key=True)
    student_id  = Column(Integer, ForeignKey("users.id"))
    category    = Column(String(50))
    room_no     = Column(String(20))
    description = Column(Text)
    status      = Column(String(20), default="open")  # open/in_progress/resolved
    ticket_no   = Column(String(30))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    student     = relationship("User", back_populates="complaints")

class LostFound(Base):
    __tablename__ = "lost_found"

    id          = Column(Integer, primary_key=True)
    posted_by   = Column(Integer, ForeignKey("users.id"))
    item_name   = Column(String(200))
    description = Column(Text)
    status      = Column(String(10))  # lost/found
    location    = Column(String(200))
    contact     = Column(String(100))
    is_resolved = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    posted_by_user = relationship("User", back_populates="lost_founds")

class FeeDetail(Base):
    __tablename__ = "fee_details"

    id          = Column(Integer, primary_key=True)
    student_id  = Column(Integer, ForeignKey("users.id"))
    semester    = Column(Integer)
    fee_type    = Column(String(100))   # Tuition/Lab/Hostel/Exam/Library/Other
    amount      = Column(Float)
    is_paid     = Column(Boolean, default=False)
    paid_at     = Column(DateTime(timezone=True), nullable=True)
    receipt_no  = Column(String(50))
    due_date    = Column(Date)

class CanteenShop(Base):
    __tablename__ = "canteen_shops"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(100))
    block       = Column(String(100))
    emoji       = Column(String(10))
    is_open     = Column(Boolean, default=True)

    menu_items  = relationship("MenuItem", back_populates="shop", cascade="all, delete-orphan")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id          = Column(Integer, primary_key=True)
    shop_id     = Column(Integer, ForeignKey("canteen_shops.id"))
    name        = Column(String(200))
    price       = Column(Float)
    is_available= Column(Boolean, default=True)
    category    = Column(String(50))

    shop        = relationship("CanteenShop", back_populates="menu_items")

class CartItem(Base):
    __tablename__ = "cart_items"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    menu_item_id= Column(Integer, ForeignKey("menu_items.id"))
    quantity    = Column(Integer, default=1)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    user        = relationship("User", back_populates="cart_items")

class CanteenOrder(Base):
    __tablename__ = "canteen_orders"

    id          = Column(Integer, primary_key=True)
    student_id  = Column(Integer, ForeignKey("users.id"))
    shop_id     = Column(Integer, ForeignKey("canteen_shops.id"))
    items       = Column(JSON)   # [{name, qty, price}]
    total       = Column(Float)
    status      = Column(String(20), default="pending")  # pending/preparing/ready/done
    ordered_at  = Column(DateTime(timezone=True), server_default=func.now())

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    token       = Column(String(200), unique=True)
    expires_at  = Column(DateTime(timezone=True))
    is_used     = Column(Boolean, default=False)

    user        = relationship("User", back_populates="password_resets")

class BusRoute(Base):
    __tablename__ = "bus_routes"

    id          = Column(Integer, primary_key=True)
    route_no    = Column(String(10))
    name        = Column(String(100))
    stops       = Column(JSON)   # ["Stop A", "Stop B", ...]
    eta_minutes = Column(Integer)
    status      = Column(String(20), default="running")  # running/delayed/off

class LibraryBook(Base):
    __tablename__ = "library_books"

    id          = Column(Integer, primary_key=True)
    title       = Column(String(300))
    author      = Column(String(200))
    accession_no= Column(String(30), unique=True)
    available   = Column(Integer, default=1)
    total       = Column(Integer, default=1)

class LibraryBorrow(Base):
    __tablename__ = "library_borrows"

    id          = Column(Integer, primary_key=True)
    student_id  = Column(Integer, ForeignKey("users.id"))
    book_id     = Column(Integer, ForeignKey("library_books.id"))
    borrowed_at = Column(Date)
    due_date    = Column(Date)
    returned_at = Column(Date, nullable=True)
    fine        = Column(Float, default=0)
