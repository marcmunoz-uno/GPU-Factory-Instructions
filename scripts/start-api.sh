#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/load-env.sh"
# shellcheck disable=SC1091
source "${ROOT_DIR}/.venv/bin/activate"

exec uvicorn gpu_factory.api.main:app --host 0.0.0.0 --port 8080
