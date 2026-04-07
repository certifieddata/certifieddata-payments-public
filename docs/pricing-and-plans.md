# Pricing and Plans

CDP plan behavior controls what features and quotas are available to a user or integration.

## Plan families

| Plan | Key | Receipt quota | Agents | Signed receipts | Webhooks | Self-serve checkout |
|---|---|---|---|---|---|---|
| Sandbox (anonymous) | `sandbox_anon` | 10 lifetime | 1 | No | No | No |
| Sandbox (free account) | `sandbox_free_account` | 100/month | 1 | No | No | No |
| Build | `build_monthly` | 2,500/month | 3 | Yes | No | Yes |
| Trust | `trust_monthly` | 10,000/month | 15 | Yes | Yes | Yes |
| Govern | `govern_monthly` | 30,000/month | Unlimited | Yes | Yes | Yes |
| Enterprise | `enterprise_custom` | Custom | Custom | Yes | Yes | Contact sales |

## Sandbox plans

Sandbox plans are free and do not go through Stripe checkout.

- `sandbox_anon` — no signup required, 10 receipts total, ephemeral session only
- `sandbox_free_account` — signup required, 100 receipts/month, saved history

Sandbox receipts are not Ed25519-signed. Use a paid plan to test signed receipt issuance.

## Paid plan checkout

Paid plans use Stripe subscriptions. Self-serve checkout is available for Build, Trust, and Govern.

Enterprise uses a contact-sales flow — no self-serve checkout.

## Plan keys in the API

Entitlement responses reference plans by their key strings:

```json
{
  "product_type": "build_monthly",
  "status": "active"
}
```

Client applications should treat plan behavior as configuration rather than hard-coded assumptions.

## Billable receipt definition

A receipt is billable when **all three conditions hold**:

1. authorization record exists
2. transaction record exists
3. signed receipt is issued

Quote attempts and blocked authorizations are never billable.

## Overage pricing

Paid plans include a monthly receipt quota. Additional receipts above the quota are billed per receipt:

| Plan | Overage per receipt |
|---|---|
| Build | $0.02 |
| Trust | $0.015 |
| Govern | $0.01 |

## Feature flags by plan

| Feature | Sandbox | Build | Trust | Govern |
|---|---|---|---|---|
| Basic verification | Yes | Yes | Yes | Yes |
| Signed receipts | No | Yes | Yes | Yes |
| Basic policies | No | Yes | Yes | Yes |
| Audit lineage | No | No | Yes | Yes |
| Webhooks | No | No | Yes | Yes |
| Advanced policy controls | No | No | Yes | Yes |
| Approval workflows | No | No | No | Yes |
| Exports | No | No | No | Yes |
| Governance controls | No | No | No | Yes |

## Related

- [Authentication](./authentication.md)
- [Sandbox and mock server](./sandbox-and-mock-server.md)
- [Errors and idempotency](./errors-and-idempotency.md)
