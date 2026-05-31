"""Pytest configuration and fixtures."""

import pytest
import time

from ai_app.settings import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW
from ai_app.proxy import request_counts


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset rate limiting state before each test."""
    # Clear rate limit data
    current_time = time.time()
    stale_keys = [
        key
        for key, value in request_counts.items()
        if current_time - value >= RATE_LIMIT_WINDOW
    ]
    for key in stale_keys:
        del request_counts[key]

    # Reset counters
    for key in list(request_counts.keys()):
        request_counts[key] = 0

    yield

    # Ensure clean state after test
    current_time = time.time()
    for key in list(request_counts.keys()):
        if current_time - request_counts.get(key, 0) >= RATE_LIMIT_WINDOW:
            del request_counts[key]


@pytest.fixture
async def mock_healthy_client(monkeypatch):
    """Create a healthy mock backend client."""
    import httpx

    async def handler(request):
        if "/health" in request.url.path:
            return httpx.Response(200, text='{"status":"ok"}')
        if "chat/completions" in request.url.path:
            return httpx.Response(200, json={"choices": []})
        if "completions" in request.url.path:
            return httpx.Response(200, json={"choices": []})
        if "embeddings" in request.url.path:
            return httpx.Response(200, json={"embedding": [0.0] * 512})
        if "/v1/models" in request.url.path:
            if request.method == "GET":
                return httpx.Response(
                    200,
                    json=[
                        {"id": "test-model", "object": "model", "created": 1234567890}
                    ],
                )
            return httpx.Response(404, json={"detail": "Not found"})
        return httpx.Response(404, json={"detail": "Not found"})

    mock_transport = httpx.MockTransport(handler)
    mock_client = httpx.AsyncClient(
        base_url="http://localhost:8080", transport=mock_transport
    )
    monkeypatch.setattr("httpx.AsyncClient", lambda *a, **k: mock_client)
    yield mock_client
    await mock_client.aclose()


@pytest.fixture
async def mock_unhealthy_client(monkeypatch):
    """Create an unhealthy mock backend client."""
    import httpx

    async def handler(request):
        if "/health" in request.url.path:
            return httpx.Response(503, json={"error": "backend unavailable"})
        return httpx.Response(500, json={"error": "backend error"})

    mock_transport = httpx.MockTransport(handler)
    mock_client = httpx.AsyncClient(
        base_url="http://localhost:8080", transport=mock_transport
    )
    monkeypatch.setattr("httpx.AsyncClient", lambda *a, **k: mock_client)
    yield mock_client
    await mock_client.aclose()
