from __future__ import annotations

import httpx
import pytest

from piphi_network_zigbee2mqtt import state
from piphi_network_zigbee2mqtt.main import app


@pytest.mark.anyio
async def test_command_replays_key_without_repeating_runtime_effect() -> None:
    state.registry.recent_events.clear()
    headers = {"X-PiPhi-Idempotency-Key": "zigbee2mqtt-action-idempotency-1"}
    payload = {
        "command": "refresh",
        "config_id": "bridge-1",
        "device_id": "bridge-1",
    }
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        first = await client.post("/command", json=payload, headers=headers)
        replay = await client.post("/command", json=payload, headers=headers)

    command_events = [
        event
        for event in state.registry.recent_events
        if event.get("event_type") == "runtime.command.received"
    ]
    assert first.status_code == 200
    assert replay.status_code == 200
    assert first.json()["replayed"] is False
    assert replay.json()["replayed"] is True
    assert len(command_events) == 1
