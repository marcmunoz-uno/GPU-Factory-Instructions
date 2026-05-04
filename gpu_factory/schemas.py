from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, field_validator


class GpuProbeJob(BaseModel):
    type: Literal["gpu_probe"]


class PythonProbeJob(BaseModel):
    type: Literal["python_probe"]
    venv_path: str | None = None


class RunContainerJob(BaseModel):
    type: Literal["run_container"]
    image: str
    args: list[str] = Field(default_factory=list)
    gpu: bool = True
    workdir: str | None = None
    env: dict[str, str] = Field(default_factory=dict)

    @field_validator("args")
    @classmethod
    def validate_args(cls, value: list[str]) -> list[str]:
        for item in value:
            if not item.strip():
                raise ValueError("container args may not be empty strings")
        return value


JobRequest = Annotated[
    Union[GpuProbeJob, PythonProbeJob, RunContainerJob],
    Field(discriminator="type"),
]


class JobAccepted(BaseModel):
    job_id: str
    queue: str
    type: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    result: dict | None = None
    error: str | None = None
