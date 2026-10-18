#!/bin/bash

# Start Prometheus
prometheus --config.file=prometheus.yml \
  --storage.tsdb.path=./prometheus-data \
  --web.listen-address=:9090 &

echo "Prometheus started on http://localhost:9090"

# Start Grafana
grafana server \
  --homepath=/opt/homebrew/opt/grafana/share/grafana \
  --config=/opt/homebrew/etc/grafana/grafana.ini &

echo "Grafana started on http://localhost:3000"
echo "Default login: admin/admin"