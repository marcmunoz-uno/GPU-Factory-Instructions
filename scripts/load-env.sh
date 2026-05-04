#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [ -f "${ROOT_DIR}/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

if [ -n "${GPU_FACTORY_API_TOKEN_FILE:-}" ] && [ -f "${GPU_FACTORY_API_TOKEN_FILE}" ]; then
  export GPU_FACTORY_API_TOKEN="$(cat "${GPU_FACTORY_API_TOKEN_FILE}")"
fi

export PYTHONUNBUFFERED=1
