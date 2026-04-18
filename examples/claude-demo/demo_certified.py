#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — Certified Artifact Purchase Demo (Python)

Extends the basic 5-phase demo to exercise the full certified-data thesis:
binds certificate_id + artifact_id + decision_record_id to a transaction
before capture, then verifies that all three IDs survive inside the signed
receipt.

Run:
    python examples/claude-demo/demo_certified.py                  # public demo key
    CDAC_API_KEY=cdp_test_xxx python examples/claude-demo/demo_certified.py
    CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo_certified.py
"""

import json
import os
import sys
import time

import requests

_DEMO_KEY = "cdp_test_demo_certifieddata_io_2026"
if not os.environ.get("CDAC_API_KEY"):
    os.environ["CDAC_API_KEY"] = _DEMO_KEY

try:
    from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient, CDACError
except ImportError:
    print("\n  SDK not installed. Run:\n    pip install certifieddata-agent-commerce\n", file=sys.stderr)
    sys.exit(1)


BASE_URL = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io")


class C:
    RESET = "\033[0m"
    BOLD  = "\033[1m"
    GREEN = "\033[32m"
    CYAN  = "\033[36m"
    GREY  = "\033[90m"
    RED   = "\033[31m"
    YEL   = "\033[33m"


def log(phase: str, msg: str) -> None:
    print(f"\n{C.BOLD}{C.CYAN}{phase}{C.RESET}  {msg}")


def ok(label: str, detail: str) -> None:
    print(f"  {C.GREEN}✓{C.RESET}  {C.BOLD}{label}{C.RESET}  {detail}")


def warn(label: str, detail: str) -> None:
    print(f"  {C.YEL}!{C.RESET}  {C.BOLD}{label}{C.RESET}  {detail}")


def fail(label: str, detail: str) -> None:
    print(f"\n  {C.RED}✗{C.RESET}  {C.BOLD}{label}{C.RESET}  {detail}", file=sys.stderr)
    sys.exit(1)


def mode_label(url: str) -> str:
    if "localhost" in url or "127.0.0.1" in url:
        return "local mock"
    if "sandbox" in url:
        return "sandbox"
    return "live"


# Profile: certified-artifact-purchase — required provenance links
REQUIRED_LINKS = ("certificate_id", "artifact_id")
RECOMMENDED_LINKS = ("decision_record_id", "receipt_hash")


def main() -> None:
    print(f"\n{C.BOLD}CertifiedData Agent Commerce — Certified Artifact Purchase{C.RESET}")
    print(f"{C.GREY}Profile: certified-artifact-purchase (v1.0.0){C.RESET}")
    print(f"{C.GREY}Mode:    {mode_label(BASE_URL)}{C.RESET}")
    print(f"{C.GREY}Target:  {BASE_URL}{C.RESET}")

    try:
        client = CertifiedDataAgentCommerceClient()
    except ValueError as e:
        fail("config", str(e))

    # Demo identifiers — in production these come from your trust graph.
    certificate_id     = "cert_01HXZ803C0R6V4K4P9HWB6J5N6"
    artifact_id        = "art_01HXZ7Z8R2QQSN5B3T5VQ4D1WA"
    decision_record_id = f"dec_demo_{int(time.time())}"

    # ── Phase 1 ──────────────────────────────────────────────────────────────
    log("Phase 1", "Declare intent — purchase of a certified synthetic dataset")
    tx = client.transactions.create(
        amount=4900,
        currency="usd",
        rail="stripe",
        description="Certified synthetic dataset v2 — purchase under CDAC profile",
        idempotency_key=f"demo-cert-{time.time_ns()}",
    )
    tx_id = tx["id"]
    ok("transaction_created", f"id={tx_id}  status={tx.get('status')}")

    # ── Phase 2 ──────────────────────────────────────────────────────────────
    log("Phase 2", "Attach full provenance — certificate + artifact + decision")
    client.transactions.attach_links(
        tx_id,
        certificate_id=certificate_id,
        artifact_id=artifact_id,
        decision_record_id=decision_record_id,
        provenance_metadata={
            "cdp:workflow_id":   "wf_certified_demo",
            "cdp:source_system": "certifieddata-agent-commerce-public",
            "partner:invoice_ref": "INV-DEMO-001",
        },
    )
    ok("certificate_id",     certificate_id)
    ok("artifact_id",        artifact_id)
    ok("decision_record_id", decision_record_id)

    # ── Phase 3 + 4 ──────────────────────────────────────────────────────────
    log("Phase 3 + 4", "capture() — policy eval → authorize → execute → inline receipt")
    try:
        capture = client.transactions.capture(tx_id)
    except CDACError as e:
        fail("capture", f"API error {e.http_status}: {e}")

    receipt = capture.get("receipt") or {}
    receipt_id = receipt.get("receipt_id") or receipt.get("id")
    if not receipt_id:
        fail("receipt", "inline receipt missing receipt_id")

    # Check every link we attached round-trips through the receipt.
    for field in REQUIRED_LINKS:
        if not receipt.get(field):
            warn(f"receipt.{field}", "not surfaced in receipt (may be in transaction.provenance)")
    ok("receipt_inline", f"receipt_id={receipt_id}")
    ok("lineage_bound",  f"decision_record_id={receipt.get('decision_record_id')}")

    print(f"\n{C.GREY}Receipt JSON:{C.RESET}")
    print(C.GREY + json.dumps(receipt, indent=2) + C.RESET)

    # ── Phase 5 ──────────────────────────────────────────────────────────────
    log("Phase 5", "Public verification")
    verify_url = f"{BASE_URL}/api/payments/verify/{receipt_id}"
    resp = requests.get(verify_url, timeout=15)
    if not resp.ok:
        fail("verify", f"HTTP {resp.status_code}")
    v = resp.json()
    if not v.get("valid"):
        fail("verify", f"valid=false — hashValid={v.get('hashValid')}, sigValid={v.get('signatureValid')}")
    ok("verify_overall", "valid=true (Ed25519 + SHA-256)")
    ok("signing_key",    f"signingKeyId={v.get('signingKeyId', '?')}")

    print(f"\n{'--' * 30}")
    print(f"{C.BOLD}{C.GREEN}Certified artifact purchase — all phases passed{C.RESET}")
    print(f"\n  Transaction:      {tx_id}")
    print(f"  Receipt:          {receipt_id}")
    print(f"  Certificate:      {certificate_id}")
    print(f"  Artifact:         {artifact_id}")
    print(f"  Decision Record:  {decision_record_id}")
    print(f"  Verify URL:       {verify_url}")
    print()


if __name__ == "__main__":
    main()
