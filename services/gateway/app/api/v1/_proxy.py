from __future__ import annotations

from typing import Iterable

import httpx
from fastapi import HTTPException, Request, Response

from app.core.config import settings

HOP_BY_HOP_HEADERS = {
    "host",
    "content-length",
    "connection",
    "accept-encoding",
}


def build_forward_headers(request: Request, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key, value in request.headers.items():
        if key.lower() in HOP_BY_HOP_HEADERS:
            continue
        headers[key] = value
    if hasattr(request.state, "request_id"):
        headers["X-Request-ID"] = request.state.request_id
    if extra_headers:
        headers.update(extra_headers)
    return headers


async def proxy_request(
    request: Request,
    service_url: str,
    upstream_path: str,
    extra_headers: dict[str, str] | None = None,
) -> Response:
    url = f"{service_url.rstrip('/')}" + upstream_path
    content = await request.body()
    headers = build_forward_headers(request, extra_headers=extra_headers)

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            upstream_response = await client.request(
                request.method,
                url,
                params=request.query_params,
                content=content,
                headers=headers,
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Upstream service unavailable: {exc}") from exc

    response_headers = {
        key: value
        for key, value in upstream_response.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
