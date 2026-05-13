# CardAI CRM Backend

Production-ready FastAPI backend for scanning business cards with OCR, extracting CRM contact fields, storing them in MSSQL, and exposing analytics/export APIs.

## Quick Start

```bash
cd backend
cp .env.example .env
docker compose up --build
```

API docs:

- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
alembic upgrade head
uvicorn main:app --reload
```

## Authentication Flow

1. `POST /api/v1/auth/register`
2. `POST /api/v1/auth/login`
3. Store `data.access_token` in the frontend and send `Authorization: Bearer <token>`.
4. Use `POST /api/v1/auth/refresh` before access token expiry.

## Card Scan

```bash
curl -X POST http://localhost:8000/api/v1/cards/scan \
  -H "Authorization: Bearer <token>" \
  -F "image=@card.jpg"
```

The backend validates the image, saves the upload, preprocesses it with OpenCV, extracts text through EasyOCR, applies NLP/regex field extraction, stores a contact, and logs OCR metadata.

## ML Training

Upload CSV/JSON datasets with `text` and `entities` fields through `POST /api/v1/ml/upload-dataset`, then train through `POST /api/v1/ml/train`.

## Environment

All deployment-sensitive values live in `.env`: database URL, Redis URL, JWT secret, CORS origin, upload limits, OCR languages, and rate limits.

## Architecture

- `api/v1/endpoints`: REST controllers
- `services`: business logic
- `repositories`: SQLAlchemy persistence
- `models`: database entities with UUID/audit/soft-delete
- `preprocessing`: OpenCV image pipeline
- `ocr`: EasyOCR adapter
- `ml`: NLP and trainable extraction modules
- `exports`: CSV, Excel, PDF generation
- `middleware`: request logging and rate limiting

## Tests

```bash
pytest
```

