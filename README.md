# GPU Factory Instructions

Safer DGX-local control plane for AI agents that need GPU access.

This package turns the useful premise of "submit work to the DGX over an API" into a tighter stack:

- FastAPI control API
- Redis queue
- RQ worker
- Docker-first GPU execution
- typed jobs instead of raw shell commands
- bearer token auth
- local MCP server for MCP-capable agents
- optional ChromaDB sidecar for retrieval workloads

## Why This Exists

Your DGX is now proven to support:

- native CUDA userland
- PyTorch CUDA on `NVIDIA GB10`
- CuPy CUDA on `NVIDIA GB10`
- Docker GPU runtime with the NVIDIA CUDA 13.0.1 container

This stack gives agents a stable way to ask the DGX to do GPU work without giving them an unauthenticated shell wrapper.

## Core Safety Properties

- No `shell=True`
- No generic "run whatever command" endpoint
- Jobs are validated with explicit schemas
- Container execution is allowlisted by image prefix
- API requires a bearer token
- Worker and API are separate processes

## Job Types

- `gpu_probe`
  - runs GPU visibility checks on the host
- `run_container`
  - runs an allowlisted Docker image with structured args
- `python_probe`
  - validates the local Python CUDA environment

## Quick Start

1. Copy environment variables:

```bash
cp .env.example .env
./scripts/bootstrap-secrets.sh
```

2. The API token is stored in:

```text
.secrets/api_token
```

and `.env` points at it through `GPU_FACTORY_API_TOKEN_FILE`.

3. Start Redis and Chroma:

```bash
docker compose up -d redis chromadb
```

4. Create the Python env:

```bash
python3 /tmp/virtualenv.pyz .venv
source .venv/bin/activate
pip install -e .
```

5. Run the API:

```bash
./scripts/start-api.sh
```

6. Run the worker:

```bash
./scripts/start-worker.sh
```

7. Run the MCP server:

```bash
./scripts/start-mcp.sh
```

## Example Requests

Health:

```bash
curl http://localhost:8080/health
```

GPU probe:

```bash
curl -X POST http://localhost:8080/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"gpu_probe"}'
```

Container GPU validation:

```bash
curl -X POST http://localhost:8080/jobs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type":"run_container",
    "image":"nvcr.io/nvidia/cuda:13.0.1-devel-ubuntu24.04",
    "args":["nvidia-smi"],
    "gpu":true
  }'
```

## Files

- `START_HERE_FOR_AGENTS.md` - single-entrypoint guide for agents using this control plane
- `scripts/bootstrap-secrets.sh` - create and permission-lock the API token file
- `scripts/start-api.sh` - launch wrapper for the API
- `scripts/start-worker.sh` - launch wrapper for the worker
- `scripts/start-mcp.sh` - launch wrapper for the local MCP server
- `scripts/install-user-services.sh` - install user-level systemd units
- `gpu_factory/mcp/server.py` - stdio MCP adapter over the local GPU Factory API
- `gpu_factory/api/` - API server
- `gpu_factory/worker/` - typed job execution
- `compose.yaml` - Redis and Chroma sidecars
- `Dockerfile` - app container for API/worker
- `.env.example` - required settings
- `DEPLOYMENT.md` - DGX-specific run and service guidance

## Recommended Next Hardening

- Put the API behind Tailscale, Caddy, or another internal-only gateway
- Rotate API tokens
- Add audit logging to a file or SQLite
- Add explicit job quotas and timeouts per job type

## Service Model

- `gpu-factory-api.service` should run persistently
- `gpu-factory-worker.service` should run persistently
- the MCP server should **not** run as a persistent service
- MCP clients should spawn `scripts/start-mcp.sh` on demand over stdio
