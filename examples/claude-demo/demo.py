#!/usr/bin/env python3
"""
CertifiedData Agent Commerce - End-to-End Demo (Python)

Demonstrates the 5-phase agent payment workflow using the public SDK.

Setup:
    pip install certifieddata-agent-commerce

Run:
    CDAC_API_KEY=cdp_test_xxx python examples/claude-demo/demo.py
    # against sandbox:
    CDAC_API_KEY=cdp_test_xxx CDAC_BASE_URL=https://sandbox.certifieddata.io \
        python examples/claude-demo/demo.py
"""

import json
import os
import sys
import time

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from certifieddata_agent_commerce import CDACError, CertifiedDataAgentCommerceClient
except ImportError:
    print("\n  SDK not installed. Run:\n    pip install certifieddata-agent-commerce\n", file=sys.stderr)
    sys.exit(1)


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    GREY = "\033[90m"
    RED = "\033[31m"


def log(phase: str, msg: str) -> None:
    print(f"\n{C.BOLD}{C.CYAN}{phase}{C.RESET}  {msg}")


def ok(label: str, detail: str) -> None:
    print(f"  {C.GREEN}✓{C.RESET}  {C.BOLD}{label}{C.RESET}  {detail}")


def fail(label: str, detail: str) -> None:
    print(f"\n  {C.RED}✗{C.RESET}  {C.BOLD}{label}{C.RESET}  {detail}", file=sys.stderr)
    sys.exit(1)


def preview(value: object, length: int) -> str:
    text = str(value or "")
    return f"{text[:length]}…" if text else "—"


BASE_URL = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io").rstrip("/")


def get_mode_label(url: str) -> str:
    lowered = url.lower()
    if "localhost" in lowered or "127.0.0.1" in lowered:
        return "local mock"
    if "sandbox" in lowered:
        return "sandbox"
    return "live"


def main() -> None:
    print(f"\n{C.BOLD}CertifiedData Agent Commerce - Demo{C.RESET}")
    print(f"{C.GREY}Mode:   {get_mode_label(BASE_URL)}{C.RESET}")
    print(f"{C.GREY}Target: {BASE_URL}{C.RESET}")
    print(f"{C.GREY}SDK:    certifieddata-agent-commerce{C.RESET}")

    try:
        client = CertifiedDataAgentCommerceClient()
    except ValueError as e:
        print(f"\n  {C.RED}Config error:{C.RESET} {e}", file=sys.stderr)
        print("  Set:  export CDAC_API_KEY=cdp_test_xxx", file=sys.stderr)
        sys.exit(1)

    log("Phase 1", "Agent declares intent - what, why, how much")

    tx = client.transactions.create(
        amount=2500,
        currency="usd",
        rail="stripe",
        idempotency_key=f"demo-{time.time_ns()}",
    )
    tx_id = tx["id"]
    ok("transaction_created", f"id={tx_id}  status={tx.get('status')}")

    log("Phase 2", "Attach provenance - bind decision record to payment")

    client.transactions.attach_links(
        tx_id,
        decision_record_id="dec_agent_demo_2026",
    )
    ok("links_attached", "decision_record_id=dec_agent_demo_2026")
    print(f"  {C.GREY}  This links the AI system's decision lineage to the financial action.{C.RESET}")

    log("Phase 3 + 4", "capture() - policy eval -> authorize -> execute -> inline signed receipt")
    print(f"  {C.GREY}-> POST /v1/transactions/{tx_id}/capture{C.RESET}")

    try:
        capture = client.transactions.capture(tx_id)
    except CDACError as e:
        fail("capture", f"API error {e.status_code}: {e}")

    status = capture.get("status")
    receipt = capture.get("receipt")

    if not receipt:
        fail("receipt", "receipt not inlined in capture response")

    receipt_id = receipt.get("receipt_id") or receipt.get("id")
    if not receipt_id:
        fail("receipt_id", "receipt_id missing from receipt payload")

    decision_record_id = receipt.get("decision_record_id")
    if not decision_record_id:
        fail("decision_record_id", "decision_record_id missing from inline receipt")

    ok("settled", f"transaction_id={tx_id}  status={status}")
    ok("receipt_inline", f"receipt_id={receipt_id}")

    sig = str(receipt.get("ed25519_sig") or receipt.get("signature") or "")
    print(f"\n{C.GREY}┌─ Inline signed receipt ─────────────────────────────────────┐{C.RESET}")
    print(f"{C.GREY}  Transaction ID  :{C.RESET} {tx_id}")
    print(f"{C.GREY}  Receipt ID      :{C.RESET} {receipt_id}")
    print(f"{C.GREY}  Policy ID       :{C.RESET} {receipt.get('policy_id', '—')}")
    print(f"{C.GREY}  Decision Record :{C.RESET} {decision_record_id}")
    print(f"{C.GREY}  SHA-256 Hash    :{C.RESET} {preview(receipt.get('sha256_hash', '—'), 32)}")
    print(f"{C.GREY}  Ed25519 Sig     :{C.RESET} {preview(sig, 48)}")
    print(f"{C.GREY}└─────────────────────────────────────────────────────────────┘{C.RESET}")
    print(f"\n{C.GREY}Full receipt JSON:{C.RESET}")
    print(C.GREY + json.dumps(receipt, indent=2) + C.RESET)

    log("Phase 5", "Independent verification - Ed25519 + SHA-256, no auth required")
    verify_url = f"{BASE_URL}/api/payments/verify/{receipt_id}"
    print(f"  {C.GREY}-> GET {verify_url} (public endpoint, no auth){C.RESET}")

    resp = requests.get(verify_url, timeout=15)
    if not resp.ok:
        fail("verify_request", f"HTTP {resp.status_code}: {resp.text}")

    verify = resp.json()

    if not verify.get("hashValid"):
        fail("hash_integrity", "hashValid=false - receipt payload may have been tampered")
    if not verify.get("signatureValid"):
        fail("ed25519_sig", "signatureValid=false - Ed25519 signature invalid")
    if not verify.get("valid"):
        fail("verify_overall", "valid=false - overall verification failed")

    ok("hash_integrity", "hashValid=true")
    ok("ed25519_sig", "signatureValid=true")
    ok("verify_overall", "valid=true")
    ok("signing_key", f"signingKeyId={verify.get('signingKeyId', 'cd_root_2026')}")

    lineage_bound = "yes" if receipt.get("decision_record_id") else "no"

    print(f"\n{'─' * 60}")
    print(f"{C.BOLD}{C.GREEN}All 5 phases passed{C.RESET}")
    print(f"\n  Receipt ID:     {receipt_id}")
    print(f"  Verify URL:     {verify_url}")
    print(f"  Signed by:      {verify.get('signingKeyId', 'cd_root_2026')}  (Ed25519)")
    print(f"  Lineage bound:  {lineage_bound}")
    print(f"\n  {C.GREY}The agent transacted. The receipt proves it - cryptographically.{C.RESET}\n")


if __name__ == "__main__":
    main()
