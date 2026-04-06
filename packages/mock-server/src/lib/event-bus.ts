/**
 * In-memory event bus.
 * Emitted events are stored and queryable via GET /v1/events.
 * No real webhook delivery — events are log-only.
 */

import { generateId } from "./id-generator.js";

interface EventRecord {
  id: string;
  object: "event";
  event_type: string;
  event_version: string;
  api_version: string;
  occurred_at: string;
  environment: "sandbox";
  livemode: false;
  resource_type: string;
  resource_id: string;
  data: unknown;
  provenance: unknown | null;
  request_context: unknown | null;
}

const events: EventRecord[] = [];

export function emitEvent(
  event_type: string,
  resource_type: string,
  resource_id: string,
  data: unknown,
  provenance: unknown = null,
  request_context: unknown = null
): EventRecord {
  const event: EventRecord = {
    id: generateId("evt"),
    object: "event",
    event_type,
    event_version: "1.0.0",
    api_version: "2025-01-01",
    occurred_at: new Date().toISOString(),
    environment: "sandbox",
    livemode: false,
    resource_type,
    resource_id,
    data,
    provenance,
    request_context,
  };
  events.push(event);
  return event;
}

export function listEvents(params?: {
  event_type?: string;
  limit?: number;
  starting_after?: string;
}): { data: EventRecord[]; has_more: boolean; next_cursor: string | null } {
  const limit = Math.min(params?.limit ?? 20, 100);
  let filtered = [...events].reverse(); // newest first

  if (params?.event_type) {
    filtered = filtered.filter((e) => e.event_type === params.event_type);
  }

  if (params?.starting_after) {
    const idx = filtered.findIndex((e) => e.id === params.starting_after);
    if (idx !== -1) filtered = filtered.slice(idx + 1);
  }

  const page = filtered.slice(0, limit);
  const has_more = filtered.length > limit;
  return {
    data: page,
    has_more,
    next_cursor: has_more ? page[page.length - 1]?.id ?? null : null,
  };
}

export function getEvent(eventId: string): EventRecord | undefined {
  return events.find((e) => e.id === eventId);
}
