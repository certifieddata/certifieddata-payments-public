# Quickstart

This guide gets you running locally with the mock server and either SDK.

## 1. Install an SDK

### TypeScript

```bash
pnpm add @certifieddata/payments
```

### Python

```bash
pip install certifieddata-agent-commerce
```

## 2. Start the mock server

```bash
pnpm install
pnpm --filter @certifieddata/agent-commerce-mock-server start
```

Health check:

```bash
curl http://localhost:3456/v1/health
```

Expected response:

```json
{ "status": "ok", "mode": "mock", "livemode": false }
```

## 3. Set environment variables

```bash
export CDAC_API_KEY=cdp_test_your_key
export CDP_API_VERSION=2025-01-01
export CDAC_BASE_URL=http://localhost:3456
```

## 4. Create a client

### TypeScript

```ts
import { CertifiedDataAgentCommerceClient } from "@certifieddata/payments";

const client = new CertifiedDataAgentCommerceClient({
  apiKey: process.env.CDAC_API_KEY!,
  apiVersion: "2025-01-01",
  baseUrl: process.env.CDAC_BASE_URL,
});
```

### Python

```python
from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient

client = CertifiedDataAgentCommerceClient(
    api_key="cdp_test_your_key",
    api_version="2025-01-01",
    base_url="http://localhost:3456",
)
```

## 5. Create a transaction

Typical flow:

1. create or reference a customer
2. create a payment intent or transaction
3. attach provenance links
4. confirm the payment flow
5. listen for webhook lifecycle events

### Example shape

```json
{
  "amount": 4900,
  "currency": "usd",
  "customer_id": "cus_123"
}
```

## 6. Attach provenance links

Attach commercial context to the funded object:

- artifact ID
- certificate ID
- decision ID
- workflow or invoice references
- partner metadata

See [`docs/provenance-links.md`](./provenance-links.md).

## 7. Add webhook handling

Before going live:

- verify webhook signatures using test vectors in `test-vectors/webhook-signature/`
- store event IDs for idempotency
- make handlers idempotent
- reconcile against transaction and settlement records

See [`docs/webhooks.md`](./webhooks.md).

## Next steps

- [Authentication](./authentication.md)
- [API resources](./api-resources.md)
- [Environments and versioning](./environments-and-versioning.md)
- [Errors and idempotency](./errors-and-idempotency.md)
