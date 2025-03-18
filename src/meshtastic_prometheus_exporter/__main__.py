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
import sys
import time
import traceback
from sys import stdout
from google.protobuf.json_format import MessageToDict

import google.protobuf.message
import meshtastic.ble_interface
import meshtastic.serial_interface
import meshtastic.tcp_interface
import redis
from google.protobuf.json_format import MessageToDict
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
import paho.mqtt.client as mqtt
from meshtastic.protobuf import mqtt_pb2
from prometheus_client import start_http_server
from pubsub import pub
from redis import BusyLoadingError
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

from meshtastic_prometheus_exporter.metrics import *
from meshtastic_prometheus_exporter.neighborinfo import on_meshtastic_neighborinfo_app
from meshtastic_prometheus_exporter.nodeinfo import on_meshtastic_nodeinfo_app
from meshtastic_prometheus_exporter.telemetry import on_meshtastic_telemetry_app
from meshtastic_prometheus_exporter.util import (
    get_decoded_node_metadata_from_redis,
    save_node_metadata_in_redis,
)

config = {
    "meshtastic_interface": os.environ.get("MESHTASTIC_INTERFACE"),
    "interface_serial_device": os.environ.get("SERIAL_DEVICE", "/dev/ttyACM0"),
    "interface_tcp_addr": os.environ.get("INTERFACE_TCP_ADDR"),
    "interface_tcp_port": os.environ.get(
        "INTERFACE_TCP_PORT", meshtastic.tcp_interface.DEFAULT_TCP_PORT
    ),
    "interface_ble_addr": os.environ.get("INTERFACE_BLE_ADDR", "/dev/ttyACM0"),
    "mqtt_address": os.environ.get("MQTT_ADDRESS", "mqtt.meshtastic.org"),
    "mqtt_use_tls": os.environ.get("MQTT_USE_TLS", False),
    "mqtt_port": os.environ.get("MQTT_PORT", 1883),
    "mqtt_keepalive": os.environ.get("MQTT_KEEPALIVE", 15),
    "mqtt_username": os.environ.get("MQTT_USERNAME"),
    "mqtt_password": os.environ.get("MQTT_PASSWORD"),
    "mqtt_topic": os.environ.get("MQTT_TOPIC", "msh/EU_433/#"),
    "prometheus_server_addr": os.environ.get("PROMETHEUS_SERVER_ADDR", "0.0.0.0"),
    "prometheus_server_port": os.environ.get("PROMETHEUS_SERVER_PORT", 9464),
    "redis_url": os.environ.get("REDIS_URL", "redis://localhost:6379"),
    "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    "flood_expire_time": os.environ.get("FLOOD_EXPIRE_TIME", 10 * 60),
    "enable_sentry": os.environ.get("ENABLE_SENTRY", False),
    "sentry_dsn": os.environ.get(
        "SENTRY_DSN",
        "https://d03452fcb06e7141c5c9a1d6ee370e8d@o4508362511286272.ingest.de.sentry.io/4508362517381200",
    ),
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

if int(config["enable_sentry"]) == 1:
    import sentry_sdk
    from sentry_sdk import add_breadcrumb
    from sentry_sdk.integrations.logging import LoggingIntegration

    logger.info(
        "Enabling error reporting via Sentry. Your unmodified MeshPackets will be sent to maintainers of this project in case of runtime errors. To disable, set ENABLE_SENTRY environment variable to 0"
    )

    def before_breadcrumb(crumb, hint):
        if crumb["category"] == "redis":
            return None
        return crumb

    sentry_sdk.init(
        dsn=config.get("sentry_dsn"),
        traces_sample_rate=1.0,
        before_breadcrumb=before_breadcrumb,
        integrations=[
            LoggingIntegration(level=logging.INFO, event_level=logging.FATAL),
        ],
    )
else:
    logger.info(
        "Error reporting via Sentry is disabled. If you want to send your unmodified MeshPackets to maintainers of this project in case of runtime errors, set ENABLE_SENTRY environment variable to 1"
    )


try:
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

    redis = redis.from_url(
        config["redis_url"],
        db=0,
        protocol=3,
        retry=Retry(ExponentialBackoff(10, 1), 3),
        retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
    )

except Exception as e:
    logger.fatal(
        f"Exception occurred while starting up: {';'.join(traceback.format_exc().splitlines())}"
    )
    sys.exit(1)


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

    if packet.get("id", None) is None:
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
            "via_mqtt": packet.get("viaMqtt", "false"),
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


def on_message(client, userdata, msg):
    try:
        envelope = mqtt_pb2.ServiceEnvelope.FromString(msg.payload)
        packet = envelope.packet
        logger.debug(
            f"Received UTF-8 payload `{MessageToDict(envelope)}` from `{msg.topic}` topic"
        )
        on_native_message(MessageToDict(packet), None)
    except Exception as e:
        logger.warning(f"Exception occurred in on_message: {e}")


def on_native_message(packet, interface):
    try:
        on_meshtastic_mesh_packet(packet)
    except Exception as e:
        logger.error(
            f"{e} occurred while processing MeshPacket {packet}, please consider submitting a PR/issue on GitHub: `{json.dumps(packet, default=repr)}` {';'.join(traceback.format_exc().splitlines())
}"
        )
        if "sentry_sdk" in globals():
            sentry_sdk.capture_exception(e)


def on_native_connection_established(interface, topic=pub.AUTO_TOPIC):
    logger.info(f"Connected to device over {type(interface).__name__}")


def on_native_connection_lost(interface, topic=pub.AUTO_TOPIC):
    logger.warning(f"Lost connection to device over {type(interface).__name__}")


def main():
    try:
        logger.info(
            "Share ideas and vote for new features https://github.com/artiommocrenco/meshtastic-prometheus-exporter/discussions/categories/ideas"
        )

        if config.get("meshtastic_interface") not in ["MQTT", "SERIAL", "TCP", "BLE"]:
            logger.fatal(
                f"Invalid value for MESHTASTIC_INTERFACE: {config['meshtastic_interface']}. Must be one of: MQTT, SERIAL, TCP, BLE"
            )
            sys.exit(1)

        pub.subscribe(on_native_message, "meshtastic.receive")
        pub.subscribe(
            on_native_connection_established, "meshtastic.connection.established"
        )
        pub.subscribe(on_native_connection_lost, "meshtastic.connection.lost")

        if config.get("meshtastic_interface") == "SERIAL":
            iface = meshtastic.serial_interface.SerialInterface(
                devPath=config.get("serial_device")
            )
        elif config.get("meshtastic_interface") == "TCP":
            iface = meshtastic.tcp_interface.TCPInterface(
                hostname=config.get("interface_tcp_addr"),
                portNumber=int(config.get("interface_tcp_port")),
            )
        elif config.get("meshtastic_interface") == "BLE":
            iface = meshtastic.ble_interface.BLEInterface(
                address=config.get("interface_ble_addr"),
            )
        elif config.get("meshtastic_interface") == "MQTT":
            mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

            mqttc.on_connect = on_connect
            mqttc.on_message = on_message

            if int(config["mqtt_use_tls"]) == 1:
                tlscontext = ssl.create_default_context()
                mqttc.tls_set_context(tlscontext)

            if config["mqtt_username"]:
                mqttc.username_pw_set(config["mqtt_username"], config["mqtt_password"])

            mqttc.connect(
                config["mqtt_address"],
                int(config["mqtt_port"]),
                keepalive=int(config["mqtt_keepalive"]),
            )

            mqttc.loop_forever()

        if hasattr(iface, "nodes") and len(iface.nodes) > 0:
            logger.info(
                f"NodeDB is available, saving metadata in Redis for {len(iface.nodes.values())} nodes"
            )
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
        else:
            logger.warning(
                "Device NodeDB is empty or not available. NodeInfo are not sent often, so populating local NodeDB (stored in Redis) may take from several hours to several days or more."
            )
            logger.warning(
                "Consider first connecting a node with populated NodeDB over Serial, BLE or TCP interface, so that Redis is populated with NodeInfo faster."
            )

        while True:
            time.sleep(1)

    except Exception as e:
        logger.fatal(
            f"Exception occurred while starting up: {';'.join(traceback.format_exc().splitlines())}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
