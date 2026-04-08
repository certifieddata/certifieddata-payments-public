"""Events resource."""

from typing import Any, Optional
from .._http import HttpClient


class EventsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, event_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/events/{event_id}")

    def list(
        self,
        *,
        event_type: Optional[str] = None,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            "/v1/events",
            params={
                "event_type": event_type,
                "limit": limit,
                "starting_after": starting_after,
            },
        )
