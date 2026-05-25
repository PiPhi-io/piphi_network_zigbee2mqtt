from __future__ import annotations

from piphi_network_zigbee2mqtt.routes.config import _runtime_config_payloads


class RuntimeConfigLike:
    def model_dump(self, *, mode: str):
        assert mode == "python"
        return {
            "id": "bridge-config",
            "config_id": "bridge-config",
            "container_id": "runtime-container",
            "serial_port": "/dev/ttyUSB0",
            "mqtt_server": "mqtt://user:pass@127.0.0.1:1883",
            "mqtt_base_topic": "zigbee2mqtt",
            "data_path": "/app/data",
        }


def test_runtime_config_payloads_normalizes_runtime_config_models() -> None:
    raw = {"id": "raw-config", "serial_port": "/dev/ttyUSB1"}

    payloads = _runtime_config_payloads([RuntimeConfigLike(), raw])

    assert payloads[0]["id"] == "bridge-config"
    assert payloads[0]["mqtt_server"] == "mqtt://user:pass@127.0.0.1:1883"
    assert payloads[1] is raw
