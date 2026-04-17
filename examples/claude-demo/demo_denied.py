#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — Governance / Denied-Path Demo

Proves that governance is not just happy-path theatre. Exercises three failure
modes that should be visible to any developer integrating CDAC:

    A. sandbox amount-limit exceeded        (policy rejection)
    B. attach provenance after capture      (state-machine rejection)
    C. cancel after capture                 (state-machine rejection)

Every failure surfaces a machine-readable error code and HTTP status — never a
silent failure or a generic 500.

Run:
    python examples/claude-demo/demo_denied.py
    CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo_denied.py
"""

import os
import sys
import time

_DEMO_KEY = "cdp_test_demo_certifieddata_io_2026"
os.environ.setdefault("CDAC_API_KEY", _DEMO_KEY)

try:
    from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient, CDACError
except ImportError:
    print("  SDK not installed: pip install certifieddata-agent-commerce", file=sys.stderr)
    sys.exit(1)


class C:
    RESET, BOLD, GREEN, CYAN, GREY, RED, YEL = (
        "\033[0m", "\033[1m", "\033[32m", "\033[36m", "\033[90m", "\033[31m", "\033[33m",
    )


def log(phase: str, msg: str) -> None:
    print(f"\n{C.BOLD}{C.CYAN}{phase}{C.RESET}  {msg}")


def expect_error(label: str, fn) -> CDACError | None:
    try:
        fn()
    except CDACError as e:
        print(f"  {C.GREEN}✓{C.RESET}  {C.BOLD}{label}{C.RESET}  HTTP {e.http_status} — {e}")
        return e
    print(f"  {C.RED}✗{C.RESET}  {C.BOLD}{label}{C.RESET}  expected error, got success", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    base_url = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io")
    print(f"\n{C.BOLD}CertifiedData Agent Commerce — Governance demo{C.RESET}")
    print(f"{C.GREY}Target: {base_url}{C.RESET}")

    client = CertifiedDataAgentCommerceClient()

    # ── A. Sandbox amount limit ────────────────────────────────────────────
    log("A", "Sandbox amount limit — expect sandbox_amount_limit_exceeded (HTTP 400)")
    expect_error(
        "policy_reject",
        lambda: client.transactions.create(
            amount=100_000_001,
            currency="usd",
            rail="stripe",
            idempotency_key=f"denied-amount-{time.time_ns()}",
        ),
    )

    # ── B. Attach provenance after capture ─────────────────────────────────
    log("B", "attach-links after capture — expect provenance.immutable_after_capture (HTTP 409)")
    tx = client.transactions.create(
        amount=2500,
        currency="usd",
        rail="stripe",
        idempotency_key=f"denied-attach-{time.time_ns()}",
    )
    client.transactions.capture(tx["id"])
    expect_error(
        "provenance_after_capture",
        lambda: client.transactions.attach_links(
            tx["id"],
            decision_record_id="dec_too_late",
        ),
    )

    # ── C. Cancel after capture ────────────────────────────────────────────
    log("C", "cancel() after capture — expect state.invalid_transition (HTTP 409)")
    expect_error(
        "cancel_after_capture",
        lambda: client.transactions.cancel(tx["id"]),
    )

    print(f"\n{C.BOLD}{C.GREEN}All 3 governance paths denied as expected{C.RESET}")
    print(f"{C.GREY}  → Each rejection returned a typed error code — suitable for programmatic handling.{C.RESET}\n")


if __name__ == "__main__":
    main()
