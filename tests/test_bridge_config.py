from __future__ import annotations

from piphi_network_zigbee2mqtt.adapter_detector import infer_adapter_hint
from piphi_network_zigbee2mqtt.bridge_models import MqttSettings, SerialSettings, Zigbee2MqttBridgeConfig
from piphi_network_zigbee2mqtt.config_renderer import render_zigbee2mqtt_config


def test_infer_adapter_hint_for_common_coordinators() -> None:
    assert infer_adapter_hint("Sonoff ZBDongle-P CC2652")[0] == "zstack"
    assert infer_adapter_hint("Nabu Casa SkyConnect EFR32")[0] == "ember"
    assert infer_adapter_hint("ConBee II Dresden Elektronik")[0] == "deconz"


def test_render_zigbee2mqtt_configuration_yaml() -> None:
    rendered = render_zigbee2mqtt_config(
        Zigbee2MqttBridgeConfig(
            mqtt=MqttSettings(
                server="mqtt://broker.local:1883",
                base_topic="zigbee2mqtt",
                user="z2m",
                password="secret",
            ),
            serial=SerialSettings(
                port="/dev/ttyZigbee",
                adapter="ember",
            ),
            frontend_port=8099,
            availability=True,
        )
    )

    assert 'server: "mqtt://broker.local:1883"' in rendered.yaml
    assert 'base_topic: "zigbee2mqtt"' in rendered.yaml
    assert 'port: "/dev/ttyZigbee"' in rendered.yaml
    assert 'adapter: "ember"' in rendered.yaml
    assert "availability: true" in rendered.yaml
    assert "frontend:" in rendered.yaml
