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

import logging
import os
import ssl
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

logger = logging.getLogger(__name__)

logger.setLevel(getattr(logging, config["log_level"].upper()))

handler = logging.StreamHandler(stdout)
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - meshtastic_prometheus_exporter - %(levelname)s - %(message)s"
    )
)

logger.addHandler(handler)

redis = redis.from_url(config["redis_url"], db=0, protocol=3)

headers = {}
if config["prometheus_token"]:
    headers = {
        "Authorization": f'Bearer {config["prometheus_token"]}',
    }

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
meter = metrics.get_meter(__name__)

meshtastic_mesh_packets_total = meter.create_counter(
    name="meshtastic_mesh_packets_total",
)

meshtastic_node_info_last_heard_timestamp_seconds = meter.create_gauge(
    name="meshtastic_node_info_last_heard_timestamp_seconds",
)

meshtastic_neighbor_info_snr_decibels = meter.create_gauge(
    name="meshtastic_neighbor_info_snr_decibels",
)

meshtastic_neighbor_info_last_rx_time = meter.create_gauge(
    name="meshtastic_neighbor_info_last_rx_time",
)

meshtastic_telemetry_device_battery_level_percent = meter.create_gauge(
    name="meshtastic_telemetry_device_battery_level_percent",
)

meshtastic_telemetry_device_voltage_volts = meter.create_gauge(
    name="meshtastic_telemetry_device_voltage_volts",
)

meshtastic_telemetry_device_channel_utilization_percent = meter.create_gauge(
    name="meshtastic_telemetry_device_channel_utilization_percent",
)

meshtastic_telemetry_device_air_util_tx_percent = meter.create_gauge(
    name="meshtastic_telemetry_device_air_util_tx_percent",
)

meshtastic_telemetry_env_temperature_celsius = meter.create_gauge(
    name="meshtastic_telemetry_env_temperature_celsius",
)

meshtastic_telemetry_env_relative_humidity_percent = meter.create_gauge(
    name="meshtastic_telemetry_env_relative_humidity_percent",
)

meshtastic_telemetry_env_barometric_pressure_pascal = meter.create_gauge(
    name="meshtastic_telemetry_env_barometric_pressure_pascal",
)

meshtastic_telemetry_env_gas_resistance_ohms = meter.create_gauge(
    name="meshtastic_telemetry_env_gas_resistance_ohms",
)

meshtastic_telemetry_env_voltage_volts = meter.create_gauge(
    name="meshtastic_telemetry_env_voltage_volts",
)

meshtastic_telemetry_env_current_amperes = meter.create_gauge(
    name="meshtastic_telemetry_env_current_amperes",
)

meshtastic_telemetry_power_ch1_voltage_volts = meter.create_gauge(
    name="meshtastic_telemetry_power_ch1_voltage_volts",
)

meshtastic_telemetry_power_ch1_current_amperes = meter.create_gauge(
    name="meshtastic_telemetry_power_ch1_current_amperes",
)

meshtastic_telemetry_power_ch2_voltage_volts = meter.create_gauge(
    name="meshtastic_telemetry_power_ch2_voltage_volts",
)

meshtastic_telemetry_power_ch2_current_amperes = meter.create_gauge(
    name="meshtastic_telemetry_power_ch2_current_amperes",
)

meshtastic_telemetry_power_ch3_voltage_volts = meter.create_gauge(
    name="meshtastic_telemetry_power_ch3_voltage_volts",
)

meshtastic_telemetry_power_ch3_current_amperes = meter.create_gauge(
    name="meshtastic_telemetry_power_ch3_current_amperes",
)

meshtastic_telemetry_air_quality_pm10_standard = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_pm10_standard",
)

meshtastic_telemetry_air_quality_pm25_standard = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_pm25_standard",
)

meshtastic_telemetry_air_quality_pm100_standard = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_pm100_standard",
)

meshtastic_telemetry_air_quality_pm10_environmental = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_pm10_environmental",
)

meshtastic_telemetry_air_quality_pm25_environmental = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_pm25_environmental",
)

meshtastic_telemetry_air_quality_pm100_environmental = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_pm100_environmental",
)

meshtastic_telemetry_air_quality_particles_03um = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_particles_03um",
)

meshtastic_telemetry_air_quality_particles_05um = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_particles_05um",
)

meshtastic_telemetry_air_quality_particles_10um = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_particles_10um",
)

meshtastic_telemetry_air_quality_particles_25um = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_particles_25um",
)

meshtastic_telemetry_air_quality_particles_50um = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_particles_50um",
)

meshtastic_telemetry_air_quality_particles_100um = meter.create_gauge(
    name="meshtastic_telemetry_air_quality_particles_100um",
)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        logger.warning(
            f"Failed to connect to MQTT server with result code {reason_code}. loop_forever() will retry connection"
        )
    else:
        logger.info(f"Connected to MQTT server with result code {reason_code}")
        client.subscribe(config["mqtt_topic"])


def get_decoded_node_metadata_from_redis(node: float, metadata: str):
    v = redis.hget(node, metadata)
    try:
        v = "unknown" if v is None else v.decode("utf-8")
    except UnicodeDecodeError:
        v = "unknown"
    return v


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
    if hasattr(packet, "encrypted"):
        logger.debug(f"Skipping processing of encrypted packet {packet['id']}")
        return

    unique = redis.set(str(packet["id"]), 1, nx=True, ex=config["flood_expire_time"])

    if not unique:
        logger.debug(f"Skipping processing of duplicate packet {packet['id']}")
        return

    source = packet["decoded"].get("source", packet["from"])

    source_long_name = get_decoded_node_metadata_from_redis(source, "long_name")
    source_short_name = get_decoded_node_metadata_from_redis(source, "short_name")
    from_long_name = get_decoded_node_metadata_from_redis(packet["from"], "long_name")
    from_short_name = get_decoded_node_metadata_from_redis(packet["from"], "short_name")
    to_long_name = get_decoded_node_metadata_from_redis(packet["to"], "long_name")
    to_short_name = get_decoded_node_metadata_from_redis(packet["to"], "short_name")

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
        on_meshtastic_nodeinfo_app(packet)
    else:
        known_from = (
            get_decoded_node_metadata_from_redis(packet["from"], "long_name")
            != "unknown"
        )
        known_source = (
            get_decoded_node_metadata_from_redis(source, "long_name") != "unknown"
        )

        if not known_from:
            logger.info(
                f"Node {packet['from']} has not yet identified, ignoring the packet {packet['id']}"
            )
            return
        if not known_source and packet["decoded"].get("source", 0) != 0:
            logger.info(
                f"Node {source} has not yet identified, ignoring the packet {packet['id']}"
            )
            return

    if packet["decoded"]["portnum"] == "TELEMETRY_APP":
        on_meshtastic_telemetry_app(packet)

    if packet["decoded"]["portnum"] == "NEIGHBORINFO_APP":
        on_meshtastic_neighborinfo_app(packet)


def on_meshtastic_nodeinfo_app(packet):
    node_info = packet["decoded"]["user"]

    logger.info(
        f"Decoded MeshPacket {packet['id']} payload into NodeInfo `{node_info}`"
    )

    source = packet["decoded"].get("source", packet["from"])
    is_licensed = node_info.get("isLicensed", 0)
    if source:
        ex = 3600 * 72
        redis.hset(
            source,
            mapping={
                "long_name": node_info["longName"],
                "short_name": node_info["shortName"],
                "hw_model": node_info["hwModel"],
                "is_licensed": str(is_licensed),
            },
        )
        redis.expire(source, ex)

    node_info_attributes = {
        "source": source,
        "user": node_info["id"],
        "source_long_name": node_info["longName"],
        "source_short_name": node_info["shortName"],
        "is_licensed": str(is_licensed),
    }
    meshtastic_node_info_last_heard_timestamp_seconds.set(
        time.time(), attributes=node_info_attributes
    )


def on_meshtastic_telemetry_app(packet):
    telemetry = packet["decoded"]["telemetry"]
    logger.info(
        f"Decoded MeshPacket {packet['id']} payload into Telemetry `{telemetry}`"
    )
    source = packet["decoded"].get("source", packet["from"])
    telemetry_attributes = {
        "source": source or "unknown",
        "source_long_name": (
            get_decoded_node_metadata_from_redis(source, "long_name")
            if source
            else "unknown"
        ),
        "source_short_name": (
            get_decoded_node_metadata_from_redis(source, "short_name")
            if source
            else "unknown"
        ),
    }
    if "deviceMetrics" in telemetry:
        logger.info(
            f"MeshPacket {packet['id']} appears to be telemetry of type device metrics"
        )
        meshtastic_telemetry_device_battery_level_percent.set(
            telemetry["deviceMetrics"]["batteryLevel"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_device_voltage_volts.set(
            telemetry["deviceMetrics"]["voltage"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_device_channel_utilization_percent.set(
            telemetry["deviceMetrics"]["channelUtilization"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_device_air_util_tx_percent.set(
            telemetry["deviceMetrics"]["airUtilTx"],
            attributes=telemetry_attributes,
        )
    if "environmentMetrics" in telemetry:
        logger.info(
            f"MeshPacket {packet['id']} appears to be telemetry of type environment metrics"
        )
        meshtastic_telemetry_env_temperature_celsius.set(
            telemetry["environmentMetrics"]["temperature"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_env_relative_humidity_percent.set(
            telemetry["environmentMetrics"]["relativeHumidity"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_env_barometric_pressure_pascal.set(
            telemetry["environmentMetrics"]["barometricPressure"] * 10**2,
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_env_gas_resistance_ohms.set(
            telemetry["environmentMetrics"]["gasResistance"] / 10**6,
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_env_voltage_volts.set(
            telemetry["environmentMetrics"]["voltage"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_env_current_amperes.set(
            telemetry["environmentMetrics"]["current"] * 10**-3,
            attributes=telemetry_attributes,
        )
    if "airQualityMetrics" in telemetry:
        logger.info(
            f"MeshPacket {packet['id']} appears to be telemetry of type air quality metrics"
        )
        meshtastic_telemetry_air_quality_pm10_standard.set(
            telemetry["airQualityMetrics"]["pm10_standard"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_pm25_standard.set(
            telemetry["airQualityMetrics"]["pm25_standard"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_pm100_standard.set(
            telemetry["airQualityMetrics"]["pm100_standard"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_pm10_environmental.set(
            telemetry["airQualityMetrics"]["pm10_environmental"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_pm25_environmental.set(
            telemetry["airQualityMetrics"]["pm25_environmental"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_pm100_environmental.set(
            telemetry["airQualityMetrics"]["pm100_environmental"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_particles_03um.set(
            telemetry["airQualityMetrics"]["particles_03um"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_particles_05um.set(
            telemetry["airQualityMetrics"]["particles_05um"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_particles_10um.set(
            telemetry["airQualityMetrics"]["particles_10um"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_particles_25um.set(
            telemetry["airQualityMetrics"]["particles_25um"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_particles_50um.set(
            telemetry["airQualityMetrics"]["particles_50um"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_air_quality_particles_100um.set(
            telemetry["airQualityMetrics"]["particles_100um"],
            attributes=telemetry_attributes,
        )
    if "powerMetrics" in telemetry:
        logger.info(
            f"MeshPacket {packet['id']} appears to be telemetry of type power metrics"
        )
        meshtastic_telemetry_power_ch1_voltage_volts.set(
            telemetry["powerMetrics"]["ch1_voltage"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_power_ch1_current_amperes.set(
            telemetry["powerMetrics"]["ch1_current"] * 10**-3,
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_power_ch2_voltage_volts.set(
            telemetry["powerMetrics"]["ch2_voltage"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_power_ch2_current_amperes.set(
            telemetry["powerMetrics"]["ch2_current"] * 10**-3,
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_power_ch3_voltage_volts.set(
            telemetry["powerMetrics"]["ch3_voltage"],
            attributes=telemetry_attributes,
        )
        meshtastic_telemetry_power_ch3_current_amperes.set(
            telemetry["powerMetrics"]["ch3_current"] * 10**-3,
            attributes=telemetry_attributes,
        )


def on_meshtastic_neighborinfo_app(packet):
    neighbor_info = packet["decoded"]["payload"]
    logger.info(
        f"Decoded MeshPacket {packet['id']} payload into NeighborInfo `{neighbor_info}`"
    )

    source = neighbor_info["node_id"]
    neighbor_info_attributes = {
        "source": source,
        "source_long_name": (
            get_decoded_node_metadata_from_redis(source, "long_name")
            if source
            else "unknown"
        ),
        "source_short_name": (
            get_decoded_node_metadata_from_redis(source, "short_name")
            if source
            else "unknown"
        ),
    }
    for n in neighbor_info["neighbors"]:
        neighbor_source = n["node_id"]

        neighbor_info_attributes["neighbor_source"] = neighbor_source or "unknown"
        neighbor_info_attributes["neighbor_source_long_name"] = (
            get_decoded_node_metadata_from_redis(neighbor_source, "long_name")
            if source
            else "unknown"
        )
        neighbor_info_attributes["neighbor_source_short_name"] = (
            get_decoded_node_metadata_from_redis(neighbor_source, "short_name")
            if source
            else "unknown"
        )

        meshtastic_neighbor_info_snr_decibels.set(
            n["snr"], attributes=neighbor_info_attributes
        )
        meshtastic_neighbor_info_last_rx_time.set(
            n["last_rx_time"], attributes=neighbor_info_attributes
        )


def on_message(client, userdata, msg):
    try:
        logger.debug(
            f"Received UTF-8 payload `{msg['payload'].decode()}` from `{msg.topic}` topic"
        )
    except UnicodeDecodeError:
        try:
            envelope = ServiceEnvelope().parse(msg["payload"])
            on_meshtastic_service_envelope(envelope, msg)
        except Exception as e:
            logger.warning(f"Exception occurred while processing ServiceEnvelope: {e}")
    except Exception as e:
        logger.warning(f"Exception occurred in on_message: {e}")


def on_native_message(packet, interface):
    pass
    on_meshtastic_mesh_packet(packet)
    # logger.debug(
    #     f"Received UTF-8 payload `{packet['payload'].decode()}` from `{packet['to']pic}` topic"
    # )
    # try:
    #     logger.debug(
    #         f"Received UTF-8 payload `{packet['payload'].decode()}` from `{packet['to']pic}` topic"
    #     )
    # except UnicodeDecodeError:
    #     try:
    #         envelope = ServiceEnvelope().parse(packet['payload'])
    #         on_meshtastic_service_envelope(envelope, packet)
    #     except Exception as e:
    #         logger.warning(f"Exception occurred while processing ServiceEnvelope: {e}")
    # except Exception as e:
    #     logger.warning(f"Exception occurred in on_message: {e}")


if __name__ == "__main__":
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

    # pub.subscribe(on_recieve, "meshtastic.receive")
    import time

    while True:
        time.sleep(1)
