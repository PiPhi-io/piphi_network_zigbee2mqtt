from __future__ import annotations

import os

INTEGRATION_ID = "piphi.service.zigbee2mqtt-sidecar"
INTEGRATION_NAME = "Zigbee2MQTT Sidecar"
INTEGRATION_VERSION = "0.1.5"
PROJECT_KIND = "sidecar"
PROJECT_PRESET = "platform-service"
PROJECT_DOMAIN = "sidecar-service"
DEFAULT_PORT = 8720
DEFAULT_ZIGBEE2MQTT_CONTAINER = "piphi-zigbee2mqtt"
DEFAULT_ZIGBEE2MQTT_IMAGE = "ghcr.io/koenkk/zigbee2mqtt:latest"
DEFAULT_ZIGBEE2MQTT_PM2_NAME = "piphi-zigbee2mqtt"
DEFAULT_ZIGBEE2MQTT_FRONTEND_PORT = 8080
DEFAULT_ZIGBEE2MQTT_CONTAINER_DATA_PATH = "/app/data"


def runtime_port() -> int:
    raw_port = os.getenv("PORT", str(DEFAULT_PORT))
    try:
        return int(raw_port)
    except ValueError:
        return DEFAULT_PORT
