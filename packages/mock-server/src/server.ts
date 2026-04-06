import express from "express";
import payeesRouter from "./routes/payees.js";
import transactionsRouter from "./routes/transactions.js";
import paymentIntentsRouter from "./routes/payment-intents.js";
import settlementsRouter from "./routes/settlements.js";
import refundsRouter from "./routes/refunds.js";
import eventsRouter from "./routes/events.js";

const CAPABILITIES = {
  version: "1.0.0",
  api_version: "2025-01-01",
  environments: ["sandbox"],
  resources: [
    "payee", "payee_alias", "payout_destination",
    "payment_intent", "transaction", "settlement", "refund", "event",
  ],
  payment_rails: ["stripe"],
  event_types: [
    "payee.created", "payee.updated", "payee.alias.created",
    "payout_destination.created",
    "payment_intent.created", "payment_intent.confirmed", "payment_intent.canceled",
    "transaction.created", "transaction.captured", "transaction.canceled", "transaction.links_attached",
    "settlement.created", "settlement.submitted", "settlement.succeeded", "settlement.failed",
    "refund.created",
  ],
  provenance_link_types: [
    "artifact_id", "certificate_id", "decision_id", "dataset_id",
    "model_id", "output_id", "receipt_hash", "external_reference", "provenance_metadata",
  ],
  idempotency: { supported: true, header_name: "Idempotency-Key" },
  webhooks: {
    supported: false,
    note: "Mock server does not deliver webhooks. Events are queryable via GET /v1/events.",
  },
  pagination: { default_limit: 20, max_limit: 100, cursor_based: true },
  sdk_support: { typescript: true, python: true, mock_server: true },
  mock_server: {
    livemode: false,
    environment: "sandbox",
    id_scheme: "counter-based (e.g. py_test_0001)",
    note: "Mock server simulates sandbox behavior only. IDs are deterministic and session-scoped.",
  },
};

export function createApp() {
  const app = express();
  app.use(express.json());

  // Meta endpoints
  app.get("/v1/health", (_req, res) => {
    res.json({
      status: "ok",
      mode: "mock",
      livemode: false,
      api_version: "2025-01-01",
      timestamp: new Date().toISOString(),
    });
  });

  app.get("/v1/capabilities", (_req, res) => {
    res.json(CAPABILITIES);
  });

  app.get("/v1/version", (_req, res) => {
    res.json({
      api_version: "2025-01-01",
      schema_version: "1.0.0",
      event_schema_version: "1.0.0",
      openapi_version: "1.0.0",
      asyncapi_version: "1.0.0",
      sdk_versions: { typescript: "0.1.0", python: "0.1.0" },
      mock_server_version: "0.1.0",
      generated_at: "2026-04-06T00:00:00Z",
    });
  });

  // Resource routes
  app.use("/v1/payees", payeesRouter);
  app.use("/v1/payment-intents", paymentIntentsRouter);
  app.use("/v1/transactions", transactionsRouter);
  app.use("/v1/settlements", settlementsRouter);
  app.use("/v1/refunds", refundsRouter);
  app.use("/v1/events", eventsRouter);

  // 404 handler
  app.use((_req, res) => {
    res.status(404).json({
      error: { code: "not_found", http_status: 404, message: "The requested endpoint does not exist." },
    });
  });

  return app;
}
