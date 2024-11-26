import logging
import time
from meshtastic_prometheus_exporter.metrics import *
import json

from meshtastic_prometheus_exporter.util import save_node_metadata_in_redis

logger = logging.getLogger("meshtastic_prometheus_exporter")


def on_meshtastic_nodeinfo_app(redis, packet):
    node_info = packet["decoded"]["user"]

    logger.debug(
        f"Received MeshPacket {packet['id']} with NodeInfo `{json.dumps(node_info, default=repr)}`"
    )

    source = packet["decoded"].get("source", packet["from"])

    if source:
        save_node_metadata_in_redis(redis, source, node_info)

    node_info_attributes = {
        "source": source,
        "user": node_info["id"],
        "source_long_name": node_info["longName"],
        "source_short_name": node_info["shortName"],
        "is_licensed": str(node_info.get("isLicensed", 0)),
    }
    meshtastic_node_info_last_heard_timestamp_seconds.set(
        time.time(), attributes=node_info_attributes
    )
