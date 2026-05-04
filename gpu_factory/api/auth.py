from __future__ import annotations

from fastapi import Header, HTTPException, status

from gpu_factory.config import settings


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.api_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid token")
