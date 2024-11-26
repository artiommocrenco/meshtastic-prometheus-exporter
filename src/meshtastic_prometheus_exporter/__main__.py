#!/usr/bin/python3

"""
meshtastic-prometheus-exporter
Copyright (C) 2024  Artiom Mocrenco and Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import json
import logging
import os
import ssl
import traceback
from sys import stdout
from time import time
import meshtastic.serial_interface
import paho.mqtt.client as mqtt
import redis
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider

from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server
from pubsub import pub
from sentry_sdk import add_breadcrumb
from sentry_sdk.integrations.logging import LoggingIntegration

from meshtastic_prometheus_exporter.neighborinfo import on_meshtastic_neighborinfo_app
from meshtastic_prometheus_exporter.nodeinfo import on_meshtastic_nodeinfo_app
from meshtastic_prometheus_exporter.telemetry import on_meshtastic_telemetry_app
from meshtastic_prometheus_exporter.metrics import *
from meshtastic_prometheus_exporter.util import (
    get_decoded_node_metadata_from_redis,
    save_node_metadata_in_redis,
)
import sentry_sdk


def before_breadcrumb(crumb, hint):
    if crumb["category"] == "redis":
        return None
    return crumb


sentry_sdk.init(
    dsn="https://d03452fcb06e7141c5c9a1d6ee370e8d@o4508362511286272.ingest.de.sentry.io/4508362517381200",
    traces_sample_rate=1.0,
    before_breadcrumb=before_breadcrumb,
    integrations=[
        LoggingIntegration(level=logging.INFO, event_level=logging.FATAL),
    ],
)

config = {
    "mqtt_address": os.environ.get("MQTT_ADDRESS", "mqtt.meshtastic.org"),
    "mqtt_use_tls": os.environ.get("MQTT_USE_TLS", False),
    "mqtt_port": os.environ.get("MQTT_PORT", 1883),
    "mqtt_keepalive": os.environ.get("MQTT_KEEPALIVE", 15),
    "mqtt_username": os.environ.get("MQTT_USERNAME"),
    "mqtt_password": os.environ.get("MQTT_PASSWORD"),
    "mqtt_topic": os.environ.get("MQTT_TOPIC", "msh/#"),
    "prometheus_endpoint": os.environ.get("PROMETHEUS_ENDPOINT"),
    "prometheus_token": os.environ.get("PROMETHEUS_TOKEN"),
    "prometheus_server_addr": os.environ.get("PROMETHEUS_SERVER_ADDR", "0.0.0.0"),
    "prometheus_server_port": os.environ.get("PROMETHEUS_SERVER_PORT", 9464),
    "redis_url": os.environ.get("REDIS_URL", "redis://localhost:6379"),
    "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    "flood_expire_time": os.environ.get("FLOOD_EXPIRE_TIME", 10 * 60),
}

logger = logging.getLogger("meshtastic_prometheus_exporter")
logger.propagate = False

logger.setLevel(getattr(logging, config["log_level"].upper()))

handler = logging.StreamHandler(stdout)
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - meshtastic_prometheus_exporter - %(levelname)s - %(message)s"
    )
)

logger.addHandler(handler)

redis = redis.from_url(config["redis_url"], db=0, protocol=3)

if config["prometheus_endpoint"] is None:
    reader = PrometheusMetricReader()
    start_http_server(
        port=config["prometheus_server_port"], addr=config["prometheus_server_addr"]
    )

provider = MeterProvider(
    resource=Resource.create(attributes={"service.name": "meshtastic"}),
    metric_readers=[reader],
    # views=[],
)
metrics.set_meter_provider(provider)
meter = metrics.get_meter("meshtastic_prometheus_exporter")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        logger.warning(
            f"Failed to connect to MQTT server with result code {reason_code}. loop_forever() will retry connection"
        )
    else:
        logger.info(f"Connected to MQTT server with result code {reason_code}")
        client.subscribe(config["mqtt_topic"])


def on_meshtastic_service_envelope(envelope, msg):
    logger.debug(
        f"Received ServiceEnvelope payload `{msg['payload']}` from `{msg.topic}` topic"
    )

    if envelope:
        logger.debug(
            f"Decoded ServiceEnvelope payload into MeshPacket `{envelope.packet}`"
        )
        on_meshtastic_mesh_packet(envelope.packet)


def on_meshtastic_mesh_packet(packet):
    if packet.get("encrypted", False):
        logger.info(f"Skipping encrypted packet {packet['id']}")
        return

    unique = redis.set(str(packet["id"]), 1, nx=True, ex=config["flood_expire_time"])

    if not unique:
        logger.info(f"Skipping duplicate packet {packet['id']}")
        return

    source = packet["decoded"].get("source", packet["from"])

    source_long_name = get_decoded_node_metadata_from_redis(redis, source, "long_name")
    source_short_name = get_decoded_node_metadata_from_redis(
        redis, source, "short_name"
    )
    from_long_name = get_decoded_node_metadata_from_redis(
        redis, packet["from"], "long_name"
    )
    from_short_name = get_decoded_node_metadata_from_redis(
        redis, packet["from"], "short_name"
    )
    to_long_name = get_decoded_node_metadata_from_redis(
        redis, packet["to"], "long_name"
    )
    to_short_name = get_decoded_node_metadata_from_redis(
        redis, packet["to"], "short_name"
    )

    # https://buf.build/meshtastic/protobufs/file/main:meshtastic/portnums.proto
    meshtastic_mesh_packets_total.add(
        1,
        attributes={
            "source": source,
            "source_long_name": source_long_name,
            "source_short_name": source_short_name,
            "from": packet["from"],
            "from_long_name": from_long_name,
            "from_short_name": from_short_name,
            "to": packet["to"],
            "to_long_name": to_long_name,
            "to_short_name": to_short_name,
            "channel": packet.get("channel", 0),
            "type": packet["decoded"]["portnum"],
            "hop_limit": packet.get("hopLimit", "unknown"),
            "want_ack": packet.get("wantAck", "unknown"),
            "delayed": packet.get("delayed", "unknown"),
            "via_mqtt": packet.get("viaMqtt", "unknown"),
        },
    )
    if packet["decoded"]["portnum"] == "NODEINFO_APP":
        on_meshtastic_nodeinfo_app(redis, packet)
    else:
        known_source = (
            get_decoded_node_metadata_from_redis(redis, source, "long_name")
            != "unknown"
        )

        if not known_source:
            logger.info(
                f"NodeInfo is now yet known for Node {source}, ignoring the packet {packet['id']}"
            )
            return

    if packet["decoded"]["portnum"] == "TELEMETRY_APP":
        on_meshtastic_telemetry_app(packet, source_long_name, source_short_name)

    if packet["decoded"]["portnum"] == "NEIGHBORINFO_APP":
        on_meshtastic_neighborinfo_app(
            redis, packet, source_long_name, source_short_name
        )


# def on_message(client, userdata, msg):
#     try:
#         logger.debug(
#             f"Received UTF-8 payload `{msg['payload'].decode()}` from `{msg.topic}` topic"
#         )
#     except UnicodeDecodeError:
#         try:
#             envelope = ServiceEnvelope().parse(msg["payload"])
#             on_meshtastic_service_envelope(envelope, msg)
#         except Exception as e:
#             logger.warning(f"Exception occurred while processing ServiceEnvelope: {e}")
#     except Exception as e:
#         logger.warning(f"Exception occurred in on_message: {e}")


def on_native_message(packet, interface):
    try:
        on_meshtastic_mesh_packet(packet)
    except Exception as e:
        logger.error(
            f"{e} occurred while processing MeshPacket {packet['id']}, please consider submitting a PR/issue on GitHub: `{json.dumps(packet, default=repr)}` {';'.join(traceback.format_exc().splitlines())
}"
        )

        sentry_sdk.capture_exception(e)


def main():
    # mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    #
    # mqttc.on_connect = on_connect
    # mqttc.on_message = on_message
    #
    # if int(config["mqtt_use_tls"]) == 1:
    #     tlscontext = ssl.create_default_context()
    #     mqttc.tls_set_context(tlscontext)
    #
    # if config["mqtt_username"]:
    #     mqttc.username_pw_set(config["mqtt_username"], config["mqtt_password"])
    #
    # mqttc.connect(
    #     config["mqtt_address"],
    #     int(config["mqtt_port"]),
    #     keepalive=int(config["mqtt_keepalive"]),
    # )
    #
    # mqttc.loop_forever()

    pub.subscribe(on_native_message, "meshtastic.receive")
    iface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM0")

    if hasattr(iface, "nodes"):
        for n in iface.nodes.values():
            save_node_metadata_in_redis(
                redis,
                n["num"],
                {
                    "longName": n["user"]["longName"],
                    "shortName": n["user"]["shortName"],
                    "hwModel": n["user"]["hwModel"],
                },
            )

    import time

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
