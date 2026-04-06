"""
Example: Create and submit a settlement using the CertifiedData Payments Python SDK.

Run against mock server:
    python examples/python-basic/create-settlement.py
"""

import sys
import os

# Allow running from repo root without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../packages/python-sdk/src"))

from certifieddata_payments import CertifiedDataPaymentsClient

client = CertifiedDataPaymentsClient(
    api_key="cdp_test_example_key",
    base_url="http://localhost:3456",
)

def main() -> None:
    # 1. Create a payee
    payee = client.payees.create(
        entity_type="company",
        legal_name="Atlas Synthetic Labs, Inc.",
        email="payments@atlas-synthetic.example",
        idempotency_key="py-payee-atlas-settlement-001",
    )
    print(f"Payee: {payee['id']}")

    # 2. Create a transaction to settle
    tx = client.transactions.create(
        amount=25000,
        currency="USD",
        rail="stripe",
        payee_id=payee["id"],
        description="Certified artifact purchase",
        idempotency_key="py-tx-settlement-001",
    )
    print(f"Transaction: {tx['id']}, status: {tx['status']}")

    # 3. Capture the transaction
    captured = client.transactions.capture(
        tx["id"],
        idempotency_key=f"py-capture-{tx['id']}",
    )
    print(f"Captured: {captured['id']}, status: {captured['status']}")

    # 4. Create a settlement referencing the captured transaction
    settlement = client.settlements.create(
        payee_id=payee["id"],
        amount=25000,
        currency="USD",
        transaction_ids=[captured["id"]],
        idempotency_key="py-settlement-batch-001",
    )
    print(f"Settlement: {settlement['id']}, status: {settlement['status']}")

    # 5. Submit the settlement
    submitted = client.settlements.submit(
        settlement["id"],
        idempotency_key=f"py-submit-{settlement['id']}",
    )
    print(f"Submitted: {submitted['id']}, status: {submitted['status']}")


if __name__ == "__main__":
    main()
