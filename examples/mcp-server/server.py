#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — MCP Server Example

Exposes CDAC payment operations as Model Context Protocol (MCP) tools so a
Claude Desktop / Claude Code / any MCP-aware client can execute
policy-governed payments and return signed receipts.

Tools exposed:
    execute_agent_payment    — create + attach_links + capture, returns receipt
    verify_receipt           — public verification of any receipt_id
    get_capabilities         — GET /v1/capabilities

Setup:
    pip install mcp certifieddata-agent-commerce
    export CDAC_API_KEY=cdp_test_xxx   # optional — public demo key used if unset

Run (stdio transport):
    python examples/mcp-server/server.py

Claude Desktop config snippet:
    {
      "mcpServers": {
        "cdac": {
          "command": "python",
          "args": ["/abs/path/to/examples/mcp-server/server.py"],
          "env": { "CDAC_API_KEY": "cdp_test_…" }
        }
      }
    }

This file degrades gracefully: if `mcp` is not installed it prints install
instructions and the tool schemas in JSON so they can be pasted into any other
tool-calling framework.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

DEMO_KEY = "cdp_test_demo_certifieddata_io_2026"
os.environ.setdefault("CDAC_API_KEY", DEMO_KEY)
BASE_URL = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io").rstrip("/")


# ── Tool schemas (portable) ──────────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "execute_agent_payment",
        "description": (
            "Run a policy-governed agent payment end-to-end: create transaction, "
            "attach provenance links (certificate_id, artifact_id, decision_record_id), "
            "capture, and return the inline signed receipt."
        ),
        "input_schema": {
            "type": "object",
            "required": ["amount", "justification"],
            "properties": {
                "amount":             {"type": "integer", "minimum": 1,
                                        "description": "Payment amount in cents."},
                "currency":           {"type": "string", "default": "usd"},
                "rail":               {"type": "string", "default": "stripe",
                                        "enum": ["stripe", "usdc_base", "usdc_ethereum", "eth_ethereum"]},
                "justification":      {"type": "string",
                                        "description": "Why the agent is paying (stored as description)."},
                "certificate_id":     {"type": "string"},
                "artifact_id":        {"type": "string"},
                "decision_record_id": {"type": "string",
                                        "description": "LLM run / trace ID — binds receipt to the decision."},
            },
        },
    },
    {
        "name": "verify_receipt",
        "description": "Publicly verify a CDAC receipt by ID. No auth required.",
        "input_schema": {
            "type": "object",
            "required": ["receipt_id"],
            "properties": {"receipt_id": {"type": "string"}},
        },
    },
    {
        "name": "get_capabilities",
        "description": "Fetch machine-readable capabilities from the CDAC API.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ── Tool implementations ─────────────────────────────────────────────────────

def _client():
    from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient
    return CertifiedDataAgentCommerceClient()


def execute_agent_payment(**kw: object) -> dict:
    client = _client()
    tx = client.transactions.create(
        amount=int(kw["amount"]),
        currency=str(kw.get("currency") or "usd"),
        rail=str(kw.get("rail") or "stripe"),
        description=str(kw.get("justification") or ""),
    )
    links = {
        "certificate_id":     kw.get("certificate_id"),
        "artifact_id":        kw.get("artifact_id"),
        "decision_record_id": kw.get("decision_record_id"),
    }
    if any(links.values()):
        client.transactions.attach_links(tx["id"], **{k: v for k, v in links.items() if v})
    cap = client.transactions.capture(tx["id"])
    receipt = cap.get("receipt") or {}
    return {
        "transaction_id": tx["id"],
        "receipt_id":     receipt.get("receipt_id"),
        "status":         cap.get("status"),
        "sha256_hash":    receipt.get("sha256_hash"),
        "ed25519_sig":    receipt.get("ed25519_sig"),
        "verify_url":     f"{BASE_URL}/api/payments/verify/{receipt.get('receipt_id')}",
        "decision_record_id": receipt.get("decision_record_id"),
    }


def verify_receipt(*, receipt_id: str) -> dict:
    with urllib.request.urlopen(
        f"{BASE_URL}/api/payments/verify/{receipt_id}", timeout=15
    ) as resp:
        return json.loads(resp.read().decode())


def get_capabilities() -> dict:
    with urllib.request.urlopen(f"{BASE_URL}/v1/capabilities", timeout=10) as resp:
        return json.loads(resp.read().decode())


TOOLS = {
    "execute_agent_payment": execute_agent_payment,
    "verify_receipt":        verify_receipt,
    "get_capabilities":      get_capabilities,
}


# ── MCP stdio server (preferred) ─────────────────────────────────────────────

def run_mcp() -> None:
    try:
        from mcp.server import Server  # type: ignore
        from mcp.server.stdio import stdio_server  # type: ignore
        from mcp.types import Tool, TextContent  # type: ignore
    except ImportError:
        print(
            "  `mcp` package not installed. Install it with:\n"
            "      pip install mcp\n\n"
            "  Tool schemas (copy-paste into any tool-calling framework):\n",
            file=sys.stderr,
        )
        print(json.dumps(TOOL_SCHEMAS, indent=2))
        sys.exit(1)

    import asyncio

    server: Server = Server("cdac-agent-commerce")

    @server.list_tools()
    async def list_tools() -> list:
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["input_schema"],
            )
            for t in TOOL_SCHEMAS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list:
        fn = TOOLS.get(name)
        if fn is None:
            return [TextContent(type="text", text=json.dumps({"error": f"unknown tool {name}"}))]
        try:
            result = fn(**arguments)
        except Exception as e:
            result = {"error": str(e)}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _run() -> None:
        async with stdio_server() as (reader, writer):
            await server.run(reader, writer, server.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    run_mcp()
