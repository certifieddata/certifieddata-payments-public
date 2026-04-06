"""Webhook signature verification for CDP webhooks."""

import hashlib
import hmac
import time


def verify_webhook_signature(
    raw_body: str | bytes,
    signature_header: str,
    timestamp_header: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> bool:
    """
    Verify a CDP webhook signature.

    CDP signs webhooks using HMAC-SHA256 over the string:
        ``{timestamp}.{raw_body}``

    The ``CDP-Signature`` header has the format::
        ``t={timestamp},v1={hmac_hex}``

    :param raw_body: Raw request body (str or bytes) — before any JSON parsing.
    :param signature_header: Value of the ``CDP-Signature`` header.
    :param timestamp_header: Value of the ``CDP-Timestamp`` header.
    :param secret: Webhook endpoint secret.
    :param tolerance_seconds: Maximum age of the webhook in seconds (default 300).
    :returns: True if the signature is valid and within the timestamp tolerance.
    :raises ValueError: If the signature header format is invalid.
    """
    # Parse timestamp
    try:
        ts = int(timestamp_header)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid CDP-Timestamp header: {timestamp_header!r}") from exc

    # Check timestamp tolerance
    now = int(time.time())
    if abs(now - ts) > tolerance_seconds:
        return False

    # Extract v1 signature from header
    v1_sig: str | None = None
    for part in signature_header.split(","):
        part = part.strip()
        if part.startswith("v1="):
            v1_sig = part[3:]
            break

    if not v1_sig:
        return False

    # Compute expected signature
    body_bytes = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
    signed_payload = f"{ts}.".encode("utf-8") + body_bytes
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

    # Constant-time comparison
    return hmac.compare_digest(expected, v1_sig)
