# meshtastic-prometheus-exporter

![meshtasticexporter](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/assets/28516476/162a2fab-5804-46d0-a97a-aa84e388ef58)

Meshtastic Prometheus Exporter captures and parses every MeshPacket from your Meshtastic network, exposing detailed metrics about the packets. It supports data collection via MQTT, BLE, Serial, or TCP, and makes these metrics available to Prometheus. It comes with grafana dashboards that help visualize network performance, node status, and telemetry for real-time or historical monitoring.

## Supported metrics

See [SUPPORTED_METRICS.md](SUPPORTED_METRICS.md) for a list of supported metrics

## Usage

### Use with MQTT

1. Find an MQTT server you want to use or use the public Meshtastic MQTT server (`mqtt.meshtastic.org`).
2. For your Meshtastic node, [configure and enable MQTT module](https://meshtastic.org/docs/configuration/module/mqtt/) for uplink.
3. Clone the repo, or download (preferably) [latest release](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/releases/latest), uncompress it and navigate to the directory with the `docker-compose.yml` file.
4. Edit the `docker-compose.yml` file and specify connection details to the MQTT server there too.
5. In your terminal, run `docker-compose up` (for this, you need Docker installed).

### Use with BLE (Bluetooth Low Energy)

You can connect to your Meshtastic device via BLE, which is useful if you don't want to use MQTT, Serial, or TCP. This method is tested on Linux (outside Docker), but may work on other platforms as well.

#### Pair your device

Open a terminal and use `bluetoothctl` to pair with your Meshtastic device:

```bash
bluetoothctl
[bluetooth]# power on
[bluetooth]# scan on
[bluetooth]# pair AA:BB:CC:DD:EE:FF
# Follow prompts to enter the passkey if requested
[bluetooth]# disconnect AA:BB:CC:DD:EE:FF
```

- Replace `AA:BB:CC:DD:EE:FF` with your device's MAC address (find it by name while scanning).
- Make sure to **disconnect** after pairing. The exporter (and the Meshtastic CLI) need to manage the connection themselves.

#### Test with Meshtastic CLI

Verify BLE connectivity with the Meshtastic CLI:

```bash
meshtastic -b AA:BB:CC:DD:EE:FF --nodes
```

If this works, you’re ready to use the exporter.

#### Run the exporter

Set the required environment variables and run the exporter:

```bash
MESHTASTIC_INTERFACE=BLE INTERFACE_BLE_ADDR=AA:BB:CC:DD:EE:FF meshtastic-prometheus-exporter
```

### Use with Serial

1. Connect your Meshtastic device to your computer via a serial interface (e.g., USB).
2. Clone the repo, or download (preferably) [latest release](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/releases/latest), uncompress it and navigate to the directory with the `docker-compose.yml` file.
3. Edit the `docker-compose.yml` file and set `MESHTASTIC_INTERFACE` to `SERIAL` and optionally specify the serial device path.
4. In your terminal, run `docker-compose up` (for this, you need Docker installed).

### Use with TCP

1. Ensure your Meshtastic device is accessible over a TCP interface.
2. Clone the repo, or download (preferably) [latest release](https://github.com/artiommocrenco/meshtastic-prometheus-exporter/releases/latest), uncompress it and navigate to the directory with the `docker-compose.yml` file.
3. Edit the `docker-compose.yml` file and set `MESHTASTIC_INTERFACE` to `TCP` and specify the TCP address and port of your device.
4. In your terminal, run `docker-compose up` (for this, you need Docker installed).

## Accessing Grafana

In your web browser, navigate to http://localhost:3000/dashboards and authenticate using default Grafana credentials (username `admin`, password `admin`).

## Installation using pipx

If you prefer to install the exporter using `pipx`, you can do so by running the following command:

```bash
pipx install meshtastic-prometheus-exporter
```

You could then run it outside docker, and configure Prometheus to scrape it:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
scrape_configs:
  - job_name: "meshtastic"
    static_configs:
      - targets: ["host.docker.internal:9464"]
```

## Installation using helm

Coming soon.

## Known limitations

* Running two exporters for the same meshtastic network that write to the same Prometheus is not supported
* While mostly reporting useful information, Grafana dashboards do contain mistakes in some of the visualizations
* Using TLS for MQTT on meshtastic side may be problematic for performance and reliability (third-party issue)
* Exception handling & code quality need improvement

## Contributing

Please feel free to contribute
