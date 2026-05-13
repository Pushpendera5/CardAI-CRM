from typing import Any

from fastapi.responses import JSONResponse


def success_response(message: str = "Success", data: Any = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "message": message, "data": data if data is not None else {}, "errors": None},
    )


def error_response(message: str, errors: Any = None, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "data": None, "errors": errors or []},
    )

