import logging
import json
from meshtastic_prometheus_exporter.util import get_decoded_node_metadata_from_redis
from meshtastic_prometheus_exporter.metrics import *

logger = logging.getLogger("meshtastic_prometheus_exporter")


def on_meshtastic_neighborinfo_app(redis, packet, source_long_name, source_short_name):
    neighbor_info = packet["decoded"]["neighborinfo"]
    logger.debug(
        f"Received MeshPacket {packet['id']} with NeighborInfo `{json.dumps(neighbor_info, default=repr)}`"
    )

    source = neighbor_info["nodeId"]
    neighbor_info_attributes = {
        "source": source,
        "source_long_name": source_long_name,
        "source_short_name": source_short_name,
    }
    for n in neighbor_info["neighbors"]:
        neighbor_source = n["nodeId"]

        neighbor_info_attributes["neighbor_source"] = neighbor_source or "unknown"
        neighbor_info_attributes["neighbor_source_long_name"] = (
            get_decoded_node_metadata_from_redis(redis, neighbor_source, "long_name")
            if source
            else "unknown"
        )
        neighbor_info_attributes["neighbor_source_short_name"] = (
            get_decoded_node_metadata_from_redis(redis, neighbor_source, "short_name")
            if source
            else "unknown"
        )

        meshtastic_neighbor_info_snr_decibels.set(
            n["snr"], attributes=neighbor_info_attributes
        )
        # https://buf.build/meshtastic/protobufs/file/main:meshtastic/mesh.proto#L1795
        # meshtastic_neighbor_info_last_rx_time.set(
        #     n["rxTime"], attributes=neighbor_info_attributes
        # )
