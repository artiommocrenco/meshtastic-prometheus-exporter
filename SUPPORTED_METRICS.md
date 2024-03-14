# Supported metrics

| Name                                                    | Type    |
|---------------------------------------------------------|---------|
| meshtastic_mesh_packets_total                           | counter |
| meshtastic_node_info_last_heard_timestamp_seconds       | gauge   |
| meshtastic_neighbor_info_snr_decibels                   | gauge   |
| meshtastic_neighbor_info_last_rx_time                   | gauge   |
| meshtastic_telemetry_device_battery_level_percent       | gauge   |
| meshtastic_telemetry_device_voltage_volts               | gauge   |
| meshtastic_telemetry_device_channel_utilization_percent | gauge   |
| meshtastic_telemetry_device_air_util_tx_percent         | gauge   |
| meshtastic_telemetry_env_temperature_celsius            | gauge   |
| meshtastic_telemetry_env_relative_humidity_percent      | gauge   |
| meshtastic_telemetry_env_barometric_pressure_pascal     | gauge   |
| meshtastic_telemetry_env_gas_resistance_ohms            | gauge   |
| meshtastic_telemetry_env_voltage_volts                  | gauge   |
| meshtastic_telemetry_env_current_amperes                | gauge   |
| meshtastic_telemetry_power_ch1_voltage_volts            | gauge   |
| meshtastic_telemetry_power_ch1_current_amperes          | gauge   |
| meshtastic_telemetry_power_ch2_voltage_volts            | gauge   |
| meshtastic_telemetry_power_ch2_current_amperes          | gauge   |
| meshtastic_telemetry_power_ch3_voltage_volts            | gauge   |
| meshtastic_telemetry_power_ch3_current_amperes          | gauge   |

## Air quality metrics

:interrobang: Who knows which units these are, please submit a PR/issue

| Name                                                 | Type  |
|------------------------------------------------------|-------|
| meshtastic_telemetry_air_quality_pm10_standard       | gauge |
| meshtastic_telemetry_air_quality_pm25_standard       | gauge |
| meshtastic_telemetry_air_quality_pm100_standard      | gauge |
| meshtastic_telemetry_air_quality_pm10_environmental  | gauge |
| meshtastic_telemetry_air_quality_pm25_environmental  | gauge |
| meshtastic_telemetry_air_quality_pm100_environmental | gauge |
| meshtastic_telemetry_air_quality_particles_03um      | gauge |
| meshtastic_telemetry_air_quality_particles_05um      | gauge |
| meshtastic_telemetry_air_quality_particles_10um      | gauge |
| meshtastic_telemetry_air_quality_particles_25um      | gauge |
| meshtastic_telemetry_air_quality_particles_50um      | gauge |
| meshtastic_telemetry_air_quality_particles_100um     | gauge |
