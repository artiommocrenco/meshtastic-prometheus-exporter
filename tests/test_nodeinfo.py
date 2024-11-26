import meshtastic_prometheus_exporter.__main__ as exporter
import json
from pytest_mock import MockerFixture


def mocked_get_decoded_node_metadata_from_redis(redis, node: float, metadata: str):
    return "mocked"


def test_nodeinfo(mocker: MockerFixture):
    packet = '{"from": 123456789, "to": 987654321, "decoded": {"portnum": "NODEINFO_APP", "bitfield": 0, "user": {"id": "!1fc44444", "longName": "namename", "shortName": "name", "macaddr": "CDIuwbaC", "hwModel": "TBEAM", "isLicensed": true}}, "id": 662811674, "rxTime": 1730000000, "rxSnr": 13.5, "hopLimit": 3, "rxRssi": -31, "hopStart": 3, "fromId": "!1fc44444", "toId": "^all"}'

    packet_decoded = json.loads(packet)

    mocker.patch("meshtastic_prometheus_exporter.__main__.redis")
    mocker.patch(
        "meshtastic_prometheus_exporter.__main__.get_decoded_node_metadata_from_redis",
        new=mocked_get_decoded_node_metadata_from_redis,
    )
    mock_set_last_heard_timestamp_seconds = mocker.patch.object(
        exporter.meshtastic_node_info_last_heard_timestamp_seconds, "set"
    )
    mock_add_packets_total = mocker.patch.object(
        exporter.meshtastic_mesh_packets_total, "add"
    )

    exporter.on_meshtastic_mesh_packet(packet_decoded)

    mock_set_last_heard_timestamp_seconds.assert_called_once()
    mock_add_packets_total.assert_called_once()
