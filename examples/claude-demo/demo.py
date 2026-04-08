#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — End-to-End Demo (Python)

Demonstrates the 5-phase agent payment workflow using the live SDK.

Setup:
    pip install certifieddata-agent-commerce

Run:
    CDAC_API_KEY=cdp_test_xxx python examples/claude-demo/demo.py
    # against sandbox:
    CDAC_API_KEY=cdp_test_xxx CDAC_BASE_URL=https://sandbox.certifieddata.io \
        python examples/claude-demo/demo.py

Phases:
    1 — Agent declares intent (create transaction)
    2 — Attach provenance links (bind decision record)
    3 — Policy evaluation + authorization
    4 — Execute — settlement + inline signed receipt
    5 — Independent verification (public, no auth)
"""

import os
import sys
import json
import requests

try:
    from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient, CDACError
except ImportError:
    print("\n  SDK not installed. Run:\n    pip install certifieddata-agent-commerce\n", file=sys.stderr)
    sys.exit(1)


class C:
    RESET = "\033[0m"
    BOLD  = "\033[1m"
    GREEN = "\033[32m"
    CYAN  = "\033[36m"
    GREY  = "\033[90m"
    RED   = "\033[31m"


def log(phase: str, msg: str) -> None:
    print(f"\n{C.BOLD}{C.CYAN}{phase}{C.RESET}  {msg}")


def ok(label: str, detail: str) -> None:
    print(f"  {C.GREEN}✓{C.RESET}  {C.BOLD}{label}{C.RESET}  {detail}")


def fail(label: str, detail: str) -> None:
    print(f"\n  {C.RED}✗{C.RESET}  {C.BOLD}{label}{C.RESET}  {detail}", file=sys.stderr)
    sys.exit(1)


BASE_URL = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io")


def main() -> None:
    print(f"\n{C.BOLD}CertifiedData Agent Commerce — Demo{C.RESET}")
    print(f"{C.GREY}Target: {BASE_URL}{C.RESET}")
    print(f"{C.GREY}SDK:    certifieddata-agent-commerce{C.RESET}")

    # Init client — reads CDAC_API_KEY + CDAC_BASE_URL from env
    try:
        client = CertifiedDataAgentCommerceClient()
    except ValueError as e:
        print(f"\n  {C.RED}Config error:{C.RESET} {e}", file=sys.stderr)
        print("  Set:  export CDAC_API_KEY=cdp_test_xxx", file=sys.stderr)
        sys.exit(1)

    # ── Phase 1: Agent declares intent ───────────────────────────────────────────
    log("Phase 1", "Agent declares intent — what, why, how much")

    tx = client.transactions.create(
        amount=2500,       # cents ($25.00)
        currency="usd",
        rail="stripe",
        idempotency_key=f"demo-{__import__('time').time_ns()}",
    )
    tx_id = tx["id"]
    ok("transaction_created", f"id={tx_id}  status={tx.get('status')}")

    # ── Phase 2: Attach provenance links ─────────────────────────────────────────
    log("Phase 2", "Attach provenance — bind decision record to payment")

    client.transactions.attach_links(
        tx_id,
        decision_id="dec_agent_demo_2026",
        artifact_id="art_gpu_compute_001",
    )
    ok("links_attached", "decision_id=dec_agent_demo_2026  artifact_id=art_gpu_compute_001")
    print(f"  {C.GREY}  This links the AI system's decision lineage to the financial action.{C.RESET}")

    # ── Phase 3 + 4: Capture — authorize + execute + inline receipt ───────────────
    log("Phase 3 + 4", "capture() — policy eval → authorize → execute → inline signed receipt")
    print(f"  {C.GREY}→ POST /v1/transactions/{tx_id}/capture{C.RESET}")

    try:
        capture = client.transactions.capture(tx_id)
    except CDACError as e:
        fail("capture", f"API error {e.status_code}: {e}")

    status  = capture.get("status")
    receipt = capture.get("receipt")

    if not receipt:
        fail("receipt", "receipt not inlined in capture response")

    receipt_id = receipt.get("receipt_id") or receipt.get("id")
    if not receipt_id:
        fail("receipt_id", "receipt_id missing from receipt payload")

    ok("settled",        f"transaction_id={tx_id}  status={status}")
    ok("receipt_inline", f"receipt_id={receipt_id}")

    print(f"\n{C.GREY}Signed receipt (inline, no second fetch):{C.RESET}")
    print(C.GREY + json.dumps(receipt, indent=2) + C.RESET)

    # ── Phase 5: Independent verification — raw requests, no SDK ─────────────────
    log("Phase 5", "Independent verification — Ed25519 + SHA-256, no auth required")
    verify_url = f"{BASE_URL}/api/payments/verify/{receipt_id}"
    print(f"  {C.GREY}→ GET {verify_url}  (public endpoint, no auth){C.RESET}")

    resp = requests.get(verify_url, timeout=15)
    if not resp.ok:
        fail("verify_request", f"HTTP {resp.status_code}: {resp.text}")

    verify = resp.json()

    if not verify.get("hashValid"):
        fail("hash_integrity", "hashValid=false — receipt payload may have been tampered")
    if not verify.get("signatureValid"):
        fail("ed25519_sig", "signatureValid=false — Ed25519 signature invalid")
    if not verify.get("valid"):
        fail("verify_overall", "valid=false — overall verification failed")

    ok("hash_integrity", "hashValid=true    SHA-256 matches stored payload")
    ok("ed25519_sig",    "signatureValid=true  Ed25519 verified against public key")
    ok("verify_overall", "valid=true  receipt is tamper-evident and independently verifiable")

    # ── Summary ───────────────────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print(f"{C.BOLD}{C.GREEN}All 5 phases passed{C.RESET}")
    print(f"\n  Receipt ID:   {receipt_id}")
    print(f"  Verify URL:   {verify_url}")
    print(f"  Signed by:    {verify.get('signingKeyId', 'cd_root_2026')}  (Ed25519)")
    print(f"\n  {C.GREY}The agent transacted. The receipt proves it — cryptographically.{C.RESET}\n")


if __name__ == "__main__":
    main()
