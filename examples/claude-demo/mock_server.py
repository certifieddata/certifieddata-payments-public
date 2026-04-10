#!/usr/bin/env python3
"""Self-contained Flask mock server for the public Claude demo."""

from __future__ import annotations

import base64
import hashlib
import itertools
import json
import sys
from typing import Any

try:
    from flask import Flask, jsonify, request
except ImportError:
    print("Flask is required. Run: pip install flask", file=sys.stderr)
    raise

try:
    from cryptography.hazmat.primitives import serialization
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
SIGNING_KEY_ID = "cd_root_2026"

app = Flask(__name__)
transactions: dict[str, dict[str, Any]] = {}
receipts: dict[str, dict[str, Any]] = {}
tx_counter = itertools.count(1)
receipt_counter = itertools.count(1)


def next_id(prefix: str, counter: itertools.count) -> str:
    return f"{prefix}_mock_{next(counter):06d}"


def canonical_json(data: dict[str, Any]) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")


def static_signature(payload: bytes) -> str:
    digest = hashlib.sha256(payload + b":mock-signature").digest()
    return base64.urlsafe_b64encode(digest * 2).decode("ascii").rstrip("=")


if Ed25519PrivateKey is not None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    SIGNATURE_MODE = "cryptographic"
else:
    private_key = None
    public_key = None
    public_key_pem = None
    SIGNATURE_MODE = "simulated"


def sign_payload(payload: bytes) -> str:
    if private_key is None:
        return static_signature(payload)
    signature = private_key.sign(payload)
    return base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")


def verify_signature(payload: bytes, signature_text: str) -> bool:
    if public_key is None or Ed25519PublicKey is None:
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
        {
            "error": {
                "code": f"{resource}.not_found",
                "http_status": 404,
                "message": f"{resource} {resource_id} not found.",
            }
        },
        404,
    )


@app.get("/v1/health")
def health() -> Any:
    return jsonify(
        {
            "status": "ok",
            "mode": "mock",
            "livemode": False,
            "signatureMode": SIGNATURE_MODE,
        }
    )


@app.post("/v1/transactions")
def create_transaction() -> Any:
    body = request.get_json(silent=True) or {}
    tx_id = next_id("txn", tx_counter)
    transactions[tx_id] = {
        "id": tx_id,
        "object": "transaction",
        "status": "created",
        "amount": body.get("amount"),
        "currency": body.get("currency"),
        "rail": body.get("rail"),
        "provenance": {},
        "receipt": None,
        "livemode": False,
    }
    return jsonify({"id": tx_id, "status": "created"}), 201


@app.post("/v1/transactions/<transaction_id>/attach-links")
def attach_links(transaction_id: str) -> Any:
    tx = transactions.get(transaction_id)
    if tx is None:
        return not_found("transaction", transaction_id)

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
    return jsonify({"ok": True})


@app.post("/v1/transactions/<transaction_id>/capture")
def capture_transaction(transaction_id: str) -> Any:
    tx = transactions.get(transaction_id)
    if tx is None:
        return not_found("transaction", transaction_id)

    decision_record_id = tx.get("provenance", {}).get("decision_record_id")
    receipt_id = next_id("rcpt", receipt_counter)

    base_receipt = {
        "receipt_id": receipt_id,
        "transaction_id": transaction_id,
        "policy_id": POLICY_ID,
        "decision_record_id": decision_record_id,
        "signing_key_id": SIGNING_KEY_ID,
        "signature_alg": "Ed25519",
        "status": "captured",
    }
    canonical = canonical_json(base_receipt)
    sha256_hash = hashlib.sha256(canonical).hexdigest()
    signature = sign_payload(canonical)

    receipt = {
        **base_receipt,
        "sha256_hash": sha256_hash,
        "ed25519_sig": signature,
    }

    tx["status"] = "captured"
    tx["receipt"] = receipt
    receipts[receipt_id] = receipt

    return jsonify(
        {
            "id": transaction_id,
            "status": "captured",
            "receipt": receipt,
        }
    )


@app.get("/api/payments/verify/<receipt_id>")
def verify_receipt(receipt_id: str) -> Any:
    receipt = receipts.get(receipt_id)
    if receipt is None:
        return not_found("receipt", receipt_id)

    base_receipt = {
        "receipt_id": receipt["receipt_id"],
        "transaction_id": receipt["transaction_id"],
        "policy_id": receipt["policy_id"],
        "decision_record_id": receipt.get("decision_record_id"),
        "signing_key_id": receipt["signing_key_id"],
        "signature_alg": receipt["signature_alg"],
        "status": receipt["status"],
    }
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
    }
    if SIGNATURE_MODE != "cryptographic":
        response["mockNote"] = "cryptography not installed; signature validation is simulated"
    if public_key_pem:
        response["publicKeyPem"] = public_key_pem
    return jsonify(response)


def main() -> None:
    print("CertifiedData Agent Commerce - Mock Server")
    print(f"Listening on http://localhost:{PORT}")
    print("This is a development mock - not connected to sandbox or live")
    if SIGNATURE_MODE == "cryptographic":
        print("Signature mode: Ed25519 keypair generated for this session")
    else:
        print("Signature mode: simulated (install cryptography for real Ed25519 signing)")
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
