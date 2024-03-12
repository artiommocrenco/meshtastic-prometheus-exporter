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

import paho.mqtt.client as mqtt
import redis
from meshtastic import ServiceEnvelope, PortNum, Telemetry, User, NeighborInfo
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.prometheus_remote_write import (
    PrometheusRemoteWriteMetricsExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server

logging.basicConfig(stream=stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

meshtastic_mesh_packet_priority_view = View(
    instrument_name="meshtastic_mesh_packet_priority",
    aggregation=ExplicitBucketHistogramAggregation([1, 10, 64, 70, 120, 127]),
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
    "redis_host": os.environ.get("REDIS_HOST", "localhost"),
    "redis_port": os.environ.get("REDIS_PORT", 6379),
}

redis = redis.Redis(
    host=config["redis_host"], port=config["redis_port"], db=0, protocol=3
)

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
else:
    exporter = PrometheusRemoteWriteMetricsExporter(
        endpoint=config["prometheus_endpoint"],
        headers=headers,
    )
    reader = PeriodicExportingMetricReader(exporter, 15000)

provider = MeterProvider(
    resource=Resource.create(attributes={"service.name": "meshtastic"}),
    metric_readers=[reader],
    views=[
        meshtastic_mesh_packet_priority_view,
    ],
)
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__)

meshtastic_mesh_packet_priority = meter.create_histogram(
    name="meshtastic_mesh_packet_priority",
)

meshtastic_mesh_packet_count_total = meter.create_counter(
    name="meshtastic_mesh_packet_count_total",
)

meshtastic_node_info_last_heard = meter.create_gauge(
    name="meshtastic_node_info_last_heard",
)

meshtastic_neighbour_info_snr = meter.create_gauge(
    name="meshtastic_neighbour_info_snr",
)

meshtastic_neighbour_info_last_rx_time = meter.create_gauge(
    name="meshtastic_neighbour_info_last_rx_time",
)

meshtastic_telemetry_device_battery_level = meter.create_gauge(
    name="meshtastic_telemetry_device_battery_level",
)

meshtastic_telemetry_device_voltage = meter.create_gauge(
    name="meshtastic_telemetry_device_voltage",
)

meshtastic_telemetry_device_channel_utilization = meter.create_gauge(
    name="meshtastic_telemetry_device_channel_utilization",
)

meshtastic_telemetry_device_air_util_tx = meter.create_gauge(
    name="meshtastic_telemetry_device_air_util_tx",
)

meshtastic_telemetry_environment_temperature = meter.create_gauge(
    name="meshtastic_telemetry_environment_temperature",
)

meshtastic_telemetry_environment_relative_humidity = meter.create_gauge(
    name="meshtastic_telemetry_environment_relative_humidity",
)

meshtastic_telemetry_environment_barometric_pressure = meter.create_gauge(
    name="meshtastic_telemetry_environment_barometric_pressure",
)

meshtastic_telemetry_environment_gas_resistance = meter.create_gauge(
    name="meshtastic_telemetry_environment_gas_resistance",
)

meshtastic_telemetry_environment_voltage = meter.create_gauge(
    name="meshtastic_telemetry_environment_voltage",
)

meshtastic_telemetry_environment_current = meter.create_gauge(
    name="meshtastic_telemetry_environment_current",
)

meshtastic_telemetry_power_ch1_voltage = meter.create_gauge(
    name="meshtastic_telemetry_power_ch1_voltage",
)

meshtastic_telemetry_power_ch1_current = meter.create_gauge(
    name="meshtastic_telemetry_power_ch1_current",
)

meshtastic_telemetry_power_ch2_voltage = meter.create_gauge(
    name="meshtastic_telemetry_power_ch2_voltage",
)

meshtastic_telemetry_power_ch2_current = meter.create_gauge(
    name="meshtastic_telemetry_power_ch2_current",
)

meshtastic_telemetry_power_ch3_voltage = meter.create_gauge(
    name="meshtastic_telemetry_power_ch3_voltage",
)

meshtastic_telemetry_power_ch3_current = meter.create_gauge(
    name="meshtastic_telemetry_power_ch3_current",
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
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print(f"Connected with result code {reason_code}")
        client.subscribe(config["mqtt_topic"])


def get_decoded_node_metadata_from_redis(node: float, metadata: str):
    v = redis.get(f"{node}_{metadata}")
    try:
        v = "unknown" if v is None else v.decode("utf-8")
    except UnicodeDecodeError:
        v = "unknown"
    return v


def on_message(client, userdata, msg):
    try:
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    except UnicodeDecodeError:
        print(f"Received `{msg.payload}` from `{msg.topic}` topic")
        envelope = ServiceEnvelope().parse(msg.payload)

        unique = redis.set(str(envelope.packet.id), 1, nx=True, ex=3600 * 5)

        if not unique:
            print(f"Duplicate packet {envelope.packet.id}")
            return

        if envelope:
            print(envelope.packet)

            from_long_name = get_decoded_node_metadata_from_redis(
                envelope.packet.from_, "long_name"
            )
            from_short_name = get_decoded_node_metadata_from_redis(
                envelope.packet.from_, "short_name"
            )
            to_long_name = get_decoded_node_metadata_from_redis(
                envelope.packet.to, "long_name"
            )
            to_short_name = get_decoded_node_metadata_from_redis(
                envelope.packet.to, "short_name"
            )

            meshtastic_mesh_packet_count_total.add(
                1,
                attributes={
                    "from": envelope.packet.from_,
                    "from_long_name": from_long_name,
                    "from_short_name": from_short_name,
                    "to": envelope.packet.to,
                    "to_long_name": to_long_name,
                    "to_short_name": to_short_name,
                    "channel": envelope.packet.channel,
                    "type": next(
                        (
                            name
                            for name, member in PortNum.__members__.items()
                            if member.value == envelope.packet.decoded.portnum
                        ),
                        "unknown",
                    ),
                    "hop_limit": envelope.packet.hop_limit,
                    "want_ack": envelope.packet.want_ack,
                    "delayed": envelope.packet.delayed,
                    "via_mqtt": envelope.packet.via_mqtt,
                },
            )

            # https://buf.build/meshtastic/protobufs/file/main:meshtastic/portnums.proto
            if envelope.packet.decoded.portnum == PortNum.NODEINFO_APP:
                print("Appears to be node (user) info")
                node_info = User().parse(envelope.packet.decoded.payload)
                print(node_info)

                node = envelope.packet.decoded.source or envelope.packet.from_
                if node:
                    ex = 3600 * 72
                    redis.set(f"{node}_long_name", str(node_info.long_name), ex=ex)
                    redis.set(f"{node}_short_name", str(node_info.short_name), ex=ex)
                    redis.set(f"{node}_macaddr", str(node_info.macaddr), ex=ex)
                    redis.set(f"{node}_hw_model", str(node_info.hw_model), ex=ex)
                    redis.set(f"{node}_is_licensed", str(node_info.is_licensed), ex=ex)
                    redis.set(f"{node}_role", str(node_info.role), ex=ex)

                node_info_attributes = {
                    "node": node or "unknown",
                    "user": node_info.id or "unknown",
                    "long_name": node_info.long_name or "unknown",
                    "short_name": node_info.short_name or "unknown",
                    "hw_model": node_info.hw_model or "unknown",
                    "is_licensed": node_info.is_licensed or "unknown",
                    "role": node_info.role or "unknown",
                }
                meshtastic_node_info_last_heard.set(
                    time(), attributes=node_info_attributes
                )
            else:
                node = envelope.packet.decoded.source or envelope.packet.from_

                known_node = redis.get(f"{node}_long_name")

                if known_node is None:
                    print(f"Node {node} has not yet identified, ignoring the packet")
                    return

            if envelope.packet.decoded.portnum == PortNum.TELEMETRY_APP:
                telemetry = Telemetry().parse(envelope.packet.decoded.payload)
                print(telemetry)
                node = envelope.packet.decoded.source or envelope.packet.from_
                telemetry_attributes = {
                    "node": node or "unknown",
                    "node_long_name": (
                        get_decoded_node_metadata_from_redis(node, "long_name")
                        if node
                        else "unknown"
                    ),
                    "node_short_name": (
                        get_decoded_node_metadata_from_redis(node, "short_name")
                        if node
                        else "unknown"
                    ),
                }
                if (
                    hasattr(telemetry, "device_metrics")
                    and len(bytes(telemetry.device_metrics)) > 0
                ):
                    print("Appears to be telemetry of type device metrics")
                    meshtastic_telemetry_device_battery_level.set(
                        telemetry.device_metrics.battery_level,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_device_voltage.set(
                        telemetry.device_metrics.voltage,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_device_channel_utilization.set(
                        telemetry.device_metrics.channel_utilization,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_device_air_util_tx.set(
                        telemetry.device_metrics.air_util_tx,
                        attributes=telemetry_attributes,
                    )
                if (
                    hasattr(telemetry, "environment_metrics")
                    and len(bytes(telemetry.environment_metrics)) > 0
                ):
                    print("Appears to be telemetry of type environment metrics")
                    meshtastic_telemetry_environment_temperature.set(
                        telemetry.environment_metrics.temperature,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_environment_relative_humidity.set(
                        telemetry.environment_metrics.relative_humidity,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_environment_barometric_pressure.set(
                        telemetry.environment_metrics.barometric_pressure,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_environment_gas_resistance.set(
                        telemetry.environment_metrics.gas_resistance,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_environment_voltage.set(
                        telemetry.environment_metrics.voltage,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_environment_current.set(
                        telemetry.environment_metrics.current,
                        attributes=telemetry_attributes,
                    )
                if (
                    hasattr(telemetry, "air_quality_metrics")
                    and len(bytes(telemetry.air_quality_metrics)) > 0
                ):
                    print("Appears to be telemetry of type air quality metrics")
                    meshtastic_telemetry_air_quality_pm10_standard.set(
                        telemetry.air_quality_metrics.pm10_standard,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_pm25_standard.set(
                        telemetry.air_quality_metrics.pm25_standard,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_pm100_standard.set(
                        telemetry.air_quality_metrics.pm100_standard,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_pm10_environmental.set(
                        telemetry.air_quality_metrics.pm10_environmental,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_pm25_environmental.set(
                        telemetry.air_quality_metrics.pm25_environmental,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_pm100_environmental.set(
                        telemetry.air_quality_metrics.pm100_environmental,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_particles_03um.set(
                        telemetry.air_quality_metrics.particles_03um,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_particles_05um.set(
                        telemetry.air_quality_metrics.particles_05um,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_particles_10um.set(
                        telemetry.air_quality_metrics.particles_10um,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_particles_25um.set(
                        telemetry.air_quality_metrics.particles_25um,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_particles_50um.set(
                        telemetry.air_quality_metrics.particles_50um,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_air_quality_particles_100um.set(
                        telemetry.air_quality_metrics.particles_100um,
                        attributes=telemetry_attributes,
                    )
                if (
                    hasattr(telemetry, "power_metrics")
                    and len(bytes(telemetry.power_metrics)) > 0
                ):
                    print("Appears to be telemetry of type power metrics")
                    meshtastic_telemetry_power_ch1_voltage.set(
                        telemetry.power_metrics.ch1_voltage,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_power_ch1_current.set(
                        telemetry.power_metrics.ch1_current,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_power_ch2_voltage.set(
                        telemetry.power_metrics.ch2_voltage,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_power_ch2_current.set(
                        telemetry.power_metrics.ch2_current,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_power_ch3_voltage.set(
                        telemetry.power_metrics.ch3_voltage,
                        attributes=telemetry_attributes,
                    )
                    meshtastic_telemetry_power_ch3_current.set(
                        telemetry.power_metrics.ch3_current,
                        attributes=telemetry_attributes,
                    )

            if envelope.packet.decoded.portnum == PortNum.NEIGHBORINFO_APP:
                print(f"Appears to be Neighbour Info")
                neighbour_info = NeighborInfo().parse(envelope.packet.decoded.payload)
                print(neighbour_info)

                node = neighbour_info.node_id
                neighbour_info_attributes = {
                    "node": node or "unknown",
                    "node_long_name": (
                        get_decoded_node_metadata_from_redis(node, "long_name")
                        if node
                        else "unknown"
                    ),
                    "node_short_name": (
                        get_decoded_node_metadata_from_redis(node, "short_name")
                        if node
                        else "unknown"
                    ),
                }
                for n in neighbour_info.neighbors:
                    neighbour_node = n.node_id

                    neighbour_info_attributes["neighbour_node"] = (
                        neighbour_node or "unknown"
                    )
                    neighbour_info_attributes["neighbour_node_long_name"] = (
                        get_decoded_node_metadata_from_redis(
                            neighbour_node, "long_name"
                        )
                        if node
                        else "unknown"
                    )
                    neighbour_info_attributes["neighbour_node_short_name"] = (
                        get_decoded_node_metadata_from_redis(
                            neighbour_node, "short_name"
                        )
                        if node
                        else "unknown"
                    )

                    meshtastic_neighbour_info_snr.set(
                        n.snr, attributes=neighbour_info_attributes
                    )
                    meshtastic_neighbour_info_last_rx_time.set(
                        n.last_rx_time, attributes=neighbour_info_attributes
                    )

    except Exception as e:
        print(f"Exception in on_message: {e}")


if __name__ == "__main__":
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
