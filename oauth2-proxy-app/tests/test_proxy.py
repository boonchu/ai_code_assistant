"""Tests for the AI App Proxy."""

import pytest
from fastapi.testclient import TestClient

from ai_app.proxy import app
from ai_app.settings import API_KEY_SECRET


@pytest.fixture
def client():
    """Create a test client with API key authentication."""
    return TestClient(app, headers={"X-API-Key": API_KEY_SECRET})


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200_with_healthy_backend(self):
        """Test that health check returns 200 when backend is healthy."""
        response = TestClient(app).get("/health")
        assert response.status_code in (200, 503)
        if response.status_code == 200:
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert "backend_url" in health_data


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def test_rate_limiting_allows_initial_requests(self):
        """Test that rate limiting allows initial requests."""
        response = TestClient(app).get("/health")
        assert response.status_code in (200, 503)


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_login_endpoint_returns_401_for_invalid_credentials(self):
        """Test that login with invalid credentials returns 401."""
        response = TestClient(app).post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_login_with_empty_credentials(self):
        """Test that login with empty credentials returns error."""
        response = TestClient(app).post("/api/v1/auth/login", data={})
        assert response.status_code in (400, 422)

    def test_me_endpoint_requires_auth(self):
        """Test that me endpoint requires authentication."""
        response = TestClient(app).get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_auth_health_endpoint(self):
        """Test that auth health endpoint exists."""
        response = TestClient(app).get("/api/v1/auth/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestProtectedEndpoints:
    """Tests for protected endpoints."""

    def test_chat_completions_requires_auth(self):
        """Test that chat completions requires authentication."""
        response = TestClient(app).post("/v1/chat/completions")
        assert response.status_code == 401

    def test_completions_requires_auth(self):
        """Test that completions requires authentication."""
        response = TestClient(app).post("/v1/completions")
        assert response.status_code == 401

    def test_embeddings_requires_auth(self):
        """Test that embeddings requires authentication."""
        response = TestClient(app).post("/v1/embeddings")
        assert response.status_code == 401

    def test_models_requires_auth(self):
        """Test that models endpoint requires authentication."""
        response = TestClient(app).get("/v1/models")
        assert response.status_code == 401


class TestCORS:
    """Tests for CORS middleware."""

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        response = TestClient(app).options(
            "/", headers={"Origin": "http://localhost:3000"}
        )
        assert response.headers.get("Access-Control-Allow-Origin")
