from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from piphi_runtime_kit_python import build_event_ingest_response

from ..state import append_runtime_event, commands, registry

router = APIRouter(tags=["commands"])


@router.post("/command")
async def command(payload: dict[str, Any]):
    command_name = str(payload.get("command") or payload.get("capability_id") or "").strip()
    if not command_name:
        raise HTTPException(status_code=400, detail="Missing command")
    if command_name not in commands:
        raise HTTPException(status_code=400, detail=f"Unsupported command: {command_name}")

    target = payload.get("target") if isinstance(payload.get("target"), dict) else {}
    device_id = str(payload.get("device_id") or target.get("device_id") or "demo-device")
    config_id = str(payload.get("config_id") or target.get("config_id") or device_id)
    requirements = payload.get("capability_requirements")
    requested_capabilities = [
        str(item).strip()
        for item in ([payload.get("capability")] + (requirements if isinstance(requirements, list) else []))
        if str(item or "").strip()
    ]
    unsupported_capability = next(
        (
            capability
            for capability in requested_capabilities
            if capability not in {"device.refresh", f"action.{command_name}"}
        ),
        None,
    )
    if unsupported_capability:
        raise HTTPException(
            status_code=400,
            detail={
                "ok": False,
                "error": "unsupported_capability",
                "message": f"This runtime does not support capability {unsupported_capability}",
            },
        )
    entry = registry.get(config_id) or {
        "device_id": device_id,
        "config_id": config_id,
    }
    event = append_runtime_event(
        "runtime.command.received",
        entry,
        {
            "command": command_name,
            "device_id": device_id,
            "entity_id": payload.get("entity_id"),
            "args": payload.get("params") or payload.get("args") or {},
            "target": target,
        },
    )
    response = build_event_ingest_response(event)
    response_payload = response.model_dump() if hasattr(response, "model_dump") else dict(response)
    return {
        **response_payload,
        "ok": True,
        "command": command_name,
        "contract_version": payload.get("contract_version"),
        "device_id": device_id,
        "config_id": config_id,
        "target": target,
        "params": payload.get("params") or payload.get("args") or {},
    }
