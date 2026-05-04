# Deployment

## DGX Notes

This package assumes the DGX host already has:

- native CUDA userland working
- Docker GPU runtime working or nearly working
- Python 3.12 available

Those were validated separately on this machine.

## Minimal Native Run

```bash
cd /home/mxrcmunoz/Desktop/GPU-Factory-Instructions
cp .env.example .env
./scripts/bootstrap-secrets.sh
python3 /tmp/virtualenv.pyz .venv
source .venv/bin/activate
pip install -e .
docker compose up -d redis chromadb
./scripts/start-api.sh
```

In a second shell:

```bash
cd /home/mxrcmunoz/Desktop/GPU-Factory-Instructions
./scripts/start-worker.sh
```

## Recommended Internal Exposure

- bind to Tailscale or another internal interface
- do not expose port `8080` publicly
- rotate `GPU_FACTORY_API_TOKEN`

## User-Level Persistent Services

Install units:

```bash
./scripts/install-user-services.sh
systemctl --user daemon-reload
systemctl --user enable --now gpu-factory-api.service gpu-factory-worker.service
```

Unit files live in:

```text
deploy/systemd/gpu-factory-api.service
deploy/systemd/gpu-factory-worker.service
```

The current tool runtime could not execute `systemctl`, so the package now includes the exact units and installer, but final enablement must be run from a real host shell.

## Secret Handling

- `.env` is now meant to reference a file-based token, not store the token inline
- `.secrets/api_token` should remain mode `600`
- `.secrets/` should remain mode `700`

## Validation Flow

1. Submit `gpu_probe`
2. Submit `python_probe` with the DGX CUDA venv path if needed
3. Submit `run_container` against `nvcr.io/nvidia/cuda:13.0.1-devel-ubuntu24.04`

If all three pass, the stack is functioning as intended.
