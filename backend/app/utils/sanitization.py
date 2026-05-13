def sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip()


def sanitize_payload(payload: dict) -> dict:
    return {key: sanitize_text(value) if isinstance(value, str) else value for key, value in payload.items()}

