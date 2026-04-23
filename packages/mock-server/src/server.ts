import express, { type Express } from "express";
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
    "artifact_id", "certificate_id", "decision_record_id", "dataset_id",
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

// Tiny per-IP token bucket so accidental CI loops or open-internet exposure
// cannot trivially exhaust the host. 60 requests / minute / IP.
const RATE_LIMIT_MAX = 60;
const RATE_LIMIT_WINDOW_MS = 60_000;
const _bucket = new Map<string, { count: number; reset: number }>();

function rateLimit(req: express.Request, res: express.Response, next: express.NextFunction) {
  const ip = req.ip || "unknown";
  const now = Date.now();
  const entry = _bucket.get(ip);
  if (!entry || entry.reset < now) {
    _bucket.set(ip, { count: 1, reset: now + RATE_LIMIT_WINDOW_MS });
    return next();
  }
  entry.count += 1;
  if (entry.count > RATE_LIMIT_MAX) {
    res.setHeader("Retry-After", Math.ceil((entry.reset - now) / 1000).toString());
    return res.status(429).json({
      error: { code: "rate_limited", http_status: 429, message: "Mock server rate limit exceeded." },
    });
  }
  next();
}

// Optional auth gate. The mock has historically been authless to make local
// development frictionless, but operators occasionally ship it on an open port
// during demos. Setting MOCK_REQUIRE_AUTH=true requires Bearer cdp_test_*.
function optionalAuth(req: express.Request, res: express.Response, next: express.NextFunction) {
  if (process.env.MOCK_REQUIRE_AUTH !== "true") return next();
  const auth = (req.headers.authorization || "").trim();
  const [scheme, token] = auth.split(/\s+/);
  if (scheme !== "Bearer" || !token || !token.startsWith("cdp_test_")) {
    return res.status(401).json({
      error: { code: "unauthorized", http_status: 401, message: "Bearer cdp_test_* token required." },
    });
  }
  next();
}

export function createApp(): Express {
  const app = express();

  // If the operator forgot to set MOCK_REQUIRE_AUTH but is running in a
  // production-shaped environment, refuse to start. This is the cheapest way
  // to stop the "mock-as-prod-API" footgun.
  if (process.env.NODE_ENV === "production" && process.env.MOCK_REQUIRE_AUTH !== "true") {
    throw new Error(
      "Refusing to start: NODE_ENV=production but MOCK_REQUIRE_AUTH is not 'true'. " +
        "The mock server has no authentication by design. Set MOCK_REQUIRE_AUTH=true " +
        "to enable a Bearer cdp_test_* gate, or unset NODE_ENV for local development.",
    );
  }

  app.use(express.json({ limit: "1mb" }));
  app.use(rateLimit);
  app.use(optionalAuth);

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
