"""
CertifiedData Agent Commerce — LLM Tool-Calling Example

Minimal copy-paste wrapper showing how to expose the SDK as an OpenAI-style
function/tool that an LLM can call.

The key pattern: pass the LLM's run/trace ID as `decision_record_id` so the
resulting signed receipt carries proof of which LLM decision triggered the spend.

Setup:
    pip install certifieddata-agent-commerce
    export CDAC_API_KEY=cdp_test_xxx   # from certifieddata.io/dashboard/cdp/api-keys

Run locally without any keys:
    pip install flask
    python examples/claude-demo/mock_server.py   # port 3456
    CDAC_API_KEY=cdp_test_any CDAC_BASE_URL=http://localhost:3456 python examples/agent_tool_example.py
"""

import os
import json
from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient

client = CertifiedDataAgentCommerceClient(
    api_key=os.environ.get("CDAC_API_KEY"),
    base_url=os.environ.get("CDAC_BASE_URL", "https://certifieddata.io"),
)


# ── 1. Tool schema (pass to your LLM/framework) ───────────────────────────────

payment_tool = {
    "type": "function",
    "function": {
        "name": "execute_agent_payment",
        "description": (
            "Authorize and capture a policy-governed payment on behalf of the agent. "
            "Returns a signed receipt that proves the payment was made and links it to "
            "the current model run for audit purposes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "integer",
                    "description": "Payment amount in cents (e.g. 2500 = $25.00)",
                    "minimum": 1,
                },
                "currency": {
                    "type": "string",
                    "description": "ISO 4217 currency code",
                    "default": "usd",
                },
                "justification": {
                    "type": "string",
                    "description": "Why the agent is making this payment — stored in the receipt",
                },
            },
            "required": ["amount", "justification"],
        },
    },
}


# ── 2. Tool implementation (called by your agent loop) ────────────────────────

def execute_agent_payment(
    *,
    amount: int,
    currency: str = "usd",
    justification: str,
    llm_run_id: str,  # injected by your framework — links receipt to LLM trace
) -> dict:
    """
    Execute an agent payment and return the signed receipt.

    `llm_run_id` is passed as `decision_record_id` so the receipt is permanently
    bound to the LLM decision that triggered it. Verify any receipt independently:

        GET https://certifieddata.io/api/payments/verify/<receipt_id>
        → { valid, hashValid, signatureValid, signingKeyId, signatureAlg }
    """
    try:
        # Phase 1 — declare intent
        tx = client.transactions.create(
            amount=amount,
            currency=currency,
        )
        tx_id = tx["id"]

        # Phase 2 — bind LLM lineage
        client.transactions.attach_links(
            tx_id,
            decision_record_id=llm_run_id,
        )

        # Phase 3+4 — policy eval → capture → inline signed receipt
        capture = client.transactions.capture(tx_id)
        receipt = capture["receipt"]

        return {
            "status": "success",
            "transaction_id": tx_id,
            "receipt_id": receipt.get("receipt_id"),
            "decision_record_id": receipt.get("decision_record_id"),
            "sha256_hash": receipt.get("sha256_hash"),
            "verification_url": (
                f"https://certifieddata.io/api/payments/verify/{receipt.get('receipt_id')}"
            ),
        }

    except Exception as exc:
        return {"status": "error", "message": str(exc)}


# ── 3. Demo (runs without a real LLM) ─────────────────────────────────────────

if __name__ == "__main__":
    result = execute_agent_payment(
        amount=2500,
        currency="usd",
        justification="Purchase external dataset for model training",
        llm_run_id="run_demo_2026_abc123",  # in production: your LLM trace/run ID
    )
    print(json.dumps(result, indent=2))

    if result["status"] == "success":
        print(f"\nVerify independently (no auth required):")
        print(f"  curl {result['verification_url']}")
