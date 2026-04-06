import { Router } from "express";
import { generateId } from "../lib/id-generator.js";
import { saveResource, getResource, listResources } from "../lib/store.js";
import { emitEvent } from "../lib/event-bus.js";
import { withIdempotency } from "../middleware/idempotency.js";

const router = Router();

router.post("/", withIdempotency, (req, res) => {
  const now = new Date().toISOString();
  const refund = saveResource("refund", {
    id: generateId("rf"),
    object: "refund",
    transaction_id: req.body.transaction_id,
    amount: req.body.amount,
    currency: req.body.currency ?? "usd",
    status: "created",
    reason: req.body.reason ?? null,
    metadata: req.body.metadata ?? null,
    succeeded_at: null,
    created_at: now,
    updated_at: now,
    livemode: false,
  });
  emitEvent("refund.created", "refund", refund.id, refund);
  res.status(201).json(refund);
});

router.get("/", (req, res) => {
  const result = listResources("refund", {
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
  });
  res.json(result);
});

router.get("/:id", (req, res) => {
  const refund = getResource("refund", req.params.id);
  if (!refund) return res.status(404).json(notFound("refund", req.params.id));
  res.json(refund);
});

function notFound(resource: string, id: string) {
  return {
    error: { code: `${resource}.not_found`, http_status: 404, message: `${resource} ${id} not found.` },
  };
}

export default router;
