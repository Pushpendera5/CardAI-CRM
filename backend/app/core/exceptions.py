from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.responses import error_response


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, errors: list | None = None) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or []


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return error_response(exc.message, exc.errors, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError):
        return error_response("Validation failed", exc.errors(), 422)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_: Request, exc: StarletteHTTPException):
        return error_response(str(exc.detail), [], exc.status_code)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception):
        return error_response("Internal server error", [{"detail": str(exc)}], 500)

