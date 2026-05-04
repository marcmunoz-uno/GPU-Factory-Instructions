#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECRETS_DIR="${ROOT_DIR}/.secrets"
TOKEN_FILE="${SECRETS_DIR}/api_token"
ENV_FILE="${ROOT_DIR}/.env"

mkdir -p "${SECRETS_DIR}"
chmod 700 "${SECRETS_DIR}"

CURRENT_INLINE_TOKEN=""
if [ -f "${ENV_FILE}" ]; then
  while IFS= read -r line; do
    case "${line}" in
      GPU_FACTORY_API_TOKEN=*)
        CURRENT_INLINE_TOKEN="${line#GPU_FACTORY_API_TOKEN=}"
        ;;
    esac
  done < "${ENV_FILE}"
fi

if [ ! -f "${TOKEN_FILE}" ]; then
  if [ -n "${CURRENT_INLINE_TOKEN}" ]; then
    printf '%s\n' "${CURRENT_INLINE_TOKEN}" > "${TOKEN_FILE}"
  else
    python3 - <<'PY' > "${TOKEN_FILE}"
import secrets
print(secrets.token_urlsafe(32))
PY
  fi
fi

chmod 600 "${TOKEN_FILE}"

if [ -f "${ENV_FILE}" ]; then
  python3 - <<'PY'
from pathlib import Path
env_path = Path("/home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.env")
lines = env_path.read_text().splitlines()
updated = []
seen_token = False
seen_file = False
for line in lines:
    if line.startswith("GPU_FACTORY_API_TOKEN="):
        updated.append("GPU_FACTORY_API_TOKEN=")
        seen_token = True
    elif line.startswith("GPU_FACTORY_API_TOKEN_FILE="):
        updated.append("GPU_FACTORY_API_TOKEN_FILE=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.secrets/api_token")
        seen_file = True
    else:
        updated.append(line)
if not seen_token:
    updated.append("GPU_FACTORY_API_TOKEN=")
if not seen_file:
    updated.append("GPU_FACTORY_API_TOKEN_FILE=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.secrets/api_token")
env_path.write_text("\n".join(updated) + "\n")
PY
fi

chmod 600 "${ENV_FILE}" 2>/dev/null || true
echo "Secrets bootstrapped at ${TOKEN_FILE}"
