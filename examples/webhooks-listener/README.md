# Webhooks Listener Example

Tiny Flask listener that registers itself with the CDAC mock server and
verifies the `CDAC-Signature` header on every delivery.

## Run

```bash
# 1. Start the mock
python examples/claude-demo/mock_server.py

# 2. Start the listener (self-registers, prints secret)
python examples/webhooks-listener/listener.py

# 3. Trigger events
CDAC_BASE_URL=http://localhost:3456 \
  python examples/claude-demo/demo.py
```

Events will appear in the listener terminal. Invalid signatures return HTTP 400.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `CDAC_BASE_URL` | `http://localhost:3456` | Mock server URL |
| `LISTENER_PORT` | `4567` | Port to listen on |
| `CDAC_WEBHOOK_SECRET` | `whsec_mock_listener_secret` | Shared HMAC secret |

## Signature format

```
CDAC-Timestamp:  1714000000
CDAC-Signature:  t=1714000000,v1=<hmac_sha256_hex>
```

The `v1` component is `HMAC-SHA256(secret, "{ts}." + raw_body)`.
