import { Router } from "express";
import { listEvents, getEvent } from "../lib/event-bus.js";

const router = Router();

router.get("/", (req, res) => {
  const result = listEvents({
    event_type: req.query.event_type as string | undefined,
    limit: req.query.limit ? Number(req.query.limit) : undefined,
    starting_after: req.query.starting_after as string | undefined,
  });
  res.json(result);
});

router.get("/:id", (req, res) => {
  const event = getEvent(req.params.id);
  if (!event) {
    return res.status(404).json({
      error: { code: "event.not_found", http_status: 404, message: `Event ${req.params.id} not found.` },
    });
  }
  res.json(event);
});

export default router;
