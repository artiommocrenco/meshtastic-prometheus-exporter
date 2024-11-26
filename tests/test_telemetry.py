import meshtastic_prometheus_exporter.__main__ as exporter
import json
from pytest_mock import MockerFixture


def mocked_get_decoded_node_metadata_from_redis(redis, node: float, metadata: str):
    return "mocked"


def test_device_metrics_telemetry(mocker: MockerFixture):
    packet = '{"from": 123456789, "to": 987654321, "decoded": {"portnum": "TELEMETRY_APP", "telemetry": {"time": 1732550036, "deviceMetrics": {"batteryLevel": 101, "voltage": 4.122, "channelUtilization": 0.0, "airUtilTx": 0.15486111, "uptimeSeconds": 2027}}}, "id": 3259852062, "rxTime": 1732550036, "hopLimit": 3, "priority": "BACKGROUND",  "fromId": null, "toId": "^all"}'

    packet_decoded = json.loads(packet)

    mocker.patch(
        "meshtastic_prometheus_exporter.__main__.get_decoded_node_metadata_from_redis",
        new=mocked_get_decoded_node_metadata_from_redis,
    )

    mock_set_battery_level = mocker.patch.object(
        exporter.meshtastic_telemetry_device_battery_level_percent, "set"
    )
    mock_set_voltage = mocker.patch.object(
        exporter.meshtastic_telemetry_device_voltage_volts, "set"
    )
    mock_set_channel_utilization = mocker.patch.object(
        exporter.meshtastic_telemetry_device_channel_utilization_percent, "set"
    )
    mock_set_air_util = mocker.patch.object(
        exporter.meshtastic_telemetry_device_air_util_tx_percent, "set"
    )
    mock_add_packets_total = mocker.patch.object(
        exporter.meshtastic_mesh_packets_total, "add"
    )

    mocker.patch("meshtastic_prometheus_exporter.__main__.redis")
    exporter.on_meshtastic_mesh_packet(packet_decoded)

    mock_set_battery_level.assert_called_once_with(
        101,
        attributes={
            "source": packet_decoded["from"],
            "source_long_name": "mocked",
            "source_short_name": "mocked",
        },
    )
    mock_set_voltage.assert_called_once_with(
        4.122,
        attributes={
            "source": packet_decoded["from"],
            "source_long_name": "mocked",
            "source_short_name": "mocked",
        },
    )
    mock_set_channel_utilization.assert_called_once_with(
        0.0,
        attributes={
            "source": packet_decoded["from"],
            "source_long_name": "mocked",
            "source_short_name": "mocked",
        },
    )
    mock_set_air_util.assert_called_once_with(
        0.15486111,
        attributes={
            "source": packet_decoded["from"],
            "source_long_name": "mocked",
            "source_short_name": "mocked",
        },
    )
    mock_add_packets_total.assert_called_once()
