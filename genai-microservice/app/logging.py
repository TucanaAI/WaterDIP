from __future__ import annotations
import logging
from typing import Iterable

SENSITIVE_HEADERS: set[str] = {
    "authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token",
}
SENSITIVE_KEYS: set[str] = {
    "api_key", "token", "secret", "password", "bearer", "prompt"  # avoid logging prompts
}

class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage().lower()
        if any(k in msg for k in SENSITIVE_KEYS):
            return False
        if any(h in msg for h in SENSITIVE_HEADERS):
            return False
        return True

def configure_logging(target_loggers: Iterable[str] = ("uvicorn", "uvicorn.error", "uvicorn.access", "app")) -> None:
    for name in target_loggers:
        logger = logging.getLogger(name)
        logger.addFilter(RedactFilter())
        # keep default handlers/levels; we only filter content

