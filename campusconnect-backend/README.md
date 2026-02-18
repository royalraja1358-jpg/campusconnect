# CampusConnect Backend

FastAPI + PostgreSQL backend for the CampusConnect student portal.

---

## Prerequisites

| Tool | Download |
|------|----------|
| Python 3.10+ | https://python.org |
| PostgreSQL 14+ | https://postgresql.org |

---

## Quick Start

### Windows
```bat
setup.bat
```

### Linux / Mac
```bash
chmod +x setup.sh
./setup.sh
```

That's it. The script will:
1. Create a virtual environment
2. Install all Python packages
3. Create the PostgreSQL database + user
4. Seed it with Raja's sample data
5. Start the server at **http://localhost:8000**

---

## Manual Setup (if the script fails)

```bash
# 1. Create venv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install packages
pip install -r requirements.txt

# 3. Create database (as postgres superuser)
psql -U postgres
CREATE USER campususer WITH PASSWORD 'campuspass';
CREATE DATABASE campusconnect OWNER campususer;
GRANT ALL PRIVILEGES ON DATABASE campusconnect TO campususer;
\q

# 4. Seed data
python seed.py

# 5. Run server
uvicorn main:app --reload --port 8000
```

---

## Login

| Field | Value |
|-------|-------|
| Reg No | `12305182` |
| Password | `campus123` |

---

## API Overview

| Module | Endpoint |
|--------|----------|
| Auth | `POST /api/auth/login` |
| Auth | `POST /api/auth/forgot-password` |
| Auth | `POST /api/auth/reset-password` |
| Auth | `POST /api/auth/change-password` |
| Profile | `GET/PATCH /api/profile` |
| Profile | `POST /api/profile/upload-photo` |
| Attendance | `GET /api/attendance` |
| Attendance | `GET /api/attendance/{subject_code}` |
| Marks | `GET /api/marks` |
| Marks | `GET /api/marks/semester/{sem}` |
| Timetable | `GET /api/timetable` |
| Timetable | `GET /api/timetable/today` |
| Assignments | `GET /api/assignments` |
| Assignments | `POST /api/assignments/{id}/submit` (multipart) |
| Exams | `GET /api/exams` |
| Feedback | `GET/POST /api/feedback` |
| Leave | `GET/POST /api/leave` |
| Notifications | `GET /api/notifications` |
| Notifications | `PATCH /api/notifications/read-all` |
| Messages | `GET /api/messages/conversations` |
| Messages | `GET /api/messages/dm/{partner_id}` |
| Messages | `GET /api/messages/group/{group_name}` |
| Messages | `POST /api/messages/send` |
| Performance | `GET /api/performance` |
| Announcements | `GET /api/announcements` |
| Reminders | `GET/POST /api/reminders` |
| Hostel | `GET/POST /api/hostel/complaints` |
| Lost & Found | `GET/POST /api/lost-found` |
| Fees | `GET /api/fees` |
| Canteen | `GET /api/canteen/shops` |
| Canteen | `POST /api/canteen/cart/add` |
| Canteen | `POST /api/canteen/order` |
| Teacher Leave | `GET /api/teacher-leave` |
| Bus | `GET /api/bus` |
| Library | `GET /api/library/borrowed` |
| Library | `GET /api/library/search?q=` |

Full interactive docs: **http://localhost:8000/docs**

---

## WebSocket (Realtime Chat)

Connect to:
```
ws://localhost:8000/api/messages/ws/<YOUR_JWT_TOKEN>
```

Send JSON actions:
```json
{ "action": "join_group",  "group": "ChE-6A" }
{ "action": "send_group",  "group": "ChE-6A", "content": "Hello!" }
{ "action": "send_dm",     "to": 2,            "content": "Hi!" }
{ "action": "ping" }
```

---

## Connecting the Frontend

Add this to your `index.html` before the closing `</body>`:

```html
<script>
const API = "http://localhost:8000";

async function apiCall(path, method="GET", body=null) {
  const token = localStorage.getItem("cc_token");
  const opts = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { "Authorization": "Bearer " + token } : {})
    },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) throw await res.json();
  return res.json();
}

// Example: login
async function doLogin() {
  const reg_no = document.getElementById("login-roll").value;
  const password = document.querySelector("input[type=password]").value;
  const data = await apiCall("/api/auth/login", "POST", { reg_no, password });
  localStorage.setItem("cc_token", data.access_token);
  localStorage.setItem("cc_user", JSON.stringify(data.user));
  navigate("home");
}
</script>
```

---

## Project Structure

```
campusconnect-backend/
├── main.py               ← FastAPI app entry
├── seed.py               ← Database seeder
├── requirements.txt
├── .env                  ← Config (edit SMTP here)
├── setup.bat / setup.sh  ← One-click start
├── uploads/              ← Uploaded files
│   ├── assignments/
│   └── profiles/
└── app/
    ├── core/
    │   ├── config.py     ← Settings
    │   ├── database.py   ← SQLAlchemy engine
    │   └── security.py   ← JWT + bcrypt
    ├── models/
    │   └── user.py       ← All database models (30+ tables)
    ├── schemas/
    │   └── schemas.py    ← All Pydantic schemas
    ├── routers/
    │   ├── auth.py
    │   ├── profile.py
    │   ├── attendance.py
    │   ├── marks.py
    │   ├── timetable.py
    │   ├── assignments.py
    │   ├── exams.py
    │   ├── feedback.py
    │   ├── leave.py
    │   ├── notifications.py
    │   ├── messages.py   ← REST + WebSocket
    │   ├── performance.py
    │   └── misc.py       ← Canteen, fees, hostel, bus...
    └── utils/
        ├── email.py
        └── websocket_manager.py
```
