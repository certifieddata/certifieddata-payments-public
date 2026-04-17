#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — USDC (Base) Rail Demo

Mirrors the basic flow but uses the ``usdc_base`` rail listed in
capabilities.json. Proves the rail enum is not stripe-only.

Run:
    python examples/claude-demo/demo_usdc.py
    CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo_usdc.py
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


def main() -> None:
    base_url = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io")
    print(f"\nCertifiedData Agent Commerce — USDC (Base) demo")
    print(f"  Target: {base_url}\n")

    client = CertifiedDataAgentCommerceClient()

    tx = client.transactions.create(
        amount=2500,
        currency="usd",   # USDC pegged; capabilities treats currency independently of rail
        rail="usdc_base",
        description="Agent payment settled on USDC/Base",
        idempotency_key=f"usdc-demo-{time.time_ns()}",
    )
    print(f"  ✓ transaction_created  id={tx['id']}  rail=usdc_base")

    client.transactions.attach_links(tx["id"], decision_record_id=f"dec_usdc_{int(time.time())}")
    print(f"  ✓ attached decision_record_id")

    cap = client.transactions.capture(tx["id"])
    receipt = cap.get("receipt") or {}
    print(f"  ✓ captured  receipt_id={receipt.get('receipt_id')}  "
          f"rail={receipt.get('rail', 'usdc_base')}")
    print(f"\n  verify: {base_url}/api/payments/verify/{receipt.get('receipt_id')}\n")


if __name__ == "__main__":
    main()
