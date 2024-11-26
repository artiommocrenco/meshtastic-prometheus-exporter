from opentelemetry import metrics

meter = metrics.get_meter("meshtastic_prometheus_exporter")

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
