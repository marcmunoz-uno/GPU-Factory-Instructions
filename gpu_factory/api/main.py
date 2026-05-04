from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from rq.job import Job

from gpu_factory.api.auth import require_bearer_token
from gpu_factory.config import settings
from gpu_factory.queue import get_queue, get_redis
from gpu_factory.schemas import JobAccepted, JobRequest, JobStatus

app = FastAPI(title="GPU Factory Instructions", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "queue": settings.queue_name,
        "chroma_url": settings.chroma_url,
    }


@app.post("/jobs", response_model=JobAccepted, dependencies=[Depends(require_bearer_token)])
def submit_job(request: JobRequest) -> JobAccepted:
    queue = get_queue()
    payload = request.model_dump()
    job = queue.enqueue(
        "gpu_factory.worker.jobs.run_job",
        payload,
        job_timeout=settings.max_container_seconds,
    )
    return JobAccepted(job_id=job.id, queue=settings.queue_name, type=request.type)


@app.get("/jobs/{job_id}", response_model=JobStatus, dependencies=[Depends(require_bearer_token)])
def get_job_status(job_id: str) -> JobStatus:
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"job not found: {exc}") from exc

    result = job.result if isinstance(job.result, dict) else None
    error = str(job.exc_info) if job.exc_info else None
    return JobStatus(job_id=job.id, status=job.get_status(), result=result, error=error)
