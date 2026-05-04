from __future__ import annotations

from gpu_factory.schemas import GpuProbeJob, PythonProbeJob, RunContainerJob
from gpu_factory.worker.runner import run_container, run_gpu_probe, run_python_probe


def run_job(payload: dict) -> dict:
    job_type = payload.get("type")

    if job_type == "gpu_probe":
        job = GpuProbeJob.model_validate(payload)
        return {"type": job.type, "result": run_gpu_probe()}

    if job_type == "python_probe":
        job = PythonProbeJob.model_validate(payload)
        return {"type": job.type, "result": run_python_probe(job.venv_path)}

    if job_type == "run_container":
        job = RunContainerJob.model_validate(payload)
        return {
            "type": job.type,
            "result": run_container(
                image=job.image,
                args=job.args,
                gpu=job.gpu,
                workdir=job.workdir,
                env=job.env,
            ),
        }

    raise ValueError(f"unsupported job type: {job_type}")
