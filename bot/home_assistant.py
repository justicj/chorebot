"""Interact with Home Assistant via its REST API."""

import os

import httpx

HA_URL = os.environ["HOME_ASSISTANT_URL"]
HA_TOKEN = os.environ["HOME_ASSISTANT_API_KEY"]

_HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# Map friendly names (used in Discord commands) to entity IDs
LIGHTS: dict[str, str] = {
    "living room": "light.living_room_light",
}

# Display names shown in bot responses (keyed the same as LIGHTS)
LIGHTS_FRIENDLY: dict[str, str] = {
    "living room": "Living Room Light",
}


async def set_light(entity_id: str, turn_on: bool) -> dict:
    """Call the light turn_on or turn_off service. Returns the HA response."""
    service = "turn_on" if turn_on else "turn_off"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{HA_URL}/api/services/light/{service}",
            headers=_HEADERS,
            json={"entity_id": entity_id},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


async def get_light_state(entity_id: str) -> dict:
    """Return the current state object for a light entity."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{HA_URL}/api/states/{entity_id}",
            headers=_HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
