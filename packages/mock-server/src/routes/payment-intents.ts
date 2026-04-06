import { type Router as ExpressRouter, Router } from "express";
import { generateId } from "../lib/id-generator.js";
import { saveResource, getResource, listResources, updateResource } from "../lib/store.js";
import { emitEvent } from "../lib/event-bus.js";
import { withIdempotency } from "../middleware/idempotency.js";

const router: ExpressRouter = Router();

router.post("/", withIdempotency, (req, res) => {
  const now = new Date().toISOString();
  const pi = saveResource("payment_intent", {
    id: generateId("pi"),
    object: "payment_intent",
    customer_id: req.body.customer_id ?? null,
    payee_id: req.body.payee_id ?? null,
    invoice_id: req.body.invoice_id ?? null,
    amount: req.body.amount,
    currency: req.body.currency,
    rail: req.body.rail,
    status: "created",
    description: req.body.description ?? null,
    transaction_id: null,
    metadata: req.body.metadata ?? null,
    created_at: now,
    updated_at: now,
    livemode: false,
  });
  emitEvent("payment_intent.created", "payment_intent", pi.id, pi);
  res.status(201).json(pi);
});

router.get("/", (req, res) => {
  const result = listResources("payment_intent", {
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
  });
  res.json(result);
});

router.get("/:id", (req, res) => {
  const pi = getResource("payment_intent", req.params.id);
  if (!pi) return res.status(404).json(notFound("payment_intent", req.params.id));
  res.json(pi);
});

router.post("/:id/confirm", withIdempotency, (req, res) => {
  const pi = getResource<{ status: string }>("payment_intent", req.params.id);
  if (!pi) return res.status(404).json(notFound("payment_intent", req.params.id));

  if (pi.status !== "created") {
    return res.status(409).json({
      error: {
        code: "state.invalid_transition",
        http_status: 409,
        message: `Cannot confirm a payment intent with status '${pi.status}'.`,
        retryable: false,
      },
    });
  }

  const updated = updateResource("payment_intent", req.params.id, { status: "confirmed" });
  emitEvent("payment_intent.confirmed", "payment_intent", req.params.id, updated);
  res.json(updated);
});

router.post("/:id/cancel", withIdempotency, (req, res) => {
  const pi = getResource<{ status: string }>("payment_intent", req.params.id);
  if (!pi) return res.status(404).json(notFound("payment_intent", req.params.id));

  const terminalStates = new Set(["succeeded", "canceled", "failed"]);
  if (terminalStates.has(pi.status)) {
    return res.status(409).json({
      error: {
        code: "state.invalid_transition",
        http_status: 409,
        message: `Cannot cancel a payment intent with status '${pi.status}'.`,
        retryable: false,
      },
    });
  }

  const updated = updateResource("payment_intent", req.params.id, { status: "canceled" });
  emitEvent("payment_intent.canceled", "payment_intent", req.params.id, updated);
  res.json(updated);
});

function notFound(resource: string, id: string) {
  return {
    error: { code: `${resource}.not_found`, http_status: 404, message: `${resource} ${id} not found.` },
  };
}

export default router;
