import { type Router as ExpressRouter, Router } from "express";
import { generateId } from "../lib/id-generator.js";
import { saveResource, getResource, listResources, updateResource } from "../lib/store.js";
import { emitEvent } from "../lib/event-bus.js";
import { withIdempotency } from "../middleware/idempotency.js";

const router: ExpressRouter = Router();

router.post("/", withIdempotency, (req, res) => {
  const now = new Date().toISOString();
  const settlement = saveResource("settlement", {
    id: generateId("stl"),
    object: "settlement",
    payee_id: req.body.payee_id,
    destination_id: req.body.destination_id ?? null,
    amount: req.body.amount,
    currency: req.body.currency,
    status: "draft",
    transaction_ids: req.body.transaction_ids ?? [],
    provenance: null,
    metadata: req.body.metadata ?? null,
    submitted_at: null,
    succeeded_at: null,
    created_at: now,
    updated_at: now,
    livemode: false,
  });
  emitEvent("settlement.created", "settlement", settlement.id, settlement);
  res.status(201).json(settlement);
});

router.get("/", (req, res) => {
  const result = listResources("settlement", {
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
  });
  res.json(result);
});

router.get("/:id", (req, res) => {
  const settlement = getResource("settlement", req.params.id);
  if (!settlement) return res.status(404).json(notFound("settlement", req.params.id));
  res.json(settlement);
});

router.post("/:id/submit", withIdempotency, (req, res) => {
  const settlement = getResource<{ status: string }>("settlement", req.params.id);
  if (!settlement) return res.status(404).json(notFound("settlement", req.params.id));

  if (settlement.status !== "draft") {
    return res.status(409).json({
      error: {
        code: "state.invalid_transition",
        http_status: 409,
        message: `Cannot submit a settlement with status '${settlement.status}'.`,
        retryable: false,
      },
    });
  }

  const now = new Date().toISOString();
  const updated = updateResource("settlement", req.params.id, {
    status: "submitted",
    submitted_at: now,
  });
  emitEvent("settlement.submitted", "settlement", req.params.id, updated);

  // Simulate async processing — immediately succeed in mock
  setTimeout(() => {
    const succeeded = updateResource("settlement", req.params.id, {
      status: "succeeded",
      succeeded_at: new Date().toISOString(),
    });
    emitEvent("settlement.succeeded", "settlement", req.params.id, succeeded);
  }, 100);

  res.json(updated);
});

router.post("/:id/cancel", withIdempotency, (req, res) => {
  const settlement = getResource<{ status: string }>("settlement", req.params.id);
  if (!settlement) return res.status(404).json(notFound("settlement", req.params.id));

  const cancelableStatuses = new Set(["draft"]);
  if (!cancelableStatuses.has(settlement.status)) {
    return res.status(409).json({
      error: {
        code: "state.invalid_transition",
        http_status: 409,
        message: `Cannot cancel a settlement with status '${settlement.status}'.`,
        retryable: false,
      },
    });
  }

  const updated = updateResource("settlement", req.params.id, { status: "canceled" });
  res.json(updated);
});

function notFound(resource: string, id: string) {
  return {
    error: { code: `${resource}.not_found`, http_status: 404, message: `${resource} ${id} not found.` },
  };
}

export default router;
