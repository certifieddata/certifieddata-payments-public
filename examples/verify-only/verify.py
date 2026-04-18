#!/usr/bin/env python3
"""
CertifiedData Agent Commerce — Verify-Only Example

The simplest possible integration: someone hands you a receipt_id (in a
webhook payload, an email, a PR comment, a URL query param) and you want to
confirm it's real — without an SDK, without an API key, without a login.

Usage:
    python examples/verify-only/verify.py <receipt_id>
    # or point at a local mock:
    CDAC_BASE_URL=http://localhost:3456 python examples/verify-only/verify.py <receipt_id>

Exit code:
    0  receipt is valid (hashValid=true AND signatureValid=true)
    1  receipt is invalid or unreachable
"""

import json
import os
import sys
import urllib.request


BASE_URL = os.environ.get("CDAC_BASE_URL", "https://certifieddata.io").rstrip("/")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python verify.py <receipt_id>", file=sys.stderr)
        return 2

    receipt_id = sys.argv[1]
    url = f"{BASE_URL}/api/payments/verify/{receipt_id}"

    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"verify: request failed — {e}", file=sys.stderr)
        return 1

    # Pretty-print for humans, use exit code for machines.
    print(json.dumps(body, indent=2))

    if body.get("valid"):
        print(f"\n  ✓  receipt {receipt_id} is valid", file=sys.stderr)
        return 0
    print(
        f"\n  ✗  receipt {receipt_id} failed verification  "
        f"hashValid={body.get('hashValid')}  signatureValid={body.get('signatureValid')}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
