#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — End-to-End Settlement Demo

Captures multiple transactions for a single payee, then creates and submits a
settlement that batches them together.

Flow:
    1. create payee
    2. capture N transactions against payee
    3. create settlement batching the transaction_ids
    4. submit() the settlement
    5. show resulting settlement status

NOTE: the bundled Flask mock at examples/claude-demo/mock_server.py does not
implement payees/settlements. Run against the Express mock or a sandbox:

    pnpm --filter @certifieddata/agent-commerce-mock-server start

Run:
    CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo_settlement.py
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


AMOUNTS = [2500, 1800, 4200]


def main() -> None:
    client = CertifiedDataAgentCommerceClient()
    base_url = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io")

    print(f"\nCertifiedData Agent Commerce — Settlement demo")
    print(f"  Target: {base_url}\n")

    try:
        payee = client.payees.create(
            entity_type="company",
            legal_name="Atlas Synthetic Labs, Inc.",
            email="payments@atlas-synthetic.example",
            default_payout_method="stripe",
            idempotency_key=f"payee-settle-demo-{time.time_ns()}",
        )
    except (CDACError, AttributeError) as e:
        print(f"  ✗  payees.create failed: {e}", file=sys.stderr)
        print(f"  NOTE: the Flask demo mock does not implement payees.", file=sys.stderr)
        sys.exit(1)

    payee_id = payee["id"]
    print(f"  ✓ payee       id={payee_id}")

    tx_ids: list[str] = []
    total = 0
    for idx, amt in enumerate(AMOUNTS, start=1):
        tx = client.transactions.create(
            amount=amt, currency="usd", rail="stripe", payee_id=payee_id,
            idempotency_key=f"settle-tx-{idx}-{time.time_ns()}",
        )
        client.transactions.capture(tx["id"])
        tx_ids.append(tx["id"])
        total += amt
        print(f"  ✓ captured    [{idx}/{len(AMOUNTS)}] id={tx['id']}  amount={amt}c")

    settlement = client.settlements.create(
        payee_id=payee_id,
        amount=total,
        currency="usd",
        transaction_ids=tx_ids,
        idempotency_key=f"stl-{payee_id}-{time.time_ns()}",
    )
    print(f"\n  ✓ settlement  id={settlement['id']}  total={total}c  "
          f"transactions={len(tx_ids)}")

    submitted = client.settlements.submit(settlement["id"])
    print(f"  ✓ submitted   status={submitted.get('status')}")
    print()


if __name__ == "__main__":
    main()
