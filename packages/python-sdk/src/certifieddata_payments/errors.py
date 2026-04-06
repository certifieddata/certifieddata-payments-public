"""CDP error classes. All errors inherit from CDPError."""

from typing import Any, Optional


class CDPError(Exception):
    """Base class for all CertifiedData Payments SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        http_status: Optional[int] = None,
        code: Optional[str] = None,
        retryable: bool = False,
        raw: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.code = code
        self.retryable = retryable
        self.raw = raw

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, http_status={self.http_status}, message={self.message!r})"


class CDPAuthError(CDPError):
    """Authentication failed (401/403)."""


class CDPValidationError(CDPError):
    """Request validation failed (400)."""

    def __init__(self, message: str, *, validation_errors: Optional[list[Any]] = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or []


class CDPNotFoundError(CDPError):
    """Resource not found (404)."""


class CDPConflictError(CDPError):
    """Conflict — state transition error or idempotency conflict (409)."""


class CDPRateLimitError(CDPError):
    """Rate limit exceeded (429). Retryable."""

    def __init__(self, message: str, *, retry_after: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(message, retryable=True, **kwargs)
        self.retry_after = retry_after


def _raise_for_status(http_status: int, body: Any) -> None:
    """Raise an appropriate CDPError from an HTTP status and error body."""
    error = body.get("error", {}) if isinstance(body, dict) else {}
    code = error.get("code", "unknown")
    message = error.get("message", "An unexpected error occurred.")
    retryable = error.get("retryable", False)

    if http_status == 401 or http_status == 403:
        raise CDPAuthError(message, http_status=http_status, code=code, raw=body)
    if http_status == 400:
        raise CDPValidationError(
            message,
            http_status=http_status,
            code=code,
            raw=body,
            validation_errors=error.get("errors", []),
        )
    if http_status == 404:
        raise CDPNotFoundError(message, http_status=http_status, code=code, raw=body)
    if http_status == 409:
        raise CDPConflictError(message, http_status=http_status, code=code, raw=body)
    if http_status == 429:
        raise CDPRateLimitError(message, http_status=http_status, code=code, raw=body)
    raise CDPError(message, http_status=http_status, code=code, retryable=retryable, raw=body)
