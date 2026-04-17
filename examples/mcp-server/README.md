# MCP Server Example

Expose CertifiedData Agent Commerce as a Model Context Protocol server so any
MCP-aware client (Claude Desktop, Claude Code, Cline, etc.) can execute
policy-governed payments and return signed receipts.

## Tools

| Tool | Purpose |
|------|---------|
| `execute_agent_payment` | Create + attach provenance + capture. Returns the inline signed receipt. |
| `verify_receipt` | Public verification of any `receipt_id`. No auth required. |
| `get_capabilities` | Fetch machine-readable `/v1/capabilities`. |

## Install

```bash
pip install mcp certifieddata-agent-commerce
```

## Claude Desktop config

```json
{
  "mcpServers": {
    "cdac": {
      "command": "python",
      "args": ["/abs/path/to/examples/mcp-server/server.py"],
      "env": {
        "CDAC_API_KEY": "cdp_test_xxx",
        "CDAC_BASE_URL": "https://certifieddata.io"
      }
    }
  }
}
```

## Local mock

```bash
# terminal A
python examples/claude-demo/mock_server.py
# terminal B — point the MCP server at the local mock:
CDAC_BASE_URL=http://localhost:3456 python examples/mcp-server/server.py
```

## Fallback mode

If `mcp` isn't installed the script prints the tool schemas as JSON so they
can be pasted into any other tool-calling framework (OpenAI tools, LangChain
`StructuredTool`, Anthropic tool-use, etc.).
