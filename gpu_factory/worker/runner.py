from __future__ import annotations

import os
import subprocess
from typing import Sequence

from gpu_factory.config import settings


def _trim(text: str, limit: int = 50000) -> str:
    return text[-limit:]


def run_subprocess(argv: Sequence[str], *, timeout: int | None = None, env: dict[str, str] | None = None) -> dict:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    proc = subprocess.run(
        list(argv),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=merged_env,
        check=False,
    )
    return {
        "argv": list(argv),
        "returncode": proc.returncode,
        "stdout": _trim(proc.stdout),
        "stderr": _trim(proc.stderr),
    }


def run_gpu_probe() -> dict:
    commands = [
        ["bash", "-lc", "command -v nvidia-smi && nvidia-smi -L"],
        ["bash", "-lc", "python3 - <<'PY'\nimport ctypes\nfor lib in ['libcuda.so.1','libcudart.so.13','libcublas.so.13']:\n    try:\n        ctypes.CDLL(lib)\n        print(lib, 'OK')\n    except Exception as exc:\n        print(lib, 'FAIL', exc)\nPY"],
    ]
    return {"checks": [run_subprocess(cmd, timeout=120) for cmd in commands]}


def run_python_probe(venv_path: str | None) -> dict:
    python_bin = "python3"
    if venv_path:
        python_bin = os.path.join(venv_path, "bin", "python")
    code = (
        "import json\n"
        "report={}\n"
        "try:\n"
        " import torch\n"
        " report['torch']={'installed':True,'cuda_available':torch.cuda.is_available(),"
        "'device_count':torch.cuda.device_count(),"
        "'devices':[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]}\n"
        "except Exception as exc:\n"
        " report['torch']={'installed':False,'error':str(exc)}\n"
        "try:\n"
        " import cupy\n"
        " count=cupy.cuda.runtime.getDeviceCount()\n"
        " report['cupy']={'installed':True,'device_count':count}\n"
        "except Exception as exc:\n"
        " report['cupy']={'installed':False,'error':str(exc)}\n"
        "print(json.dumps(report))\n"
    )
    return run_subprocess([python_bin, "-c", code], timeout=300)


def run_container(image: str, args: list[str], gpu: bool, workdir: str | None, env: dict[str, str]) -> dict:
    if len(args) > settings.max_container_args:
        raise ValueError("too many container args")
    if not any(image.startswith(prefix) for prefix in settings.allowed_image_prefixes):
        raise ValueError(f"image '{image}' is not in the allowlist")

    argv = ["docker", "run", "--rm"]
    if gpu:
        argv.extend(["--gpus=all"])
    if workdir:
        argv.extend(["-w", workdir])
    for key, value in env.items():
        argv.extend(["-e", f"{key}={value}"])
    argv.append(image)
    argv.extend(args)
    return run_subprocess(argv, timeout=settings.max_container_seconds)
