# LibraryAI Pro

Production-grade intelligent library management system with FastAPI backend, SQLite database, JWT authentication, and a full HTML/CSS/JS frontend.

## Project Structure

```
AI library/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── seed.py                 # Database seed script
│   ├── requirements.txt
│   ├── database/db.py          # SQLAlchemy engine & session
│   ├── models/                 # User, Book, Loan, Request, Notification, Review, Settings
│   ├── schemas/                # Pydantic request/response models
│   ├── routes/                 # API route handlers
│   ├── services/               # Recommendations, fines, notifications
│   └── utils/                  # JWT, bcrypt security
├── frontend/
│   ├── index.html              # Full UI (student + admin portals)
│   └── js/api.js               # Backend API client
└── LibraryAI-Pro-Light-Readable.html  # Original standalone frontend reference
```

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Seed the database

```bash
python seed.py
```

This creates:
- **50 books** across 9 genres
- **1 admin account**: `admin` / `library@2024`
- **20 demo students** (e.g. `STU-001` / `library@2024`)
- Sample loans, overdue records, and pending requests

### 3. Start the server

```bash
uvicorn main:app --reload
```

Or on Windows if `uvicorn` is not on PATH:

```bash
python -m uvicorn main:app --reload
```

The app serves:
- **Frontend UI**: http://127.0.0.1:8000/
- **API docs**: http://127.0.0.1:8000/docs

## Default Credentials

| Role    | Login ID   | Password      |
|---------|------------|---------------|
| Admin   | `admin`    | `library@2024` |
| Student | `STU-001`  | `library@2024` |

## Business Rules

- Maximum **3 books** per student
- Loan period: **14 days**
- Fine: **₹2 per day** overdue
- Maximum **2 renewals** per loan
- Book approval decreases available copies; returns restore them

## API Endpoints

| Group          | Endpoints |
|----------------|-----------|
| Auth           | `POST /auth/register`, `/auth/login`, `/auth/change-password` |
| Books          | `GET/POST /books`, `GET/PUT/DELETE /books/{id}` |
| Requests       | `GET/POST /requests`, `PUT /requests/{id}/approve`, `/reject` |
| Loans          | `GET /loans`, `POST /loans/issue`, `/renew`, `/return` |
| Members        | `GET /members`, `GET /members/{id}` |
| Notifications  | `GET /notifications`, `PUT /notifications/{id}/read` |
| Analytics      | `GET /analytics/dashboard`, `/top-books`, `/genre-distribution` |
| Reports        | `GET /reports/overdue`, `/fines`, `/members` |
| Chatbot        | `POST /chatbot/query` |
| Settings       | `GET/POST /settings` |

Legacy frontend-compatible aliases (`/student/login`, `/admin/login`, `/dashboard`) are also supported.

## Rebuild Frontend (optional)

If you edit `LibraryAI-Pro-Light-Readable.html`, regenerate the integrated frontend:

```bash
python build_frontend.py
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite, PyJWT, bcrypt
- **Frontend**: HTML, CSS, JavaScript (fetch API via `frontend/js/api.js`)
- **Charts**: Chart.js (admin analytics dashboard)
