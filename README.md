# CardAI CRM

**AI-powered Business Card Scanner & Contact Management System**

Scan business cards, automatically extract contact information, and manage everything in a clean CRM dashboard -- all in one place.

---

## What does this project do?

| Feature | Description |
|---|---|
| **Card Scanning** | Upload a photo of a business card -- name, phone, email, and company are automatically detected using OCR (EasyOCR) and NLP |
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

| Technology | Version | Purpose |
|---|---|---|
| **FastAPI** | 0.115.6 | REST API framework with async support and auto-generated Swagger docs |
| **Uvicorn** | 0.34.0 | ASGI server to run the FastAPI application |
| **SQLAlchemy** | 2.0.36 | ORM for database models and queries |
| **Alembic** | 1.14.0 | Database schema migrations |
| **Pydantic v2** | 2.10.4 | Request/response validation and settings management |
| **pyodbc** | 5.2.0 | MSSQL database driver |
| **python-jose** | 3.3.0 | JWT token creation and verification (HS256) |
| **passlib + bcrypt** | 1.7.4 / 4.0.1 | Password hashing |
| **EasyOCR** | 1.7.2 | Deep learning-based text extraction from images |
| **OpenCV** (headless) | 4.10.0.84 | Image preprocessing -- resize, denoise, threshold |
| **Pillow** | 11.0.0 | Image loading and format conversion |
| **spaCy** | 3.8.13 | NLP-based entity extraction (names, organizations) |
| **scikit-learn** | 1.6.0 | ML model training for custom field extraction |
| **NumPy** | 2.0.2 | Numerical operations for image and ML pipelines |
| **pandas** | 2.2.3 | Data manipulation for exports and reports |
| **Celery** | 5.4.0 | Distributed background task queue |
| **Redis** | 5.2.1 | Message broker for Celery |
| **openpyxl** | 3.1.5 | Excel (.xlsx) export |
| **ReportLab** | 4.2.5 | PDF export generation |
| **joblib** | 1.4.2 | Saving and loading trained ML models |
| **python-multipart** | 0.0.20 | Multipart form data (file uploads) |
| **email-validator** | 2.2.0 | Email format validation |
| **pytest + httpx** | 8.3.4 / 0.28.1 | Testing framework with async HTTP client |

### Frontend

| Technology | Purpose |
|---|---|
| **HTML5** | Page structure -- no frontend framework used |
| **Tailwind CSS** (CDN) | Utility-first CSS framework for styling and responsive layout |
| **Vanilla JavaScript** | All interactivity -- no React/Vue/Angular |
| **Fetch API** | HTTP calls to the backend REST API |
| **Material Symbols** (Google Fonts) | Icon library used across all pages |
| **CSS Custom Properties** | Design token system (colors, spacing, typography) |
| **shared/api.js** | Centralized API utility -- handles auth headers, token refresh, fetch wrapper |

### Infrastructure & DevOps

| Technology | Purpose |
|---|---|
| **Docker + Docker Compose** | Containerized deployment (app + MSSQL + Redis) |
| **Microsoft SQL Server** (MSSQL) | Primary production database |
| **SQLite** | Local development fallback (zero-config) |
| **Redis** | Celery broker |
| **Alembic** | Version-controlled schema evolution |

---

## Project Structure

```
CardAI-CRM/
|
+-- backend/                        # FastAPI application
|   +-- main.py                     # App entry point
|   +-- requirements.txt            # Python dependencies
|   +-- .env.example                # Environment variables template
|   +-- docker-compose.yml          # Docker setup (app + MSSQL + Redis)
|   |
|   +-- alembic/                    # Database migrations
|   |   +-- versions/
|   |
|   +-- app/
|       +-- api/v1/
|       |   +-- endpoints/          # Route handlers
|       |   |   +-- auth.py         # Login, register, refresh, logout
|       |   |   +-- cards.py        # Card scan upload
|       |   |   +-- contacts.py     # CRUD for contacts
|       |   |   +-- companies.py    # Company listing
|       |   |   +-- reports.py      # Analytics data
|       |   |   +-- exports.py      # CSV/Excel/PDF export
|       |   |   +-- ml.py           # Dataset upload & model training
|       |   |   +-- admin.py        # Admin-only user management
|       |   +-- dependencies/
|       |       +-- auth.py         # JWT auth dependency injection
|       |
|       +-- services/               # Business logic layer
|       |   +-- auth_service.py
|       |   +-- card_service.py     # Scan pipeline orchestration
|       |   +-- contact_service.py
|       |   +-- ml_service.py
|       |   +-- report_service.py
|       |   +-- tasks.py            # Celery background tasks
|       |
|       +-- repositories/           # Database queries (SQLAlchemy)
|       +-- models/                 # DB table definitions
|       +-- schemas/                # Pydantic request/response models
|       +-- preprocessing/          # OpenCV image pipeline
|       +-- ocr/                    # EasyOCR adapter
|       +-- ml/                     # NLP field extractor
|       +-- exports/                # Export generators (CSV/Excel/PDF)
|       +-- middleware/             # Rate limiting, request logging, JWT context
|       +-- config/settings.py      # All app configuration via .env
|
+-- Frontend/                       # Static HTML pages
|   +-- login_cardai_crm/           # Login page
|   +-- dashboard_cardai_crm/       # Main dashboard with charts
|   +-- scan_card_cardai_crm/       # Card scan / upload UI
|   +-- contacts_cardai_crm/        # Contacts list & management
|   +-- companies_cardai_crm/       # Companies list
|   +-- reports_cardai_crm/         # Reports & analytics
|   +-- admin_panel/                # Admin user management
|   +-- shared/
|       +-- api.js                  # Shared API utility (auth headers, fetch wrapper)
|
+-- .gitignore
```

---

## Card Scan Flow

```
User uploads image
      |
      v
OpenCV preprocessing (resize, denoise, threshold)
      |
      v
EasyOCR text extraction
      |
      v
spaCy NLP + Regex field extraction
  (name, phone, email, company, designation, address, website)
      |
      v
Contact saved to database
      |
      v
Response returned to frontend
```

---

## Quick Start (Local Dev)

### 1. Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
.venv\Scripts\activate
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

POST   /api/v1/cards/scan           <- Upload business card image

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

GET    /api/v1/admin/users          <- Admin only
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
