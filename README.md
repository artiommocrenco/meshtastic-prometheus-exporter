# meshtastic-prometheus-exporter

![meshtasticexporter](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/assets/28516476/162a2fab-5804-46d0-a97a-aa84e388ef58)

## Supported metrics

See [SUPPORTED_METRICS.md](SUPPORTED_METRICS.md) for a list of supported metrics

## Usage

1. configure a node (firmware version SHOULD be exactly equal to `v2.3.0.5f47ca1`) in the mesh as uplink to your
   MQTT server of choice
2. download (preferably) [latest release](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/releases/tag/2.3.0.5f47ca1-0.3), use env vars to specify connection details to your MQTT server of choice (see `docker-compose.yml`)
3. run `docker-compose up -d`

Within a few minutes, data should begin populating on the dashboards. Wait several hours to allow Redis to be populated
with node information. After the wait, all data should be visible on the dashboards.

This has been tested with:

- Prometheus pull scheme as in `docker-compose.yml`
- Scaleway
  Cockpit & [Grafana Mimir remote write api](https://grafana.com/docs/mimir/latest/references/http-api/#remote-write)

## Known limitations

* All nodes serving as MQTT uplinks SHOULD have firmware version exactly equal to `v2.3.0.5f47ca1`
* Running two exporters for the same meshtastic network that write to the same Prometheus is not supported
* While mostly reporting useful information, Grafana dashboards do contain mistakes in some of the visualizations
* Using TLS for MQTT on meshtastic side may be problematic for performance and reliability (third-party issue)
* Exception handling & code quality need improvement
* Inefficient usage of main thread (does not use asyncio)

## Contributing

Please feel free to contribute
