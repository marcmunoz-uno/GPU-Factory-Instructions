from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import httpx


ROOT = Path("/home/mxrcmunoz/Desktop/GPU-Factory-Instructions")
ENV_FILE = ROOT / ".env"
TOKEN_FILE = ROOT / ".secrets" / "api_token"
API_BASE = "http://127.0.0.1:8080"


def load_token() -> str:
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("GPU_FACTORY_API_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("No GPU Factory API token found")


TOKEN = load_token()


TOOLS: list[dict[str, Any]] = [
    {
        "name": "gpu_probe",
        "description": "Submit a GPU visibility probe job to the local DGX GPU Factory.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "python_probe",
        "description": "Validate PyTorch/CuPy visibility in a Python environment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "venv_path": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "run_cuda_container",
        "description": "Run an allowlisted Docker image via GPU Factory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string"},
                "args": {"type": "array", "items": {"type": "string"}},
                "gpu": {"type": "boolean"},
                "workdir": {"type": "string"},
                "env": {"type": "object", "additionalProperties": {"type": "string"}},
            },
            "required": ["image", "args"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_job_status",
        "description": "Fetch the status/result of a previously submitted GPU Factory job.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string"},
            },
            "required": ["job_id"],
            "additionalProperties": False,
        },
    },
]


def mcp_result(payload: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, indent=2),
            }
        ]
    }


def api_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }


def submit_job(payload: dict[str, Any]) -> dict[str, Any]:
    response = httpx.post(f"{API_BASE}/jobs", headers=api_headers(), json=payload, timeout=20.0)
    response.raise_for_status()
    return response.json()


def get_status(job_id: str) -> dict[str, Any]:
    response = httpx.get(f"{API_BASE}/jobs/{job_id}", headers=api_headers(), timeout=20.0)
    response.raise_for_status()
    return response.json()


def handle_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "gpu_probe":
        return mcp_result(submit_job({"type": "gpu_probe"}))
    if name == "python_probe":
        payload: dict[str, Any] = {"type": "python_probe"}
        if "venv_path" in arguments and arguments["venv_path"]:
            payload["venv_path"] = arguments["venv_path"]
        return mcp_result(submit_job(payload))
    if name == "run_cuda_container":
        payload = {
            "type": "run_container",
            "image": arguments["image"],
            "args": arguments.get("args", []),
            "gpu": arguments.get("gpu", True),
            "workdir": arguments.get("workdir"),
            "env": arguments.get("env", {}),
        }
        return mcp_result(submit_job(payload))
    if name == "get_job_status":
        return mcp_result(get_status(arguments["job_id"]))
    raise ValueError(f"Unknown tool: {name}")


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "gpu-factory-mcp",
                    "version": "0.1.0",
                },
                "capabilities": {
                    "tools": {},
                },
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS,
            },
        }

    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {}) or {}
        try:
            result = handle_tool(name, arguments)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": str(exc),
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}",
        },
    }


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        request = json.loads(line)
        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
