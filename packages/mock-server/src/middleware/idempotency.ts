import type { Request, Response, NextFunction } from "express";
import {
  getIdempotencyRecord,
  setIdempotencyRecord,
} from "../lib/idempotency-store.js";

/**
 * Middleware that implements idempotency semantics for POST/PATCH endpoints.
 * - Same key + same payload → replay cached response
 * - Same key + different payload → 409 conflict
 */
export function withIdempotency(req: Request, res: Response, next: NextFunction): void {
  const key = req.headers["idempotency-key"] as string | undefined;
  if (!key) {
    next();
    return;
  }

  const existing = getIdempotencyRecord(key);
  if (existing) {
    const incomingBody = JSON.stringify(req.body ?? {});
    const cachedBody = JSON.stringify((existing.body as { _req_body?: unknown })?.["_req_body"] ?? {});
    if (incomingBody !== cachedBody) {
      res.status(409).json({
        error: {
          code: "idempotency.key_reused_with_different_payload",
          http_status: 409,
          message: "The idempotency key was already used with a different request payload.",
          retryable: false,
        },
      });
      return;
    }
    // Replay cached response (strip internal _req_body field)
    const { _req_body: _, ...responseBody } = existing.body as Record<string, unknown>;
    res.status(existing.status).json(responseBody);
    return;
  }

  // Intercept the json() call to cache the response
  const originalJson = res.json.bind(res);
  res.json = function (body: unknown) {
    setIdempotencyRecord(key, res.statusCode, {
      ...(body as object),
      _req_body: req.body ?? {},
    });
    return originalJson(body);
  };

  next();
}
