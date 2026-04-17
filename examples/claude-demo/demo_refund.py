#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — End-to-End Refund Demo

Captures a transaction and then issues a partial refund. Demonstrates that
refund records link back to the original transaction_id for reconciliation.

NOTE: the bundled Flask mock at examples/claude-demo/mock_server.py does not
implement refunds. Run against the packages/mock-server Express mock or a
sandbox / live environment:

    pnpm --filter @certifieddata/agent-commerce-mock-server start

Run:
    CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo_refund.py
"""

import os
import sys
import time

os.environ.setdefault("CDAC_API_KEY", "cdp_test_demo_certifieddata_io_2026")

try:
    from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient, CDACError
except ImportError:
    print("  SDK not installed: pip install certifieddata-agent-commerce", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    client = CertifiedDataAgentCommerceClient()
    base_url = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io")

    print(f"\nCertifiedData Agent Commerce — Refund demo")
    print(f"  Target: {base_url}\n")

    tx = client.transactions.create(
        amount=5000,
        currency="usd",
        rail="stripe",
        idempotency_key=f"refund-demo-{time.time_ns()}",
    )
    client.transactions.attach_links(tx["id"], decision_record_id="dec_refund_demo")
    client.transactions.capture(tx["id"])
    print(f"  ✓ captured    id={tx['id']}  amount=$50.00")

    try:
        refund = client.refunds.create(
            transaction_id=tx["id"],
            amount=1500,
            reason="partial refund — customer request",
            idempotency_key=f"rf-{tx['id']}-001",
        )
    except CDACError as e:
        print(f"\n  ✗  refund failed: HTTP {e.http_status} — {e}", file=sys.stderr)
        print(f"  NOTE: the Flask demo mock does not implement refunds. Use the Express "
              f"mock or a real environment.", file=sys.stderr)
        sys.exit(1)

    print(f"  ✓ refund      id={refund.get('id')}  amount=$15.00  "
          f"status={refund.get('status')}")
    print(f"\n  Transaction {tx['id']} has been partially refunded.")
    print(f"  Original receipt still verifies — refunds are separate resources.\n")


if __name__ == "__main__":
    main()
