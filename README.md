# CardAI CRM

**AI-powered Business Card Scanner & Contact Management System**

Scan business cards, automatically extract contact information, and manage everything in a clean CRM dashboard — all in one place.

---

## What does this project do?

| Feature | Description |
|---|---|
| **Card Scanning** | Upload a photo of a business card — name, phone, email, and company are automatically detected using OCR (EasyOCR) and NLP |
| **Contact Management** | View, edit, search, and delete extracted contacts |
| **Company Grouping** | Contacts are automatically grouped under their respective companies |
| **Reports & Analytics** | Dashboard with contact growth, scan activity, and company-wise breakdown charts |
| **Export** | Export contacts to CSV, Excel, or PDF |
| **Authentication** | JWT-based login/logout with access + refresh tokens, role-based access (user / admin / superadmin) |
| **Admin Panel** | User management, system statistics, and role assignment |
| **ML Training** | Upload custom datasets to fine-tune the field extractor model |

---

## Tech Stack

### Backend
- **FastAPI** — REST API framework
- **SQLAlchemy + Alembic** — ORM + database migrations
- **MSSQL** (production) / **SQLite** (local dev fallback)
- **EasyOCR + OpenCV** — image preprocessing and text extraction
- **spaCy** — NLP-based field extraction (name, org, etc.)
- **Celery + Redis** — background tasks (ML training, heavy exports)
- **JWT (HS256)** — authentication with refresh token rotation

### Frontend
- **Plain HTML + Tailwind CSS** — no framework, lightweight
- **Vanilla JS + Fetch API** — API calls via `shared/api.js`

---

## Project Structure

```
CardAI-CRM/
│
├── backend/                        # FastAPI application
│   ├── main.py                     # App entry point
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   ├── docker-compose.yml          # Docker setup (app + MSSQL + Redis)
│   │
│   ├── alembic/                    # Database migrations
│   │   └── versions/
│   │
│   └── app/
│       ├── api/v1/
│       │   ├── endpoints/          # Route handlers
│       │   │   ├── auth.py         # Login, register, refresh, logout
│       │   │   ├── cards.py        # Card scan upload
│       │   │   ├── contacts.py     # CRUD for contacts
│       │   │   ├── companies.py    # Company listing
│       │   │   ├── reports.py      # Analytics data
│       │   │   ├── exports.py      # CSV/Excel/PDF export
│       │   │   ├── ml.py           # Dataset upload & model training
│       │   │   └── admin.py        # Admin-only user management
│       │   └── dependencies/
│       │       └── auth.py         # JWT auth dependency injection
│       │
│       ├── services/               # Business logic layer
│       │   ├── auth_service.py
│       │   ├── card_service.py     # Scan pipeline orchestration
│       │   ├── contact_service.py
│       │   ├── ml_service.py
│       │   ├── report_service.py
│       │   └── tasks.py            # Celery background tasks
│       │
│       ├── repositories/           # Database queries (SQLAlchemy)
│       ├── models/                 # DB table definitions
│       ├── schemas/                # Pydantic request/response models
│       ├── preprocessing/          # OpenCV image pipeline
│       ├── ocr/                    # EasyOCR adapter
│       ├── ml/                     # NLP field extractor
│       ├── exports/                # Export generators (CSV/Excel/PDF)
│       ├── middleware/             # Rate limiting, request logging, JWT context
│       └── config/settings.py     # All app configuration via .env
│
├── Frontend/                       # Static HTML pages
│   ├── login_cardai_crm/           # Login page
│   ├── dashboard_cardai_crm/       # Main dashboard with charts
│   ├── scan_card_cardai_crm/       # Card scan / upload UI
│   ├── contacts_cardai_crm/        # Contacts list & management
│   ├── companies_cardai_crm/       # Companies list
│   ├── reports_cardai_crm/         # Reports & analytics
│   ├── admin_panel/                # Admin user management
│   └── shared/
│       └── api.js                  # Shared API utility (auth headers, fetch wrapper)
│
└── .gitignore
```

---

## Card Scan Flow

```
User uploads image
      ↓
OpenCV preprocessing (resize, denoise, threshold)
      ↓
EasyOCR text extraction
      ↓
spaCy NLP + Regex field extraction
  (name, phone, email, company, designation, address, website)
      ↓
Contact saved to database
      ↓
Response returned to frontend
```

---

## Quick Start (Local Dev)

### 1. Backend

```bash
cd backend
cp .env.example .env          # Fill in your values
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
alembic upgrade head
uvicorn main:app --reload
```

API docs available at: `http://localhost:8000/docs`

### 2. Docker (Recommended)

```bash
cd backend
docker compose up --build
```

Starts: FastAPI app + MSSQL + Redis

### 3. Frontend

Frontend files are served directly by the FastAPI backend at:

| Page | URL |
|---|---|
| Login | `http://localhost:8000/login` |
| Dashboard | `http://localhost:8000/dashboard` |
| Scan Card | `http://localhost:8000/scan` |
| Contacts | `http://localhost:8000/contacts` |
| Companies | `http://localhost:8000/companies` |
| Reports | `http://localhost:8000/reports` |
| Admin | `http://localhost:8000/admin` |

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
DATABASE_URL=mssql+pyodbc://...
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
FRONTEND_ORIGIN=http://localhost:8000
```

---

## API Overview

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

POST   /api/v1/cards/scan           ← Upload business card image

GET    /api/v1/contacts/
POST   /api/v1/contacts/
PUT    /api/v1/contacts/{id}
DELETE /api/v1/contacts/{id}

GET    /api/v1/companies/

GET    /api/v1/reports/summary
GET    /api/v1/reports/activity

GET    /api/v1/exports/csv
GET    /api/v1/exports/excel
GET    /api/v1/exports/pdf

POST   /api/v1/ml/upload-dataset
POST   /api/v1/ml/train

GET    /api/v1/admin/users          ← Admin only
```

---

## Tests

```bash
cd backend
pytest
```

Coverage: auth, contacts, reports, ML extractor.

---

## User Roles

| Role | Access |
|---|---|
| `user` | Scan cards, manage own contacts, export |
| `admin` | All user features + user management |
| `superadmin` | Full system access |
