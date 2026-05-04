from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _load_token() -> str:
    token = os.environ.get("GPU_FACTORY_API_TOKEN", "").strip()
    token_file = os.environ.get("GPU_FACTORY_API_TOKEN_FILE", "").strip()
    if token:
        return token
    if token_file:
        with open(token_file, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    return ""


@dataclass(frozen=True)
class Settings:
    api_token: str
    redis_url: str
    queue_name: str
    chroma_url: str
    allowed_image_prefixes: tuple[str, ...]
    max_container_seconds: int
    max_container_args: int


def load_settings() -> Settings:
    token = _load_token()
    if not token:
        raise RuntimeError("GPU_FACTORY_API_TOKEN or GPU_FACTORY_API_TOKEN_FILE must be set")

    return Settings(
        api_token=token,
        redis_url=os.environ.get("GPU_FACTORY_REDIS_URL", "redis://localhost:6379/0"),
        queue_name=os.environ.get("GPU_FACTORY_QUEUE_NAME", "gpu-factory"),
        chroma_url=os.environ.get("GPU_FACTORY_CHROMA_URL", "http://localhost:8001"),
        allowed_image_prefixes=tuple(
            _split_csv(
                os.environ.get(
                    "GPU_FACTORY_ALLOWED_IMAGE_PREFIXES",
                    "nvcr.io/nvidia/cuda:,nvcr.io/nvidia/pytorch:,python:",
                )
            )
        ),
        max_container_seconds=int(os.environ.get("GPU_FACTORY_MAX_CONTAINER_SECONDS", "3600")),
        max_container_args=int(os.environ.get("GPU_FACTORY_MAX_CONTAINER_ARGS", "32")),
    )


settings = load_settings()
