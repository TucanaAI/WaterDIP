from __future__ import annotations

import logging
from typing import Iterable


SENSITIVE_HEADERS: set[str] = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
}

SENSITIVE_KEYS: set[str] = {
    "api_key",
    "token",
    "secret",
    "password",
    "bearer",
    "prompt",
}


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage().lower()
        if any(key in msg for key in SENSITIVE_KEYS):
            return False
        if any(header in msg for header in SENSITIVE_HEADERS):
            return False
        return True


def configure_logging(
    target_loggers: Iterable[str] = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "app",
    ),
) -> None:
    for name in target_loggers:
        logger = logging.getLogger(name)
        logger.addFilter(RedactFilter())