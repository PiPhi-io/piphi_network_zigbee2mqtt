from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from piphi_network_zigbee2mqtt.bridge_models import MqttSettings
from piphi_network_zigbee2mqtt.zigbee2mqtt_mqtt import Zigbee2MqttMqttClient


class FakeMqttModule:
    instances: list["FakeMqttClient"] = []

    class Client:
        def __init__(self, client_id: str) -> None:
            self.client_id = client_id
            self.on_connect = None
            self.on_subscribe = None
            self.on_message = None
            self.subscriptions: list[str] = []
            self.published: list[tuple[str, str]] = []
            self.username: str | None = None
            self.password: str | None = None
            FakeMqttModule.instances.append(self)

        def username_pw_set(self, username: str, password: str | None) -> None:
            self.username = username
            self.password = password

        def connect(self, host: str, port: int, keepalive: int) -> None:
            self.host = host
            self.port = port
            self.keepalive = keepalive
            self.on_connect(self, None, None, 0)

        def loop_start(self) -> None:
            pass

        def loop_stop(self) -> None:
            pass

        def disconnect(self) -> None:
            pass

        def subscribe(self, topic: str) -> None:
            self.subscriptions.append(topic)
            if topic.endswith("/bridge/devices"):
                payload = [
                    {
                        "friendly_name": "Kitchen Plug",
                        "ieee_address": "0x00158d00018255df",
                        "type": "Router",
                        "supported": True,
                    }
                ]
                self.on_message(self, None, SimpleNamespace(payload=json.dumps(payload).encode("utf-8")))
            if self.on_subscribe:
                self.on_subscribe(self, None, 1, [0])

        def publish(self, topic: str, payload: str) -> None:
            self.published.append((topic, payload))
            request = json.loads(payload)
            response = {
                "status": "ok",
                "data": {"time": request["time"]},
                "transaction": request["transaction"],
            }
            self.on_message(self, None, SimpleNamespace(payload=json.dumps(response).encode("utf-8")))


FakeMqttClient = FakeMqttModule.Client


@pytest.mark.anyio
async def test_list_devices_reads_retained_bridge_devices_topic() -> None:
    FakeMqttModule.instances.clear()
    client = Zigbee2MqttMqttClient(
        mqtt=MqttSettings(server="mqtt://user:pass@broker.local:1884", base_topic="zigbee2mqtt"),
        mqtt_module=FakeMqttModule,
    )

    result = await client.list_devices()

    assert result.ok is True
    assert result.response_topic == "zigbee2mqtt/bridge/devices"
    assert result.request_topic is None
    assert result.devices[0].friendly_name == "Kitchen Plug"
    fake_client = FakeMqttModule.instances[0]
    assert fake_client.host == "broker.local"
    assert fake_client.port == 1884
    assert fake_client.username == "user"
    assert fake_client.password == "pass"
    assert fake_client.subscriptions == ["zigbee2mqtt/bridge/devices"]


@pytest.mark.anyio
async def test_permit_join_uses_request_response_transaction() -> None:
    FakeMqttModule.instances.clear()
    client = Zigbee2MqttMqttClient(
        mqtt=MqttSettings(server="mqtt://broker.local:1883", base_topic="zigbee2mqtt"),
        mqtt_module=FakeMqttModule,
    )

    result = await client.permit_join(value=True, time=45, device="coordinator")

    assert result.ok is True
    assert result.request_topic == "zigbee2mqtt/bridge/request/permit_join"
    assert result.response_topic == "zigbee2mqtt/bridge/response/permit_join"
    assert result.transaction is not None
    fake_client = FakeMqttModule.instances[0]
    topic, payload = fake_client.published[0]
    decoded = json.loads(payload)
    assert topic == "zigbee2mqtt/bridge/request/permit_join"
    assert decoded["time"] == 45
    assert decoded["device"] == "coordinator"
    assert decoded["transaction"] == result.transaction
