# meshtastic-prometheus-exporter

![meshtasticexporter](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/assets/28516476/162a2fab-5804-46d0-a97a-aa84e388ef58)

## Supported metrics

| Name                                                 | Type    |
|------------------------------------------------------|---------|
| meshtastic_mesh_packet_count_total                   | counter |
| meshtastic_node_info_last_heard                      | gauge   |
| meshtastic_neighbor_info_snr                         | gauge   |
| meshtastic_neighbor_info_last_rx_time                | gauge   |
| meshtastic_telemetry_device_battery_level            | gauge   |
| meshtastic_telemetry_device_voltage                  | gauge   |
| meshtastic_telemetry_device_channel_utilization      | gauge   |
| meshtastic_telemetry_device_air_util_tx              | gauge   |
| meshtastic_telemetry_environment_temperature         | gauge   |
| meshtastic_telemetry_environment_relative_humidity   | gauge   |
| meshtastic_telemetry_environment_barometric_pressure | gauge   |
| meshtastic_telemetry_environment_gas_resistance      | gauge   |
| meshtastic_telemetry_environment_voltage             | gauge   |
| meshtastic_telemetry_environment_current             | gauge   |
| meshtastic_telemetry_power_ch1_voltage               | gauge   |
| meshtastic_telemetry_power_ch1_current               | gauge   |
| meshtastic_telemetry_power_ch2_voltage               | gauge   |
| meshtastic_telemetry_power_ch2_current               | gauge   |
| meshtastic_telemetry_power_ch3_voltage               | gauge   |
| meshtastic_telemetry_power_ch3_current               | gauge   |
| meshtastic_telemetry_air_quality_pm10_standard       | gauge   |
| meshtastic_telemetry_air_quality_pm25_standard       | gauge   |
| meshtastic_telemetry_air_quality_pm100_standard      | gauge   |
| meshtastic_telemetry_air_quality_pm10_environmental  | gauge   |
| meshtastic_telemetry_air_quality_pm25_environmental  | gauge   |
| meshtastic_telemetry_air_quality_pm100_environmental | gauge   |
| meshtastic_telemetry_air_quality_particles_03um      | gauge   |
| meshtastic_telemetry_air_quality_particles_05um      | gauge   |
| meshtastic_telemetry_air_quality_particles_10um      | gauge   |
| meshtastic_telemetry_air_quality_particles_25um      | gauge   |
| meshtastic_telemetry_air_quality_particles_50um      | gauge   |
| meshtastic_telemetry_air_quality_particles_100um     | gauge   |

## Usage

1. configure a node (firmware version SHOULD be exactly equal to `v2.3.0.5f47ca1`) in the mesh as uplink to your
   MQTT server of choice
2. use env vars to specify connection details to your MQTT server of choice (see `docker-compose.yml`)
3. run `docker-compose up -d`

Within a few minutes, data should begin populating on the dashboards. Wait several hours to allow Redis to be populated
with node information. After the wait, all data should be visible on the dashboards.

This has been tested with:

- Prometheus pull scheme as in `docker-compose.yml`
- Scaleway
  Cockpit & [Grafana Mimir remote write api](https://grafana.com/docs/mimir/latest/references/http-api/#remote-write)

## Known limitations

* All nodes serving as MQTT uplinks SHOULD have firmware version exactly equal to `v2.3.0.5f47ca1`
* Running two exporters for the same meshtastic network that write to the same Prometheus is not yet supported
* Processing of MQTT data from several meshtastic nodes has not yet been tested
* While mostly reporting useful information, Grafana dashboards do contain mistakes in some of the visualizations
* Using TLS for MQTT on meshtastic side may be problematic for performance and reliability (third-party issue)
* Exception handling & code quality need improvement
* Inefficient usage of main thread (does not use asyncio)

## Contributing

Please feel free to contribute
