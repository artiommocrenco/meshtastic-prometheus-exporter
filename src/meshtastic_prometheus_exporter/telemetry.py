import logging
import json
from meshtastic_prometheus_exporter.metrics import *
from meshtastic_prometheus_exporter.util import get_decoded_node_metadata_from_redis

logger = logging.getLogger("meshtastic_prometheus_exporter")


def on_device_metrics_telemetry(packet, attributes):
    logger.info(f"MeshPacket {packet['id']} is device metrics telemetry")
    meshtastic_telemetry_device_battery_level_percent.set(
        packet["decoded"]["telemetry"]["deviceMetrics"]["batteryLevel"],
        attributes=attributes,
    )
    meshtastic_telemetry_device_voltage_volts.set(
        packet["decoded"]["telemetry"]["deviceMetrics"]["voltage"],
        attributes=attributes,
    )
    meshtastic_telemetry_device_channel_utilization_percent.set(
        packet["decoded"]["telemetry"]["deviceMetrics"]["channelUtilization"],
        attributes=attributes,
    )
    meshtastic_telemetry_device_air_util_tx_percent.set(
        packet["decoded"]["telemetry"]["deviceMetrics"]["airUtilTx"],
        attributes=attributes,
    )


def on_meshtastic_telemetry_app(packet, source_long_name, source_short_name):
    telemetry = packet["decoded"]["telemetry"]
    logger.debug(
        f"Received MeshPacket {packet['id']} with Telemetry `{json.dumps(telemetry, default=repr)}`"
    )
    source = packet["decoded"].get("source", packet["from"])
    telemetry_attributes = {
        "source": source or "unknown",
        "source_long_name": source_long_name or "unknown",
        "source_short_name": source_short_name or "unknown",
    }
    if "deviceMetrics" in telemetry:
        on_device_metrics_telemetry(packet, telemetry_attributes)
        return

    if "environmentMetrics" in telemetry:
        logger.info(f"MeshPacket {packet['id']} is environment metrics telemetry")
        if "temperature" in telemetry["environmentMetrics"]:
            meshtastic_telemetry_env_temperature_celsius.set(
                telemetry["environmentMetrics"]["temperature"],
                attributes=telemetry_attributes,
            )
        if "relativeHumidity" in telemetry["environmentMetrics"]:
            meshtastic_telemetry_env_relative_humidity_percent.set(
                telemetry["environmentMetrics"]["relativeHumidity"],
                attributes=telemetry_attributes,
            )
        if "barometricPressure" in telemetry["environmentMetrics"]:
            meshtastic_telemetry_env_barometric_pressure_pascal.set(
                telemetry["environmentMetrics"]["barometricPressure"] * 10**2,
                attributes=telemetry_attributes,
            )
        if "gasResistance" in telemetry["environmentMetrics"]:
            meshtastic_telemetry_env_gas_resistance_ohms.set(
                telemetry["environmentMetrics"]["gasResistance"] / 10**6,
                attributes=telemetry_attributes,
            )
        if "voltage" in telemetry["environmentMetrics"]:
            meshtastic_telemetry_env_voltage_volts.set(
                telemetry["environmentMetrics"]["voltage"],
                attributes=telemetry_attributes,
            )
        if "current" in telemetry["environmentMetrics"]:
            meshtastic_telemetry_env_current_amperes.set(
                telemetry["environmentMetrics"]["current"] * 10**-3,
                attributes=telemetry_attributes,
            )
    if "airQualityMetrics" in telemetry:
        logger.info(f"MeshPacket {packet['id']} is air quality metrics telemetry")
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
        logger.info(f"MeshPacket {packet['id']} is power metrics telemetry")
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
