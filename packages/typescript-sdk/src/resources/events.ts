import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";
import type { PaginationEnvelope, ListParams } from "../types/common.js";
import type { Event } from "../types/resources.js";

export class EventsResource {
  constructor(private readonly config: CDPClientConfig) {}

  async get(eventId: string): Promise<Event> {
    return makeRequest(this.config, "GET", `/v1/events/${eventId}`);
  }

  async list(params?: ListParams & { event_type?: string }): Promise<PaginationEnvelope<Event>> {
    return makeRequest(this.config, "GET", "/v1/events", {
      query: {
        limit: params?.limit,
        starting_after: params?.starting_after,
        event_type: params?.event_type,
      },
    });
  }
}
