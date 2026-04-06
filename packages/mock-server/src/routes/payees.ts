import { type Router as ExpressRouter, Router } from "express";
import { generateId } from "../lib/id-generator.js";
import { saveResource, getResource, listResources, updateResource } from "../lib/store.js";
import { emitEvent } from "../lib/event-bus.js";
import { withIdempotency } from "../middleware/idempotency.js";

const router: ExpressRouter = Router();

router.post("/", withIdempotency, (req, res) => {
  const now = new Date().toISOString();
  const payee = saveResource("payee", {
    id: generateId("py"),
    object: "payee",
    entity_type: req.body.entity_type ?? "company",
    legal_name: req.body.legal_name ?? null,
    email: req.body.email ?? null,
    status: "active",
    kyc_status: "pending",
    default_payout_method: req.body.default_payout_method ?? null,
    metadata: req.body.metadata ?? null,
    created_at: now,
    updated_at: now,
    livemode: false,
  });
  emitEvent("payee.created", "payee", payee.id, payee);
  res.status(201).json(payee);
});

router.get("/", (req, res) => {
  const result = listResources("payee", {
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
  });
  res.json(result);
});

router.get("/:id", (req, res) => {
  const payee = getResource("payee", req.params.id);
  if (!payee) return res.status(404).json(notFound("payee", req.params.id));
  res.json(payee);
});

router.patch("/:id", withIdempotency, (req, res) => {
  const updated = updateResource("payee", req.params.id, req.body);
  if (!updated) return res.status(404).json(notFound("payee", req.params.id));
  emitEvent("payee.updated", "payee", req.params.id, updated);
  res.json(updated);
});

// Aliases
router.post("/:payeeId/aliases", withIdempotency, (req, res) => {
  const payee = getResource("payee", req.params.payeeId);
  if (!payee) return res.status(404).json(notFound("payee", req.params.payeeId));
  const now = new Date().toISOString();
  const alias = saveResource("payee_alias", {
    id: generateId("pya"),
    object: "payee_alias",
    payee_id: req.params.payeeId,
    external_system: req.body.external_system,
    external_ref: req.body.external_ref,
    created_at: now,
  });
  emitEvent("payee.alias.created", "payee_alias", alias.id, alias);
  res.status(201).json(alias);
});

router.get("/:payeeId/aliases", (req, res) => {
  const result = listResources("payee_alias", {
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
    filter: (a: { payee_id: string }) => a.payee_id === req.params.payeeId,
  });
  res.json(result);
});

// Payout destinations
router.post("/:payeeId/payout-destinations", withIdempotency, (req, res) => {
  const payee = getResource("payee", req.params.payeeId);
  if (!payee) return res.status(404).json(notFound("payee", req.params.payeeId));
  const now = new Date().toISOString();
  const dest = saveResource("payout_destination", {
    id: generateId("pydst"),
    object: "payout_destination",
    payee_id: req.params.payeeId,
    rail_type: req.body.rail_type,
    status: "pending_verification",
    is_default: req.body.is_default ?? false,
    version: 1,
    processor_ref: req.body.processor_ref ?? null,
    metadata: req.body.metadata ?? null,
    created_at: now,
    updated_at: now,
  });
  emitEvent("payout_destination.created", "payout_destination", dest.id, dest);
  res.status(201).json(dest);
});

router.get("/:payeeId/payout-destinations", (req, res) => {
  const result = listResources("payout_destination", {
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
    filter: (d: { payee_id: string }) => d.payee_id === req.params.payeeId,
  });
  res.json(result);
});

function notFound(resource: string, id: string) {
  return {
    error: {
      code: `${resource}.not_found`,
      http_status: 404,
      message: `${resource} ${id} not found.`,
    },
  };
}

export default router;
