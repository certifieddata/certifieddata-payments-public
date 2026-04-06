import { Router } from "express";
import { generateId } from "../lib/id-generator.js";
import { saveResource, getResource, listResources, updateResource } from "../lib/store.js";
import { emitEvent } from "../lib/event-bus.js";
import { withIdempotency } from "../middleware/idempotency.js";

const router = Router();

const IMMUTABLE_AFTER = new Set(["captured", "succeeded", "failed", "canceled"]);

router.post("/", withIdempotency, (req, res) => {
  const now = new Date().toISOString();
  const tx = saveResource("transaction", {
    id: generateId("tx"),
    object: "transaction",
    payment_intent_id: req.body.payment_intent_id ?? null,
    payee_id: req.body.payee_id ?? null,
    customer_id: req.body.customer_id ?? null,
    amount: req.body.amount,
    currency: req.body.currency,
    rail: req.body.rail,
    status: "created",
    description: req.body.description ?? null,
    provenance: null,
    receipt: null,
    metadata: req.body.metadata ?? null,
    created_at: now,
    updated_at: now,
    livemode: false,
  });
  emitEvent("transaction.created", "transaction", tx.id, tx);
  res.status(201).json(tx);
});

router.get("/", (req, res) => {
  const result = listResources("transaction", {
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
  });
  res.json(result);
});

router.get("/:id", (req, res) => {
  const tx = getResource("transaction", req.params.id);
  if (!tx) return res.status(404).json(notFound("transaction", req.params.id));
  res.json(tx);
});

router.post("/:id/attach-links", withIdempotency, (req, res) => {
  const tx = getResource<{ status: string; provenance: unknown }>("transaction", req.params.id);
  if (!tx) return res.status(404).json(notFound("transaction", req.params.id));

  if (IMMUTABLE_AFTER.has(tx.status)) {
    return res.status(409).json({
      error: {
        code: "provenance.immutable_after_capture",
        http_status: 409,
        message: "Provenance links can no longer be modified after capture.",
        retryable: false,
      },
    });
  }

  const updated = updateResource("transaction", req.params.id, { provenance: req.body });
  emitEvent("transaction.links_attached", "transaction", req.params.id, updated);
  res.json(updated);
});

router.post("/:id/capture", withIdempotency, (req, res) => {
  const tx = getResource<{ status: string }>("transaction", req.params.id);
  if (!tx) return res.status(404).json(notFound("transaction", req.params.id));

  if (!["created", "submitted"].includes(tx.status)) {
    return res.status(409).json({
      error: {
        code: "state.invalid_transition",
        http_status: 409,
        message: `Cannot capture a transaction with status '${tx.status}'.`,
        retryable: false,
      },
    });
  }

  const now = new Date().toISOString();
  const receipt = {
    id: generateId("rcpt"),
    schema_version: "payment_receipt.v1",
    hash: `sha256:mock_${Date.now().toString(16)}`,
    created_at: now,
  };

  const updated = updateResource("transaction", req.params.id, {
    status: "captured",
    receipt,
  });
  emitEvent("transaction.captured", "transaction", req.params.id, updated);
  res.json(updated);
});

router.post("/:id/cancel", withIdempotency, (req, res) => {
  const tx = getResource<{ status: string }>("transaction", req.params.id);
  if (!tx) return res.status(404).json(notFound("transaction", req.params.id));

  if (IMMUTABLE_AFTER.has(tx.status)) {
    return res.status(409).json({
      error: {
        code: "state.invalid_transition",
        http_status: 409,
        message: `Cannot cancel a transaction with status '${tx.status}'.`,
        retryable: false,
      },
    });
  }

  const updated = updateResource("transaction", req.params.id, { status: "canceled" });
  emitEvent("transaction.canceled", "transaction", req.params.id, updated);
  res.json(updated);
});

function notFound(resource: string, id: string) {
  return {
    error: { code: `${resource}.not_found`, http_status: 404, message: `${resource} ${id} not found.` },
  };
}

export default router;
