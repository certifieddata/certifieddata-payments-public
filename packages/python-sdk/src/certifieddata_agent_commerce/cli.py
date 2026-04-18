"""
``cdac`` — CertifiedData Agent Commerce command-line helper.

Usage::

    cdac demo                   # run the basic 5-phase demo
    cdac demo certified         # certified-artifact variant
    cdac demo denied            # governance/denied-path demo
    cdac demo idempotency       # idempotency-replay demo
    cdac verify <receipt_id>    # independent verify against the public endpoint
    cdac capabilities           # GET /v1/capabilities
    cdac health                 # GET /v1/health

Reads ``CDAC_API_KEY`` and ``CDAC_BASE_URL`` from the environment. A built-in
public demo key is used when none is set.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DEFAULT_BASE_URL = "https://certifieddata.io"
DEMO_KEY = "cdp_test_demo_certifieddata_io_2026"


def _base_url() -> str:
    return (os.environ.get("CDAC_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def _ensure_key() -> None:
    if not os.environ.get("CDAC_API_KEY"):
        os.environ["CDAC_API_KEY"] = DEMO_KEY


def _exec_demo(name: str) -> int:
    """Locate and exec a demo script shipped with the repo."""
    repo_root = Path(__file__).resolve().parents[4]
    mapping = {
        "basic":       "examples/claude-demo/demo.py",
        "certified":   "examples/claude-demo/demo_certified.py",
        "denied":      "examples/claude-demo/demo_denied.py",
        "idempotency": "examples/claude-demo/demo_idempotency.py",
    }
    if name not in mapping:
        print(f"cdac: unknown demo '{name}'. options: {', '.join(mapping)}", file=sys.stderr)
        return 2
    script = repo_root / mapping[name]
    if not script.exists():
        print(f"cdac: demo script not found at {script}. "
              f"Run from a clone of the public repo or pass CDAC_DEMO_PATH.", file=sys.stderr)
        return 2
    _ensure_key()
    # Use runpy so the script runs as __main__ with the current interpreter.
    import runpy
    runpy.run_path(str(script), run_name="__main__")
    return 0


def _cmd_verify(argv: list[str]) -> int:
    if not argv:
        print("Usage: cdac verify <receipt_id>", file=sys.stderr)
        return 2
    receipt_id = argv[0]
    try:
        import urllib.request
        url = f"{_base_url()}/api/payments/verify/{receipt_id}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = resp.read().decode("utf-8")
            body = json.loads(data)
    except Exception as e:
        print(f"cdac verify: request failed — {e}", file=sys.stderr)
        return 1
    print(json.dumps(body, indent=2))
    return 0 if body.get("valid") else 1


def _cmd_capabilities() -> int:
    import urllib.request
    try:
        with urllib.request.urlopen(f"{_base_url()}/v1/capabilities", timeout=10) as resp:
            print(resp.read().decode("utf-8"))
        return 0
    except Exception as e:
        print(f"cdac capabilities: {e}", file=sys.stderr)
        return 1


def _cmd_health() -> int:
    import urllib.request
    try:
        with urllib.request.urlopen(f"{_base_url()}/v1/health", timeout=10) as resp:
            print(resp.read().decode("utf-8"))
        return 0
    except Exception as e:
        print(f"cdac health: {e}", file=sys.stderr)
        return 1


USAGE = """cdac — CertifiedData Agent Commerce CLI

Commands:
  demo [basic|certified|denied|idempotency]  run a bundled demo (default: basic)
  verify <receipt_id>                        independent public verification
  capabilities                               GET /v1/capabilities
  health                                     GET /v1/health

Environment:
  CDAC_API_KEY    API key (falls back to built-in public demo key)
  CDAC_BASE_URL   Default https://certifieddata.io
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "demo":
        return _exec_demo(rest[0] if rest else "basic")
    if cmd == "verify":
        return _cmd_verify(rest)
    if cmd == "capabilities":
        return _cmd_capabilities()
    if cmd == "health":
        return _cmd_health()
    print(f"cdac: unknown command '{cmd}'\n", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
