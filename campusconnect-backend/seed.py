"""
Run this ONCE after first startup to populate the database:
    python seed.py
"""
from datetime import date, datetime, timedelta
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import *

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("🌱 Seeding CampusConnect database...")

# ─── Staff ──────────────────────────────────────────────────
staff_data = [
    ("2001", "Dr. Sundar",    "sundar@campus.edu",    "Professor",         False),
    ("2002", "Dr. Venkatesh", "venkatesh@campus.edu", "HOD / Professor",   False),
    ("2003", "Prof. Ramesh",  "ramesh@campus.edu",    "Assoc. Professor",  False),
    ("2004", "Dr. Priya",     "priya@campus.edu",     "Asst. Professor",   True),   # on leave today
    ("2005", "Prof. Krishnan","krishnan@campus.edu",  "Asst. Professor",   False),
    ("2006", "Prof. Anitha",  "anitha@campus.edu",    "Asst. Professor",   True),   # on leave today
    ("2007", "Prof. Nair",    "nair@campus.edu",      "Asst. Professor",   False),
]
staff_objs = {}
for sno, name, email, desig, on_leave in staff_data:
    s = Staff(staff_no=sno, name=name, email=email, designation=desig,
              is_on_leave=on_leave, leave_date=date.today() if on_leave else None)
    db.add(s)
    db.flush()
    staff_objs[sno] = s

# ─── Subjects ───────────────────────────────────────────────
subjects_data = [
    # Sem 6
    ("CH6001", "Chemical Reaction Engineering", 6, 4, "2001"),
    ("CH6002", "Mass Transfer",                 6, 4, "2003"),
    ("CH6003", "Biochemical Engineering",        6, 3, "2006"),
    ("CH6004", "Heat Transfer",                  6, 4, "2004"),
    ("CH6005", "Process Control",                6, 3, "2005"),
    # Sem 5
    ("CH5001", "Chemical Engg. Thermodynamics", 5, 4, "2001"),
    ("CH5002", "Fluid Mechanics",                5, 4, "2003"),
    ("CH5003", "Particle Technology",            5, 3, "2004"),
    ("CH5004", "Python Programming",             5, 3, "2007"),
    ("CH5005", "Instrumentation",                5, 3, "2005"),
    # Sem 4
    ("CH4001", "C++ Programming",               4, 3, "2007"),
    ("CH4002", "Material & Energy Balance",      4, 4, "2003"),
    ("CH4003", "Transport Phenomena",            4, 4, "2001"),
    ("CH4004", "Organic Chemistry",              4, 3, "2004"),
    ("MA4001", "Engineering Maths IV",           4, 4, "2005"),
    # Sem 3
    ("CH3001", "Stoichiometry & Thermodynamics", 3, 4, "2001"),
    ("CH3002", "Physical Chemistry",             3, 3, "2004"),
    ("MA3001", "Engineering Maths III",          3, 4, "2005"),
    ("CS3001", "Python & Numerical Methods",     3, 3, "2007"),
    ("CH3003", "Chemical Process Calculations",  3, 3, "2003"),
    # Sem 2
    ("PH2001", "Engineering Physics",            2, 4, "2004"),
    ("EC2001", "Electronics & Circuits",         2, 3, "2007"),
    ("MA2001", "Engineering Maths II",           2, 4, "2005"),
    ("CH2001", "Basic Chemical Engineering",     2, 4, "2001"),
    ("HS2001", "Environmental Studies",          2, 2, "2006"),
    # Sem 1
    ("MA1001", "Engineering Maths I",            1, 4, "2005"),
    ("HS1001", "Soft Skills I",                  1, 2, "2006"),
    ("CH1001", "Engineering Chemistry",          1, 4, "2004"),
    ("PH1001", "Engineering Physics I",          1, 4, "2003"),
    ("ME1001", "Workshop / Engg. Practices",     1, 2, "2007"),
]
sub_objs = {}
for code, name, sem, credits, sno in subjects_data:
    sub = Subject(code=code, name=name, semester=sem,
                  credits=credits, staff_id=staff_objs[sno].id)
    db.add(sub)
    db.flush()
    sub_objs[code] = sub

# ─── Timetable (Sem 6) ──────────────────────────────────────
tt_entries = [
    # Monday (0)
    ("CH6001", 0, "09:00", "10:00", "Room 204", "Lec"),
    ("CH6002", 0, "11:00", "12:00", "Room 301", "Lec"),
    ("CH6005", 0, "14:00", "17:00", "Lab 3",    "Lab"),
    # Tuesday (1)
    ("CH6001", 1, "09:00", "10:00", "Room 204", "Lec"),
    ("CH6002", 1, "10:30", "11:30", "Room 301", "Lec"),
    ("CH6005", 1, "13:00", "14:00", "Room 202", "Lec"),
    ("CH6004", 1, "16:00", "17:00", "Room 105", "Lec"),
    # Wednesday (2)
    ("CH6004", 2, "09:00", "10:00", "Room 105", "Lec"),
    ("CH6003", 2, "11:00", "12:00", "Room 202", "Lec"),
    ("CH6002", 2, "14:00", "17:00", "Lab 2",    "Lab"),
    # Thursday (3)
    ("CH6005", 3, "09:00", "10:00", "Room 202", "Lec"),
    ("CH6001", 3, "11:00", "12:00", "Room 204", "Lec"),
    ("CH6001", 3, "14:00", "17:00", "Lab 4",    "Lab"),
    # Friday (4)
    ("CH6002", 4, "09:00", "10:00", "Room 301", "Lec"),
    ("CH6004", 4, "11:00", "12:00", "Room 105", "Lec"),
    ("CH6003", 4, "13:00", "14:00", "Room 202", "Lec"),
    # Saturday (5)
    ("CH6001", 5, "09:00", "10:00", "Room 204", "Tut"),
    ("CH6002", 5, "11:00", "12:00", "Room 301", "Tut"),
]
for code, day, st, et, room, etype in tt_entries:
    db.add(TimetableEntry(subject_id=sub_objs[code].id,
                          day_of_week=day, start_time=st, end_time=et,
                          room=room, entry_type=etype))

# ─── Student User ───────────────────────────────────────────
user = User(
    reg_no="12305182",
    name="Raja M",
    email="royalraja1358@gmail.com",
    phone="8838909272",
    password_hash=hash_password("campus123"),
    is_active=True,
)
db.add(user)
db.flush()

profile = StudentProfile(
    user_id=user.id,
    dob=date(2005, 8, 6),
    gender=GenderEnum.male,
    father_name="Murugesan",
    batch="2023-27",
    address="Door No. 14, 2nd Cross St., Chennai, India",
    program="B.Tech Chemical Engineering",
    academic_session="2023-present",
    section="ChE-6A",
    semester=6,
    blood_group="B+",
    hostel_room="Block C, Room 214",
    hod="Dr. Venkatesh",
    cgpa=7.58,
)
db.add(profile)

# ─── Attendance (Sem 6) ─────────────────────────────────────
att_config = {
    "CH6001": (39, 44),
    "CH6002": (37, 45),
    "CH6003": (38, 45),
    "CH6004": (35, 46),
    "CH6005": (30, 44),
}
base_date = date(2025, 1, 6)
for code, (present, total) in att_config.items():
    sid = sub_objs[code].id
    for i in range(total):
        d = base_date + timedelta(days=i * 2)
        status = "present" if i < present else "absent"
        db.add(Attendance(student_id=user.id, subject_id=sid,
                          date=d, status=status))

# ─── Marks ──────────────────────────────────────────────────
marks_data = {
    6: [
        ("CH6001", 26, 24, None, "A",   7.62),
        ("CH6002", 24, 22, None, "A",   7.62),
        ("CH6003", 24, 22, None, "A",   7.62),
        ("CH6004", 22, 20, None, "B+",  7.62),
        ("CH6005", 20, 18, None, "B",   7.62),
    ],
    5: [
        ("CH5001", 25, 23, 72, "A",   7.80),
        ("CH5002", 26, 24, 75, "A",   7.80),
        ("CH5003", 22, 20, 65, "B+",  7.80),
        ("CH5004", 28, 26, 82, "A+",  7.80),
        ("CH5005", 23, 21, 66, "B+",  7.80),
    ],
    4: [
        ("CH4001", 27, 25, 80, "A+",  7.70),
        ("CH4002", 24, 22, 70, "A",   7.70),
        ("CH4003", 21, 19, 63, "B+",  7.70),
        ("CH4004", 24, 22, 68, "A",   7.70),
        ("MA4001", 21, 19, 60, "B",   7.70),
    ],
    3: [
        ("CH3001", 22, 20, 65, "B+",  7.50),
        ("CH3002", 24, 22, 68, "A",   7.50),
        ("MA3001", 20, 18, 58, "B",   7.50),
        ("CS3001", 26, 24, 74, "A",   7.50),
        ("CH3003", 22, 20, 64, "B+",  7.50),
    ],
    2: [
        ("PH2001", 22, 20, 66, "B+",  7.40),
        ("EC2001", 20, 18, 60, "B",   7.40),
        ("MA2001", 22, 20, 64, "B+",  7.40),
        ("CH2001", 25, 23, 72, "A",   7.40),
        ("HS2001", 26, 24, 76, "A",   7.40),
    ],
    1: [
        ("MA1001", 22, 20, 65, "B+",  7.45),
        ("HS1001", 27, 25, 80, "A+",  7.45),
        ("CH1001", 24, 22, 70, "A",   7.45),
        ("PH1001", 21, 19, 63, "B+",  7.45),
        ("ME1001", 25, 23, 72, "A",   7.45),
    ],
}
for sem, entries in marks_data.items():
    for code, internal, mid, endsem, grade, sgpa in entries:
        db.add(Mark(
            student_id=user.id, subject_id=sub_objs[code].id,
            semester=sem, internal_marks=internal, midterm_marks=mid,
            end_sem_marks=endsem, grade=grade, sgpa=sgpa,
        ))

# ─── Assignments ────────────────────────────────────────────
assignments_data = [
    ("CH6001", "CSTR Design Problem",
     "Design a CSTR for a second-order reaction and calculate conversion.",
     date(2025, 2, 20), False),
    ("CH6002", "Absorption Column Design",
     "Design a packed absorption column and determine NTU/HTU.",
     date(2025, 2, 22), False),
    ("CH6005", "PID Controller Tuning",
     "Tune a PID controller using Ziegler-Nichols method and simulate response.",
     date(2025, 2, 25), False),
    ("CH6004", "Heat Exchanger Simulation",
     "Simulate a shell-and-tube heat exchanger using LMTD method.",
     date(2025, 2, 10), True),
    ("CH6003", "Enzyme Kinetics Report",
     "Study Michaelis-Menten kinetics experimentally and plot Lineweaver-Burk.",
     date(2025, 2, 12), True),
]
for code, title, desc, due, done in assignments_data:
    a = Assignment(subject_id=sub_objs[code].id, title=title,
                   description=desc, due_date=due)
    db.add(a)
    db.flush()
    if done:
        db.add(AssignmentSubmission(
            assignment_id=a.id, student_id=user.id,
            file_url=f"/uploads/assignments/sample_{code}.pdf",
            status="submitted",
        ))

# ─── Exams (Sem 6) ──────────────────────────────────────────
exams_data = [
    ("CH6001", date(2025, 3, 10), "09:00", "12:00", "Block A - 201", 100),
    ("CH6002", date(2025, 3, 12), "09:00", "12:00", "Block B - 105", 100),
    ("CH6003", date(2025, 3, 14), "14:00", "17:00", "Block A - 301", 100),
    ("CH6004", date(2025, 3, 17), "09:00", "12:00", "Block C - 202", 100),
    ("CH6005", date(2025, 3, 19), "14:00", "17:00", "Block B - 204", 100),
]
for code, d, st, et, room, mx in exams_data:
    db.add(Exam(subject_id=sub_objs[code].id, exam_type="end_sem",
                date=d, start_time=st, end_time=et, room_no=room,
                max_marks=mx, semester=6))

# ─── Announcements ──────────────────────────────────────────
announcements = [
    ("End Semester Exam Schedule Released",
     "Sem 6 end semester exams begin March 10. Hall tickets downloadable from Feb 28.",
     "exam", "Admin Office"),
    ("Fee Payment — Last Date Mar 31",
     "Semester 6 fee must be paid before March 31. Late fee ₹500/day applies.",
     "fee", "Accounts Dept."),
    ("ChemE Industrial Visit Confirmed",
     "Industrial visit to CPCL Refinery on Mar 5. Submit permission slips by Feb 22.",
     "academic", "Dept. Office"),
    ("Anti-Ragging Policy Reminder",
     "Zero tolerance policy. Report incidents to Student Welfare Officer.",
     "general", "Dean Office"),
    ("Library Books Return Reminder",
     "All borrowed books must be returned before exams. Fine ₹2/day per book.",
     "library", "Library"),
]
for title, body, cat, posted_by in announcements:
    db.add(Announcement(title=title, body=body, category=cat, posted_by=posted_by))

# ─── Notifications ──────────────────────────────────────────
notifs = [
    ("Assignment Deadline Extended",
     "Dr. Sundar extended CRE (CH6001) deadline to Feb 25.", "marks"),
    ("Low Attendance Warning",
     "CH6005 Process Control at 68% — below required 75%.", "attendance"),
    ("ChemE Symposium Registration Open",
     "ChemE Symposium 2025 registrations now open!", "general"),
    ("Mid-Sem Results Published",
     "Sem 6 mid-semester marks are now available.", "marks"),
    ("Leave Approved",
     "Medical leave Jan 15-16 approved by HOD.", "leave"),
]
for title, body, ntype in notifs:
    db.add(Notification(user_id=user.id, title=title, body=body, notif_type=ntype))

# ─── Reminders ──────────────────────────────────────────────
reminders = [
    ("Submit CRE Assignment", "assignment",
     datetime(2025, 2, 20, 9, 0)),
    ("CH6001 Exam Preparation", "exam",
     datetime(2025, 3, 8, 8, 0)),
    ("Fee Payment Deadline", "fee",
     datetime(2025, 3, 31, 10, 0)),
]
for title, rtype, rat in reminders:
    db.add(Reminder(user_id=user.id, title=title,
                    remind_type=rtype, remind_at=rat))

# ─── Leave Applications ─────────────────────────────────────
db.add(LeaveApplication(student_id=user.id, leave_type="Medical Leave",
                         from_date=date(2025, 1, 15), to_date=date(2025, 1, 16),
                         reason="Doctor appointment", status="approved"))
db.add(LeaveApplication(student_id=user.id, leave_type="Personal Leave",
                         from_date=date(2024, 12, 10), to_date=date(2024, 12, 10),
                         reason="Family function", status="approved"))
db.add(LeaveApplication(student_id=user.id, leave_type="Emergency Leave",
                         from_date=date(2024, 11, 5), to_date=date(2024, 11, 6),
                         reason="Emergency at home", status="pending"))

# ─── Fee Details (Sem 6) ────────────────────────────────────
fees_data = [
    ("Tuition Fee",  45000, True,  datetime(2025, 1, 10), "22541", date(2025, 1, 15)),
    ("Lab Fee",       5000, True,  datetime(2025, 1, 10), "22541", date(2025, 1, 15)),
    ("Hostel Fee",    4500, True,  datetime(2025, 1, 12), "22556", date(2025, 1, 15)),
    ("Exam Fee",      3000, False, None,                  None,    date(2025, 3, 31)),
    ("Library Fee",    500, False, None,                  None,    date(2025, 3, 31)),
    ("Other Charges", 14500, False, None,                 None,    date(2025, 3, 31)),
]
for ftype, amt, paid, paid_at, receipt, due in fees_data:
    db.add(FeeDetail(student_id=user.id, semester=6, fee_type=ftype,
                     amount=amt, is_paid=paid, paid_at=paid_at,
                     receipt_no=receipt, due_date=due))

# ─── Hostel Complaints ──────────────────────────────────────
db.add(HostelComplaint(student_id=user.id, category="Internet",
                        room_no="C-214", description="Internet not working",
                        status="resolved", ticket_no="HC2025-071"))
db.add(HostelComplaint(student_id=user.id, category="Plumbing",
                        room_no="C-214", description="Tap leaking in bathroom",
                        status="in_progress", ticket_no="HC2025-082"))

# ─── Lost & Found ───────────────────────────────────────────
db.add(LostFound(posted_by=user.id, item_name="Blue Water Bottle",
                  description="Lost near Lab Complex B on Feb 16. Has name sticker.",
                  status="lost", location="Lab Complex B",
                  contact="8838909272"))
db.add(LostFound(posted_by=user.id, item_name="Student ID Card",
                  description="Lost near Canteen. Contact admin if found.",
                  status="lost", location="Near Canteen",
                  contact="8838909272"))

# ─── Canteen Shops ──────────────────────────────────────────
shops_data = [
    ("Sai Annapoorna",     "Near Block A",    "🍱", True,  [("Idli (2 pcs)",20,"breakfast"),("Masala Dosa",35,"breakfast"),("Vada",15,"breakfast"),("Sambar Rice",40,"lunch"),("Curd Rice",30,"lunch")]),
    ("Sri Krishna Mess",   "Near Block B",    "🍛", True,  [("Meals (Full)",60,"lunch"),("Chicken Rice",80,"lunch"),("Veg Biryani",65,"lunch"),("Rasam Rice",35,"lunch"),("Chapati (2 pcs)",25,"dinner")]),
    ("Campus Cafe",        "Admin Block",     "☕", True,  [("Coffee",15,"beverages"),("Tea",10,"beverages"),("Cold Coffee",35,"beverages"),("Sandwich",40,"snacks"),("Maggi",30,"snacks")]),
    ("Juice Corner",       "Near Hostel C",   "🥤", True,  [("Fresh Lime",20,"beverages"),("Mango Juice",30,"beverages"),("Watermelon",25,"beverages"),("Mixed Fruit",40,"beverages"),("Sugarcane",20,"beverages")]),
    ("Spicy Bites",        "Sports Ground",   "🌶️",True,  [("Pani Puri",20,"snacks"),("Bhel Puri",25,"snacks"),("Chicken Lollipop",60,"snacks"),("Gobi 65",45,"snacks"),("Parotta",30,"meals")]),
    ("Meenatchi Bakery",   "Near Gate",       "🍞", True,  [("Bread Toast",15,"breakfast"),("Egg Puff",20,"snacks"),("Cake Slice",30,"dessert"),("Bun",10,"snacks"),("Samosa",15,"snacks")]),
    ("Noodle Hub",         "Lab Complex",     "🍜", True,  [("Veg Noodles",45,"meals"),("Egg Noodles",55,"meals"),("Fried Rice",50,"meals"),("Spring Roll",35,"snacks"),("Chilly Parotta",60,"meals")]),
    ("South Side Kitchen", "Near Library",    "🥘", True,  [("Mini Tiffin",25,"breakfast"),("Pongal",20,"breakfast"),("Upma",15,"breakfast"),("Pesarattu",25,"breakfast"),("Rava Dosa",30,"breakfast")]),
    ("Fruit Stall",        "Main Ground",     "🍎", True,  [("Banana (1 pc)",5,"fruits"),("Apple",20,"fruits"),("Orange (2 pcs)",15,"fruits"),("Cut Fruit Bowl",30,"fruits"),("Papaya",20,"fruits")]),
    ("Chill Zone",         "Near Hostel D",   "🍦", False, [("Ice Cream",25,"dessert"),("Kulfi",20,"dessert"),("Milkshake",40,"beverages"),("Buttermilk",10,"beverages"),("Lassi",30,"beverages")]),
]
for sname, block, emoji, is_open, items in shops_data:
    shop = CanteenShop(name=sname, block=block, emoji=emoji, is_open=is_open)
    db.add(shop)
    db.flush()
    for iname, price, cat in items:
        db.add(MenuItem(shop_id=shop.id, name=iname, price=price,
                        is_available=is_open, category=cat))

# ─── Bus Routes ─────────────────────────────────────────────
bus_routes = [
    ("12", "Tambaram Route",  ["Tambaram", "Chrompet", "GST Road", "Pallavaram", "Campus"], 8),
    ("7",  "Velachery Route", ["Velachery", "Guindy", "Porur", "Ramapuram", "Campus"], 22),
    ("3",  "T.Nagar Route",   ["T.Nagar", "Ashok Nagar", "Vadapalani", "Campus"], 35),
    ("5",  "Ambattur Route",  ["Ambattur", "Padi", "Anna Nagar", "Koyambedu", "Campus"], 45),
    ("9",  "OMR Route",       ["Sholinganallur", "Perungudi", "Adyar", "Campus"], 30),
]
for rno, name, stops, eta in bus_routes:
    db.add(BusRoute(route_no=rno, name=name, stops=stops, eta_minutes=eta, status="running"))

# ─── Library ────────────────────────────────────────────────
books = [
    ("Chemical Reaction Engineering",      "Octave Levenspiel",         "LB4521", 3),
    ("Transport Phenomena",                "Bird, Stewart, Lightfoot",  "LB3812", 2),
    ("Mass Transfer Operations",           "Robert Treybal",            "LB4102", 2),
    ("Process Systems Analysis & Control", "Coughanowr & LeBlanc",      "LB4820", 1),
    ("Unit Operations of Chemical Engg.",  "McCabe & Smith",            "LB3501", 4),
    ("Chemical Engineering Thermodynamics","Smith, Van Ness, Abbott",   "LB4003", 2),
    ("Principles of Heat Transfer",        "Frank Kreith",              "LB4310", 3),
    ("Process Control: Modeling Design",   "Coughanowr",                "LB4711", 1),
]
book_objs = []
for title, author, acc, total in books:
    b = LibraryBook(title=title, author=author, accession_no=acc,
                     available=total-1, total=total)
    db.add(b)
    db.flush()
    book_objs.append(b)

# Borrow 2 books for Raja
db.add(LibraryBorrow(student_id=user.id, book_id=book_objs[0].id,
                      borrowed_at=date(2025, 2, 1), due_date=date(2025, 2, 25)))
db.add(LibraryBorrow(student_id=user.id, book_id=book_objs[1].id,
                      borrowed_at=date(2025, 2, 5), due_date=date(2025, 3, 5)))

# ─── Messages (sample) ──────────────────────────────────────
# Create a few other users for messaging demo
other_user = User(reg_no="12305205", name="Karthik R",
                  email="karthik@campus.edu", phone="9876543210",
                  password_hash=hash_password("campus123"), is_active=True)
db.add(other_user)
db.flush()
db.add(StudentProfile(user_id=other_user.id, section="ChE-6A",
                       semester=6, batch="2023-27",
                       program="B.Tech Chemical Engineering"))

db.add(Message(sender_id=other_user.id, group_name="ChE-6A",
               content="Anyone done the CRE assignment?"))
db.add(Message(sender_id=user.id, group_name="ChE-6A",
               content="Working on it! CSTR design right?"))

db.commit()
print("✅ Database seeded successfully!")
print(f"\n📋 Login credentials:")
print(f"   Reg No  : 12305182")
print(f"   Password: campus123")
print(f"\n🌐 API docs: http://localhost:8000/docs")
db.close()
