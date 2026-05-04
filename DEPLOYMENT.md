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
python3 /tmp/virtualenv.pyz .venv
source .venv/bin/activate
pip install -e .
docker compose up -d redis chromadb
export $(grep -v '^#' .env | xargs)
uvicorn gpu_factory.api.main:app --host 0.0.0.0 --port 8080
```

In a second shell:

```bash
cd /home/mxrcmunoz/Desktop/GPU-Factory-Instructions
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
rq worker gpu-factory
```

## Recommended Internal Exposure

- bind to Tailscale or another internal interface
- do not expose port `8080` publicly
- rotate `GPU_FACTORY_API_TOKEN`

## Example Worker/API Services

API service:

```ini
[Unit]
Description=GPU Factory API
After=network.target docker.service

[Service]
WorkingDirectory=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions
EnvironmentFile=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.env
ExecStart=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.venv/bin/uvicorn gpu_factory.api.main:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

Worker service:

```ini
[Unit]
Description=GPU Factory Worker
After=network.target docker.service

[Service]
WorkingDirectory=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions
EnvironmentFile=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.env
ExecStart=/home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.venv/bin/rq worker gpu-factory
Restart=always

[Install]
WantedBy=multi-user.target
```

## Validation Flow

1. Submit `gpu_probe`
2. Submit `python_probe` with the DGX CUDA venv path if needed
3. Submit `run_container` against `nvcr.io/nvidia/cuda:13.0.1-devel-ubuntu24.04`

If all three pass, the stack is functioning as intended.
