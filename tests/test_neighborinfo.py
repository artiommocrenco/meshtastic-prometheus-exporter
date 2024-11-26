import meshtastic_prometheus_exporter.__main__ as exporter
import json
from pytest_mock import MockerFixture
from unittest.mock import call


def mocked_get_decoded_node_metadata_from_redis(redis, node: float, metadata: str):
    return "mocked"


def test_nodeinfo(mocker: MockerFixture):
    packet = '{"from": 123456789, "to": 987654321, "decoded": {"portnum": "NEIGHBORINFO_APP", "neighborinfo": {"nodeId": 123456789, "lastSentById": 123456789, "nodeBroadcastIntervalSecs": 3600, "neighbors": [{"nodeId": 123456711, "snr": 3.5}, {"nodeId": 123456722, "snr": 6.5}, {"nodeId": 123456733, "snr": -11.5}, {"nodeId": 123456744, "snr": 6.25}, {"nodeId": 123456755, "snr": 6.75}]}}, "id": 3117092156, "rxTime": 1702513724, "rxSnr": -10.0, "hopLimit": 2, "rxRssi": -119, "fromId": "!b6ffffac", "toId": "^all"}'

    packet_decoded = json.loads(packet)

    mocker.patch("meshtastic_prometheus_exporter.__main__.redis")
    mocker.patch(
        "meshtastic_prometheus_exporter.neighborinfo.get_decoded_node_metadata_from_redis",
        new=mocked_get_decoded_node_metadata_from_redis,
    )
    mocker.patch(
        "meshtastic_prometheus_exporter.__main__.get_decoded_node_metadata_from_redis",
        new=mocked_get_decoded_node_metadata_from_redis,
    )
    mock_set_last_rx_time = mocker.patch.object(
        exporter.meshtastic_neighbor_info_last_rx_time, "set"
    )
    mock_set_snr_decibels = mocker.patch.object(
        exporter.meshtastic_neighbor_info_snr_decibels, "set"
    )
    mock_add_packets_total = mocker.patch.object(
        exporter.meshtastic_mesh_packets_total, "add"
    )

    exporter.on_meshtastic_mesh_packet(packet_decoded)

    # mock_set_last_rx_time.assert_called_once()
    mock_add_packets_total.assert_called_once()

    neighbor_info = json.loads(packet)["decoded"]["neighborinfo"]
    for n in neighbor_info["neighbors"]:
        mock_set_snr_decibels.assert_called()  # TODO: more logic here
