# Verify-Only Example

Minimum-viable receipt verification. No SDK, no API key, no login.

## One-liner (curl)

```bash
curl -s https://certifieddata.io/api/payments/verify/<receipt_id> | jq .
```

## One-liner (Python stdlib)

```python
import json, urllib.request
r = urllib.request.urlopen("https://certifieddata.io/api/payments/verify/<receipt_id>")
print(json.loads(r.read()))
```

## Scriptable

```bash
python examples/verify-only/verify.py <receipt_id>
# exit 0 = valid, exit 1 = invalid/unreachable
```

## What it returns

```json
{
  "valid": true,
  "hashValid": true,
  "signatureValid": true,
  "signingKeyId": "cd_root_2026",
  "signatureAlg": "Ed25519"
}
```

`valid == hashValid && signatureValid`. Use these booleans directly in your
reconciliation / audit pipeline.
