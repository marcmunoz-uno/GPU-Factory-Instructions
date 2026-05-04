#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="${HOME}/.config/systemd/user"

mkdir -p "${UNIT_DIR}"
cp "${ROOT_DIR}/deploy/systemd/gpu-factory-api.service" "${UNIT_DIR}/"
cp "${ROOT_DIR}/deploy/systemd/gpu-factory-worker.service" "${UNIT_DIR}/"

echo "Installed user units to ${UNIT_DIR}"
echo "Next run in a real host shell:"
echo "  systemctl --user daemon-reload"
echo "  systemctl --user enable --now gpu-factory-api.service gpu-factory-worker.service"
