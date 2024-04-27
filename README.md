# meshtastic-prometheus-exporter

![meshtasticexporter](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/assets/28516476/162a2fab-5804-46d0-a97a-aa84e388ef58)

## Supported metrics

See [SUPPORTED_METRICS.md](SUPPORTED_METRICS.md) for a list of supported metrics

## Usage

1. find an MQTT server you want to use or use the public Meshtastic MQTT server (`mqtt.meshtastic.org`)
2. for your meshtastic node (you should be using firmware version `2.3.7.30fbcab`), [configure and enable MQTT module](https://meshtastic.org/docs/configuration/module/mqtt/) for uplink
3. download (preferably) [latest release](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/releases/latest), uncompress it and navigate to the directory with the `docker-compose.yml` file
4. edit the `docker-compose.yml` file and specify connection details to the MQTT server there too
5. in your terminal, run `docker-compose up --build --force-recreate` (for this, you need docker installed)
6. in your web browser, navigate to http://localhost:3000/dashboards and authenticate using default Grafana credentials (username `admin`, password `admin`)

Within a few minutes, data should begin populating on the dashboards. At first, you are likely to see most packets as if they come from "unknown" sources.  Wait several hours to allow Redis to be populated
with node information (nodes rarely send information about themselves, usually every 3 hours). After the wait, all data should be visible on the dashboards.

This has been tested with:

- Prometheus pull scheme as in `docker-compose.yml`
- Scaleway
  Cockpit & [Grafana Mimir remote write api](https://grafana.com/docs/mimir/latest/references/http-api/#remote-write)

## Known limitations

* All nodes serving as MQTT uplinks SHOULD have firmware version specified above
* Running two exporters for the same meshtastic network that write to the same Prometheus is not supported
* While mostly reporting useful information, Grafana dashboards do contain mistakes in some of the visualizations
* Using TLS for MQTT on meshtastic side may be problematic for performance and reliability (third-party issue)
* Exception handling & code quality need improvement
* Inefficient usage of main thread (does not use asyncio)

## Contributing

Please feel free to contribute
