#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — Idempotency Replay Demo

Proves that POST /v1/transactions/{id}/capture with the same Idempotency-Key
returns the *same* signed receipt on retry — including the same receipt_id,
sha256_hash, and ed25519_sig. This is the governance guarantee that agents
can safely retry after network partitions without double-capturing.

Run:
    python examples/claude-demo/demo_idempotency.py
    CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo_idempotency.py
"""

import os
import sys
import time

_DEMO_KEY = "cdp_test_demo_certifieddata_io_2026"
os.environ.setdefault("CDAC_API_KEY", _DEMO_KEY)

try:
    from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient
except ImportError:
    print("  SDK not installed: pip install certifieddata-agent-commerce", file=sys.stderr)
    sys.exit(1)


class C:
    RESET, BOLD, GREEN, CYAN, GREY, RED = (
        "\033[0m", "\033[1m", "\033[32m", "\033[36m", "\033[90m", "\033[31m",
    )


def main() -> None:
    base_url = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io")
    print(f"\n{C.BOLD}CertifiedData Agent Commerce — Idempotency-replay demo{C.RESET}")
    print(f"{C.GREY}Target: {base_url}{C.RESET}\n")

    client = CertifiedDataAgentCommerceClient()

    tx = client.transactions.create(
        amount=1500, currency="usd", rail="stripe",
        idempotency_key=f"idem-demo-{time.time_ns()}",
    )
    tx_id = tx["id"]
    client.transactions.attach_links(tx_id, decision_record_id="dec_idem_demo")

    capture_key = f"capture-{tx_id}"

    first  = client.transactions.capture(tx_id, idempotency_key=capture_key)
    second = client.transactions.capture(tx_id, idempotency_key=capture_key)

    r1 = first.get("receipt") or {}
    r2 = second.get("receipt") or {}
    fields = ("receipt_id", "sha256_hash", "ed25519_sig",
              "decision_record_id", "certificate_id", "artifact_id")

    all_match = True
    for f in fields:
        v1, v2 = r1.get(f), r2.get(f)
        if v1 == v2:
            print(f"  {C.GREEN}✓{C.RESET}  {f:<22} identical  ({str(v1)[:48]}…)" if v1 and len(str(v1)) > 48
                  else f"  {C.GREEN}✓{C.RESET}  {f:<22} identical  ({v1})")
        else:
            print(f"  {C.RED}✗{C.RESET}  {f:<22} DIFFER  first={v1!r}  second={v2!r}")
            all_match = False

    print()
    if all_match:
        print(f"{C.BOLD}{C.GREEN}Replay-safe: same Idempotency-Key returned the same signed receipt.{C.RESET}")
        print(f"{C.GREY}Agents can retry capture across network partitions without risk of double-capture.{C.RESET}\n")
    else:
        print(f"{C.BOLD}{C.RED}Idempotency guarantee violated — receipts differ across retries.{C.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
