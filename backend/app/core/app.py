import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.routes.router import api_router
from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.database.session import get_db
from app.middleware.jwt_context import JWTContextMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    # Resolve frontend path once at module creation time
    workspace_root = Path(__file__).resolve().parents[3]
    frontend_path = workspace_root / "Frontend"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Resolved FRONTEND path: %s (exists=%s)", frontend_path, frontend_path.exists())
        if settings.database_url.startswith("sqlite"):
            from app.database.base import Base
            from app.database.session import engine
            Base.metadata.create_all(bind=engine)
        logger.info("CardAI CRM starting in '%s' environment", settings.app_env)
        yield

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="AI-powered business card scanner CRM backend.",
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(JWTContextMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # frontend_path already resolved above in lifespan closure
    @app.get("/health", tags=["Health"])
    async def health(db: Session = Depends(get_db)):
        db_status = "ok"
        try:
            db.execute(text("SELECT 1"))
        except Exception as exc:
            db_status = f"error: {exc}"
            logger.error("Health check DB error: %s", exc)
        healthy = db_status == "ok"
        return {
            "success": healthy,
            "message": "CardAI CRM API is healthy" if healthy else "Service degraded",
            "data": {"status": "ok" if healthy else "degraded", "database": db_status},
            "errors": None,
        }

    # ── Frontend page routes ──────────────────────────────────────────────────

    def _serve(folder: str, filename: str = "code.html") -> FileResponse:
        p = frontend_path / folder / filename
        if p.exists():
            return FileResponse(str(p), media_type="text/html")
        logger.warning("Frontend file not found: %s", p)
        return FileResponse(str(p), media_type="text/html")

    @app.get("/", include_in_schema=False)
    async def root():
        return _serve("login_cardai_crm")

    @app.get("/login", include_in_schema=False)
    @app.get("/login_cardai_crm/code.html", include_in_schema=False)
    async def login_page():
        return _serve("login_cardai_crm")

    @app.get("/dashboard", include_in_schema=False)
    @app.get("/dashboard_cardai_crm/code.html", include_in_schema=False)
    async def dashboard_page():
        return _serve("dashboard_cardai_crm")

    @app.get("/contacts", include_in_schema=False)
    @app.get("/contacts_cardai_crm/code.html", include_in_schema=False)
    async def contacts_page():
        return _serve("contacts_cardai_crm")

    @app.get("/scan", include_in_schema=False)
    @app.get("/scan_card_cardai_crm/code.html", include_in_schema=False)
    async def scan_page():
        return _serve("scan_card_cardai_crm")

    @app.get("/companies", include_in_schema=False)
    @app.get("/companies_cardai_crm/code.html", include_in_schema=False)
    async def companies_page():
        return _serve("companies_cardai_crm")

    @app.get("/reports", include_in_schema=False)
    @app.get("/reports_cardai_crm/code.html", include_in_schema=False)
    async def reports_page():
        return _serve("reports_cardai_crm")

    @app.get("/admin", include_in_schema=False)
    @app.get("/admin_panel/code.html", include_in_schema=False)
    async def admin_panel_page():
        return _serve("admin_panel")

    # Mount shared static assets
    if frontend_path.exists():
        app.mount("/shared", StaticFiles(directory=str(frontend_path / "shared"), html=False), name="shared")

    # Mount uploads so card images are accessible as /uploads/<filename>
    uploads_path = Path(settings.upload_dir)
    if uploads_path.exists():
        app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

    return app
