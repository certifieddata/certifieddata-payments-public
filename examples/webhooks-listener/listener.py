#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — Webhooks Listener Example

Runs a tiny Flask server that:
 1. Registers itself as a webhook endpoint with the CDAC mock server
 2. Receives live event deliveries (signed with HMAC-SHA256)
 3. Verifies the CDAC-Signature header before processing

Pair with the mock server so you can see the full event lifecycle in one shot:

    # Terminal A — start the mock
    python examples/claude-demo/mock_server.py

    # Terminal B — start this listener (will self-register)
    python examples/webhooks-listener/listener.py

    # Terminal C — run any demo, events will flow to Terminal B
    CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo.py

Environment:
    CDAC_BASE_URL     Default http://localhost:3456
    LISTENER_PORT     Default 4567
    CDAC_WEBHOOK_SECRET   If unset, one is generated and printed
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("  Flask is required: pip install flask", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("  requests is required: pip install requests", file=sys.stderr)
    sys.exit(1)


BASE_URL     = os.environ.get("CDAC_BASE_URL", "http://localhost:3456").rstrip("/")
PORT         = int(os.environ.get("LISTENER_PORT", "4567"))
TOLERANCE_S  = 300
SECRET       = os.environ.get("CDAC_WEBHOOK_SECRET", "whsec_mock_listener_secret")

app = Flask(__name__)


def verify_signature(body: bytes, signature_header: str, timestamp_header: str, secret: str) -> bool:
    try:
        ts = int(timestamp_header)
    except (TypeError, ValueError):
        return False
    if abs(int(time.time()) - ts) > TOLERANCE_S:
        return False
    v1 = None
    for part in signature_header.split(","):
        part = part.strip()
        if part.startswith("v1="):
            v1 = part[3:]
            break
    if not v1:
        return False
    expected = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)


@app.post("/webhooks/cdac")
def receive() -> tuple[str, int]:
    body = request.get_data()
    sig  = request.headers.get("CDAC-Signature", "")
    ts   = request.headers.get("CDAC-Timestamp", "")
    if not verify_signature(body, sig, ts, SECRET):
        print(f"  [!] signature INVALID — dropping request")
        return "invalid signature", 400

    envelope = json.loads(body)
    event_type = envelope.get("type", "?")
    data = envelope.get("data") or {}
    print(f"\n  [ok] {envelope.get('id')}  {event_type}")
    for k in ("id", "status"):
        if k in data:
            print(f"       {k}={data[k]}")
    receipt = data.get("receipt")
    if receipt:
        print(f"       receipt_id={receipt.get('receipt_id')}  "
              f"decision_record_id={receipt.get('decision_record_id')}")
    return "ok", 200


def self_register() -> None:
    url = f"http://127.0.0.1:{PORT}/webhooks/cdac"
    try:
        resp = requests.post(
            f"{BASE_URL}/v1/webhook_endpoints",
            json={"url": url, "secret": SECRET},
            timeout=3,
        )
        if resp.ok:
            print(f"  [ok] registered as webhook endpoint: id={resp.json().get('id')}")
        else:
            print(f"  [!] registration failed HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"  [!] registration failed ({e}) — is the mock server running?")


def main() -> None:
    print(f"\nCertifiedData Agent Commerce — Webhooks Listener")
    print(f"  Mock:     {BASE_URL}")
    print(f"  Listen:   http://127.0.0.1:{PORT}/webhooks/cdac")
    print(f"  Secret:   {SECRET}")
    self_register()
    print("  Waiting for events… (Ctrl-C to exit)\n")
    app.run(host="127.0.0.1", port=PORT, debug=False)


if __name__ == "__main__":
    main()
