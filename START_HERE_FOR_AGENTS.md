# Start Here For Agents

This repo is the safer way to use the DGX for GPU work.

## Use This Repo When

- you need to submit GPU work through an API
- you want queueing and typed jobs
- you want Docker-first execution without handing out raw shell access

## What Is Already Proven

- API health works
- bearer-token auth works
- queue submission works
- worker execution works
- `gpu_probe` finished successfully through the live stack

## Read In This Order

1. `README.md`
2. `DEPLOYMENT.md`
3. `gpu_factory/schemas.py`
4. `gpu_factory/worker/runner.py`

## Fastest Safe Usage

Load the local token safely:

```bash
TOKEN=$(cat /home/mxrcmunoz/Desktop/GPU-Factory-Instructions/.secrets/api_token)
```

Health:

```bash
curl http://127.0.0.1:8080/health
```

Submit GPU probe:

```bash
curl -X POST http://127.0.0.1:8080/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"gpu_probe"}'
```

Check job status:

```bash
curl http://127.0.0.1:8080/jobs/<job_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Preferred Job Order

1. `gpu_probe`
2. `python_probe`
3. `run_container`

## Rules

- Prefer typed jobs over direct host commands
- Prefer `run_container` for isolated GPU workloads
- Do not add raw shell execution endpoints
- Do not expose the API publicly
