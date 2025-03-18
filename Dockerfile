FROM python:3.13-slim
WORKDIR /app
COPY dist/meshtastic_prometheus_exporter*.whl /app
RUN pip install --no-cache-dir /app/meshtastic_prometheus_exporter*.whl
ENTRYPOINT ["meshtastic-prometheus-exporter"]