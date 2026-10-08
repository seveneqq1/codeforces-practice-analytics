"""Small, typed wrapper around the public Codeforces API."""

from __future__ import annotations

from typing import Any

import httpx


class CodeforcesAPIError(RuntimeError):
    """Raised when Codeforces returns an error or cannot be reached."""


class CodeforcesAPI:
    BASE_URL = "https://codeforces.com/api"

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    def _get(self, method: str, **params: Any) -> Any:
        try:
            response = httpx.get(
                f"{self.BASE_URL}/{method}",
                params=params,
                timeout=self.timeout,
                follow_redirects=True,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise CodeforcesAPIError(f"Could not reach Codeforces: {exc}") from exc

        if payload.get("status") != "OK":
            message = payload.get("comment", "Unknown Codeforces API error")
            raise CodeforcesAPIError(message)
        return payload["result"]

    def user(self, handle: str) -> dict[str, Any]:
        users = self._get("user.info", handles=handle)
        if not users:
            raise CodeforcesAPIError(f"User {handle!r} was not found")
        return users[0]

    def submissions(self, handle: str, count: int = 5000) -> list[dict[str, Any]]:
        return self._get("user.status", handle=handle, **{"from": 1, "count": count})

    def problemset(self) -> list[dict[str, Any]]:
        result = self._get("problemset.problems")
        return result["problems"]
