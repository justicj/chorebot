"""Fetch calendar entries from Sonarr and Radarr APIs."""

import os
from datetime import date, timedelta

import httpx

SONARR_URL = os.environ.get("SONARR_URL")
RADARR_URL = os.environ.get("RADARR_URL")
SONARR_API_KEY = os.environ["SONARR_API_KEY"]
RADARR_API_KEY = os.environ["RADARR_API_KEY"]


async def _get(client: httpx.AsyncClient, base_url: str, api_key: str, start: date, end: date, extra_params: dict | None = None) -> list[dict]:
    url = f"{base_url}/api/v3/calendar"
    params = {"start": start.isoformat(), "end": end.isoformat(), **(extra_params or {})}
    headers = {"X-Api-Key": api_key}
    resp = await client.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


async def fetch_calendar(start: date, end: date) -> dict:
    """Return {"sonarr": [...], "radarr": [...]} for the given date range."""
    async with httpx.AsyncClient() as client:
        sonarr_task = _get(client, SONARR_URL, SONARR_API_KEY, start, end, {"includeSeries": "true"})
        radarr_task = _get(client, RADARR_URL, RADARR_API_KEY, start, end)
        import asyncio
        sonarr, radarr = await asyncio.gather(sonarr_task, radarr_task, return_exceptions=True)

    return {
        "sonarr": sonarr if not isinstance(sonarr, BaseException) else [],
        "radarr": radarr if not isinstance(radarr, BaseException) else [],
        "errors": {
            **({"sonarr": str(sonarr)} if isinstance(sonarr, BaseException) else {}),
            **({"radarr": str(radarr)} if isinstance(radarr, BaseException) else {}),
        },
    }
