# Events

Events represent things that happen in the CertifiedData Agent Commerce system. They are queryable via `GET /v1/events` and also delivered via webhooks.

## Machine-readable references

- Schema: [schemas/resources/event.schema.json](../schemas/resources/event.schema.json)
- Event types: [schemas/enums/event-types.json](../schemas/enums/event-types.json)
- Event-resource map: [schemas/event-resource-map.json](../schemas/event-resource-map.json)
- AsyncAPI contract: [asyncapi/certifieddata-agent-commerce-events-v1.asyncapi.yaml](../asyncapi/certifieddata-agent-commerce-events-v1.asyncapi.yaml)
- Example: [examples/json/event.transaction.captured.json](../examples/json/event.transaction.captured.json)

## Event envelope

Every event includes:

| Field | Description |
|-------|-------------|
| `id` | Event ID (`evt_` prefix) |
| `event_type` | E.g. `transaction.captured` |
| `event_version` | Schema version of the event payload |
| `api_version` | API version at time of event |
| `occurred_at` | RFC 3339 UTC timestamp |
| `environment` | `sandbox` or `live` |
| `livemode` | Boolean |
| `resource_type` | Resource that triggered the event |
| `resource_id` | ID of the affected resource |
| `data` | Snapshot of the resource at event time |
| `provenance` | Provenance link set (nullable) |
| `request_context` | Optional request context for reconciliation |

## Event types

All supported event types: [schemas/enums/event-types.json](../schemas/enums/event-types.json)

Key event types:

| Event type | Trigger |
|------------|---------|
| `payee.created` | `POST /v1/payees` |
| `transaction.created` | `POST /v1/transactions` |
| `transaction.links_attached` | `POST /v1/transactions/{id}/attach-links` |
| `transaction.captured` | `POST /v1/transactions/{id}/capture` |
| `settlement.submitted` | `POST /v1/settlements/{id}/submit` |
| `settlement.succeeded` | Settlement processing completes |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/events` | List events (supports `event_type` filter) |
| `GET` | `/v1/events/{id}` | Retrieve a specific event |

## TypeScript SDK

```typescript
const events = await client.events.list({ event_type: "transaction.captured", limit: 20 });
const event = await client.events.get("evt_...");
```

## Webhooks

Events are delivered as webhooks when you configure a webhook endpoint. See [webhooks.md](webhooks.md) for signature verification.
