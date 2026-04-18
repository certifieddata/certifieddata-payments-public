#!/usr/bin/env python3
"""Self-contained Flask mock server for the public Claude demo.

Supports the full 5-phase happy-path flow plus governance paths:
 * sandbox amount-limit enforcement
 * provenance immutability after capture
 * cancel state-machine enforcement
 * idempotency-key replay
 * webhook emission (best-effort, fire-and-forget POST)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import itertools
import json
import os as _os
import sys
import threading
import time
from typing import Any

try:
    from flask import Flask, jsonify, request
except ImportError:
    print("Flask is required. Run: pip install flask", file=sys.stderr)
    raise

try:
    import requests as _requests
except ImportError:
    _requests = None  # webhook emission becomes a no-op

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
except ImportError:
    Ed25519PrivateKey = None
    Ed25519PublicKey = None


HOST = "127.0.0.1"
PORT = 3456
POLICY_ID = "pol_mock_agent_demo_v1"
# DEMO ONLY — do not use in production. This key ID is intentionally fictional
# and will never match a real platform signing key.
SIGNING_KEY_ID = "cd_demo_mock_only"
SANDBOX_AMOUNT_LIMIT_CENTS = 100_000  # mirrors capabilities.sandbox_limits.max_amount_cents

# Ephemeral key — fresh at startup, never reused, never predictable.
_EPHEMERAL_KEY_BYTES = _os.urandom(32)

app = Flask(__name__)
transactions: dict[str, dict[str, Any]] = {}
receipts: dict[str, dict[str, Any]] = {}
idempotency: dict[str, dict[str, Any]] = {}
webhook_endpoints: list[dict[str, Any]] = []  # {url, secret}
tx_counter = itertools.count(1)
receipt_counter = itertools.count(1)


if Ed25519PrivateKey is not None:
    private_key = Ed25519PrivateKey.from_private_bytes(_EPHEMERAL_KEY_BYTES)
    public_key = private_key.public_key()
    SIGNATURE_MODE = "cryptographic"
else:
    private_key = None
    public_key = None
    SIGNATURE_MODE = "simulated"


def next_id(prefix: str, counter: itertools.count) -> str:
    return f"{prefix}_mock_{next(counter):06d}"


def canonical_json(data: dict[str, Any]) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")


def static_signature(payload: bytes) -> str:
    digest = hashlib.sha256(payload + b":mock-signature").digest()
    return base64.urlsafe_b64encode(digest * 2).decode("ascii").rstrip("=")


def sign_payload(payload: bytes) -> str:
    if private_key is None:
        return static_signature(payload)
    return base64.urlsafe_b64encode(private_key.sign(payload)).decode("ascii").rstrip("=")


def verify_signature(payload: bytes, signature_text: str) -> bool:
    if public_key is None:
        return True
    padding = "=" * (-len(signature_text) % 4)
    try:
        signature = base64.urlsafe_b64decode(signature_text + padding)
        public_key.verify(signature, payload)
        return True
    except Exception:
        return False


def not_found(resource: str, resource_id: str) -> tuple[dict[str, Any], int]:
    return (
        {"error": {"code": f"{resource}.not_found", "http_status": 404,
                    "message": f"{resource} {resource_id} not found.", "retryable": False}},
        404,
    )


def error(code: str, status: int, message: str, retryable: bool = False) -> tuple[Any, int]:
    return jsonify({"error": {"code": code, "http_status": status,
                              "message": message, "retryable": retryable}}), status


def idempotent(endpoint: str):
    """Return cached response for same (endpoint, idempotency-key), else None."""
    key = request.headers.get("Idempotency-Key")
    if not key:
        return None, None
    full_key = f"{endpoint}:{key}"
    return idempotency.get(full_key), full_key


def cache_response(full_key: str | None, payload: Any, status: int) -> None:
    if full_key:
        idempotency[full_key] = {"payload": payload, "status": status}


def emit_webhook(event_type: str, data: dict[str, Any]) -> None:
    """Fire-and-forget POST to every registered webhook endpoint."""
    if _requests is None or not webhook_endpoints:
        return
    envelope = {
        "id": f"evt_mock_{int(time.time()*1000)}",
        "type": event_type,
        "created_at": int(time.time()),
        "livemode": False,
        "api_version": "2025-01-01",
        "data": data,
    }
    body = json.dumps(envelope, separators=(",", ":"))
    ts = str(int(time.time()))
    for ep in list(webhook_endpoints):
        secret = ep.get("secret", "")
        sig = hmac.new(secret.encode("utf-8"),
                       f"{ts}.".encode("utf-8") + body.encode("utf-8"),
                       hashlib.sha256).hexdigest()
        threading.Thread(
            target=_post_webhook,
            args=(ep["url"], body, ts, sig),
            daemon=True,
        ).start()


def _post_webhook(url: str, body: str, ts: str, sig: str) -> None:
    try:
        _requests.post(
            url,
            data=body,
            headers={
                "Content-Type":    "application/json",
                "CDAC-Timestamp":  ts,
                "CDAC-Signature":  f"t={ts},v1={sig}",
            },
            timeout=3,
        )
    except Exception:
        pass


@app.get("/v1/health")
def health() -> Any:
    return jsonify({"status": "ok", "mode": "mock", "livemode": False,
                    "signatureMode": SIGNATURE_MODE})


@app.get("/v1/capabilities")
def capabilities() -> Any:
    """Expose a minimal capabilities shape for discovery demos."""
    return jsonify({
        "version": "1.0.0",
        "api_version": "2025-01-01",
        "environments": ["sandbox"],
        "payment_rails": ["stripe", "usdc_base", "usdc_ethereum", "eth_ethereum"],
        "sandbox_limits": {"max_amount_cents": SANDBOX_AMOUNT_LIMIT_CENTS},
        "webhooks": {"signature_algorithm": "hmac-sha256",
                      "signature_header": "CDAC-Signature",
                      "timestamp_header": "CDAC-Timestamp"},
        "receipt_verification": {"signing_algorithm": "Ed25519",
                                  "algorithm": "sha256-stable-json"},
    })


@app.post("/v1/webhook_endpoints")
def create_webhook_endpoint() -> Any:
    body = request.get_json(silent=True) or {}
    url = body.get("url")
    if not url:
        return error("webhook_endpoint.invalid", 400, "url is required")
    secret = body.get("secret") or "whsec_mock_" + hashlib.sha256(url.encode()).hexdigest()[:16]
    record = {"id": f"wh_mock_{len(webhook_endpoints)+1}", "url": url, "secret": secret,
              "livemode": False}
    webhook_endpoints.append(record)
    return jsonify(record), 201


@app.post("/v1/transactions")
def create_transaction() -> Any:
    cached, key = idempotent("POST:/v1/transactions")
    if cached is not None:
        return jsonify(cached["payload"]), cached["status"]

    body = request.get_json(silent=True) or {}
    amount = body.get("amount")

    if isinstance(amount, int) and amount > SANDBOX_AMOUNT_LIMIT_CENTS:
        return error(
            "sandbox_amount_limit_exceeded", 400,
            f"Sandbox transactions must not exceed {SANDBOX_AMOUNT_LIMIT_CENTS} cents. Got {amount}.",
            retryable=False,
        )

    tx_id = next_id("txn", tx_counter)
    now = int(time.time())
    tx = {
        "id": tx_id, "object": "transaction", "status": "created",
        "amount": amount, "currency": body.get("currency"), "rail": body.get("rail"),
        "description": body.get("description"),
        "provenance": {}, "receipt": None, "livemode": False,
        "created_at": now, "updated_at": now,
    }
    transactions[tx_id] = tx
    payload = {"id": tx_id, "status": "created", "amount": amount,
               "currency": tx["currency"], "rail": tx["rail"]}
    cache_response(key, payload, 201)
    emit_webhook("transaction.created", tx)
    return jsonify(payload), 201


@app.get("/v1/transactions/<transaction_id>")
def get_transaction(transaction_id: str) -> Any:
    tx = transactions.get(transaction_id)
    if tx is None:
        return not_found("transaction", transaction_id)
    return jsonify(tx)


@app.post("/v1/transactions/<transaction_id>/attach-links")
def attach_links(transaction_id: str) -> Any:
    tx = transactions.get(transaction_id)
    if tx is None:
        return not_found("transaction", transaction_id)

    if tx["status"] in ("captured", "succeeded", "failed", "canceled"):
        return error(
            "provenance.immutable_after_capture", 409,
            f"Cannot modify provenance on transaction with status '{tx['status']}'.",
        )

    body = request.get_json(silent=True) or {}
    tx["provenance"] = {
        "artifact_id": body.get("artifact_id"),
        "certificate_id": body.get("certificate_id"),
        "decision_record_id": body.get("decision_record_id") or body.get("decision_id"),
        "dataset_id": body.get("dataset_id"),
        "model_id": body.get("model_id"),
        "output_id": body.get("output_id"),
        "receipt_hash": body.get("receipt_hash"),
        "external_reference": body.get("external_reference"),
        "provenance_metadata": body.get("provenance_metadata"),
    }
    emit_webhook("transaction.links_attached", tx)
    return jsonify({"ok": True, "provenance": tx["provenance"]})


@app.post("/v1/transactions/<transaction_id>/capture")
def capture_transaction(transaction_id: str) -> Any:
    cached, key = idempotent(f"POST:/v1/transactions/{transaction_id}/capture")
    if cached is not None:
        return jsonify(cached["payload"]), cached["status"]

    tx = transactions.get(transaction_id)
    if tx is None:
        return not_found("transaction", transaction_id)

    if tx["status"] not in ("created", "submitted"):
        return error(
            "state.invalid_transition", 409,
            f"Cannot capture transaction with status '{tx['status']}'.",
        )

    provenance = tx.get("provenance") or {}
    receipt_id = next_id("rcpt", receipt_counter)

    # Canonical payload — includes every field a verifier needs. Signing and
    # hashing cover this exact shape; sha256_hash + ed25519_sig are excluded
    # from the canonical form.
    base_receipt = {
        "receipt_id": receipt_id,
        "transaction_id": transaction_id,
        "policy_id": POLICY_ID,
        "decision_record_id": provenance.get("decision_record_id"),
        "certificate_id": provenance.get("certificate_id"),
        "artifact_id": provenance.get("artifact_id"),
        "signing_key_id": SIGNING_KEY_ID,
        "signature_alg": "Ed25519",
        "status": "captured",
        "schema_version": "payment_receipt.v1",
    }
    canonical = canonical_json(base_receipt)
    sha256_hash = hashlib.sha256(canonical).hexdigest()
    signature = sign_payload(canonical)

    receipt = {**base_receipt, "sha256_hash": sha256_hash, "ed25519_sig": signature}
    tx["status"] = "captured"
    tx["receipt"] = receipt
    receipts[receipt_id] = receipt

    payload = {"id": transaction_id, "status": "captured", "receipt": receipt}
    cache_response(key, payload, 200)
    emit_webhook("transaction.captured", tx)
    return jsonify(payload)


@app.post("/v1/transactions/<transaction_id>/cancel")
def cancel_transaction(transaction_id: str) -> Any:
    tx = transactions.get(transaction_id)
    if tx is None:
        return not_found("transaction", transaction_id)
    if tx["status"] in ("captured", "succeeded", "failed", "canceled"):
        return error(
            "state.invalid_transition", 409,
            f"Cannot cancel transaction with status '{tx['status']}'.",
        )
    tx["status"] = "canceled"
    emit_webhook("transaction.canceled", tx)
    return jsonify(tx)


@app.get("/api/payments/verify/<receipt_id>")
def verify_receipt(receipt_id: str) -> Any:
    receipt = receipts.get(receipt_id)
    if receipt is None:
        return not_found("receipt", receipt_id)

    base_receipt = {k: v for k, v in receipt.items() if k not in ("sha256_hash", "ed25519_sig")}
    canonical = canonical_json(base_receipt)
    hash_valid = hashlib.sha256(canonical).hexdigest() == receipt.get("sha256_hash")
    signature_valid = verify_signature(canonical, str(receipt.get("ed25519_sig", "")))
    valid = hash_valid and signature_valid

    response = {
        "valid": valid,
        "hashValid": hash_valid,
        "signatureValid": signature_valid,
        "signingKeyId": SIGNING_KEY_ID,
        "signatureAlg": "Ed25519",
        "mockNote": "Local development mock. Receipts are not verifiable against the real platform.",
    }
    if SIGNATURE_MODE != "cryptographic":
        response["simulatedNote"] = "cryptography not installed; signature validation is simulated"
    return jsonify(response)


def main() -> None:
    print("CertifiedData Agent Commerce — Mock Server  [DEMO ONLY]")
    print(f"Listening on http://localhost:{PORT}")
    print(f"Signing key ID: {SIGNING_KEY_ID}  (fictional — not a production key)")
    if SIGNATURE_MODE == "cryptographic":
        print("Signature mode: ephemeral Ed25519 keypair (generated at startup, not persisted)")
    else:
        print("Signature mode: simulated (install cryptography for real Ed25519 signing)")
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
