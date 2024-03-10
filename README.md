# meshtastic-prometheus-exporter

## Usage

1. configure at least one node (firmware version SHOULD be exactly equal to `v2.2.23`) in the mesh as uplink to your MQTT server of choice
2. obtain access to a Grafana with Prometheus data source that supports Prometheus remote write 
3. use env vars to specify connection details to your MQTT server of choice (see `docker-compose.yml`)
4. use env vars to specify Prometheus remote write URL & token (see `docker-compose.yml`)
5. run `docker-compose up --build`
6. import the Grafana dashboards located in the `grafana-dashboards/` directory
7. within a few minutes, data should begin populating on the dashboards
8. wait several hours to allow Redis to be populated with node information
9. after the wait, all data should be visible on the dashboards

This has been tested with Scaleway Cockpit & Grafana Mimir remote write api
https://grafana.com/docs/mimir/latest/references/http-api/#remote-write

## Known limitations

* All nodes serving as MQTT uplinks SHOULD have firmware version exactly equal to `v2.2.23`
* Only Prometheus remote write is supported
* Running two exporters for the same meshtastic network that write to the same Prometheus is not yet supported
* Processing of MQTT data from several meshtastic nodes has not yet been tested
* While mostly reporting useful information, Grafana dashboards do contain mistakes in some of the visualizations
* Using TLS for MQTT on meshtastic side may be problematic for performance and reliability (third-party issue)
* Exception handling & code quality need improvement
* Inefficient usage of main thread (does not use asyncio)