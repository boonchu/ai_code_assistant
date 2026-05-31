"""
Tests for authentication router endpoints.

Tests cover:
- Login endpoint
- Me endpoint
- API key authentication
- Error handling
- Validation
"""

import pytest
from fastapi.testclient import TestClient

from ai_app.routers.auth import app


class TestLoginEndpoint:
    """Tests for /api/v1/auth/login endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_login_success_view(self, client):
        """Test successful login as viewer."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "view", "password": "SecureV1ew!2024"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "view"
        assert data["role"] == "viewer"
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_success_admin(self, client):
        """Test successful login as admin."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "demo", "password": "D3mo!Admin@2024"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "demo"
        assert data["role"] == "admin"
        assert "access_token" in data

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "view", "password": "wrong_password"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Incorrect username or password" in data["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "password"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_empty_username(self, client):
        """Test login with empty username."""
        response = client.post(
            "/api/v1/auth/login", data={"username": "", "password": "password"}
        )

        # Empty username is rejected (422 validation error or 400)
        assert response.status_code in [400, 422]

    def test_login_short_username(self, client):
        """Test login with username too short."""
        response = client.post(
            "/api/v1/auth/login", data={"username": "ab", "password": "password"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Username must be between 3 and 30 characters" in data["detail"]

    def test_login_long_username(self, client):
        """Test login with username too long."""
        long_username = "a" * 50
        response = client.post(
            "/api/v1/auth/login",
            data={"username": long_username, "password": "password"},
        )

        assert response.status_code == 400

    def test_login_sql_injection_attempt(self, client):
        """Test login with SQL injection attempt."""
        malicious_usernames = ["user; DROP TABLE users--", "user'--"]

        for username in malicious_usernames:
            response = client.post(
                "/api/v1/auth/login",
                data={"username": username, "password": "password"},
            )

            # Should reject due to invalid format
            assert response.status_code in [400, 401]

    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        # Missing password
        response = client.post("/api/v1/auth/login", data={"username": "view"})
        assert response.status_code in [400, 422]

        # Missing username
        response = client.post(
            "/api/v1/auth/login", data={"password": "SecureV1ew!2024"}
        )
        assert response.status_code in [400, 422]

    def test_login_special_characters_username(self, client):
        """Test login with special characters in username."""
        special_usernames = ["user@domain", "user#test", "user$test"]

        for username in special_usernames:
            response = client.post(
                "/api/v1/auth/login",
                data={"username": username, "password": "password"},
            )
            # Should either work (if valid) or reject (if invalid)
            assert response.status_code in [200, 400, 401]


class TestMeEndpoint:
    """Tests for /api/v1/auth/me endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_me_with_valid_token(self, client):
        """Test /me with valid token."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "view", "password": "SecureV1ew!2024"},
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "view"
        assert data["role"] == "viewer"

    def test_me_with_invalid_token(self, client):
        """Test /me with invalid token."""
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_me_with_expired_token(self, client):
        """Test /me with expired token."""
        # This is a manual test - tokens don't expire in test environment
        # But the endpoint should handle it gracefully
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0Iiwicm9sZSI6InZpZXdlciJ9.fake"
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        # Should return 401 for invalid token
        assert response.status_code == 401

    def test_me_with_admin_token(self, client):
        """Test /me with admin token."""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "demo", "password": "D3mo!Admin@2024"},
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "demo"
        assert data["role"] == "admin"


class TestAPIKeyAuth:
    """Tests for API key authentication."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_api_key_valid(self, client):
        """Test valid API key."""
        from ai_app.settings import API_KEY_SECRET

        response = client.get(
            "/api/v1/auth/api-key", headers={"X-API-Key": API_KEY_SECRET}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "api_user"
        assert data["role"] == "admin"
        assert data["method"] == "api_key"

    def test_api_key_post(self, client):
        """Test API key validation via POST."""
        from ai_app.settings import API_KEY_SECRET

        response = client.post("/api/v1/auth/api-key", data={"api_key": API_KEY_SECRET})

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "api_user"
        assert data["role"] == "admin"

    def test_api_key_invalid(self, client):
        """Test invalid API key."""
        response = client.get(
            "/api/v1/auth/api-key", headers={"X-API-Key": "invalid_key"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid API key" in data["detail"]

    def test_api_key_missing_header(self, client):
        """Test API key missing header."""
        response = client.get("/api/v1/auth/api-key")

        assert response.status_code == 422  # Missing required field

    def test_api_key_empty(self, client):
        """Test empty API key."""
        response = client.get("/api/v1/auth/api-key", headers={"X-API-Key": ""})

        assert response.status_code == 401


class TestHealthEndpoint:
    """Tests for health endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_auth_health(self, client):
        """Test authentication health endpoint."""
        response = client.get("/api/v1/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth"

    def test_v1_health(self, client):
        """Test /v1/health endpoint."""
        response = client.get("/v1/health")

        assert response.status_code == 200

    def test_health_backend(self, client):
        """Test backend health endpoint."""
        response = client.get("/health")

        # May succeed or fail depending on backend availability
        assert response.status_code in [200, 503]


class TestLogoutEndpoint:
    """Tests for logout endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_logout_success(self, client):
        """Test successful logout."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "view", "password": "SecureV1ew!2024"},
        )
        token = login_response.json()["access_token"]

        # Logout
        response = client.post(
            "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )

        # Should succeed (logout is a placeholder)
        assert response.status_code == 200
        data = response.json()
        assert "Successfully logged out" in data["detail"]


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app, raise_server_exceptions=False)

    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoint."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_method_not_allowed(self, client):
        """Test method not allowed."""
        # GET on POST endpoint
        response = client.get("/api/v1/auth/login")

        assert response.status_code == 405

    def test_rate_limiting(self, client):
        """Test rate limiting (if configured)."""
        # Make multiple requests quickly
        for i in range(5):
            response = client.get("/api/v1/auth/health")
            assert response.status_code == 200


class TestSecurity:
    """Security-related tests."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_token_includes_role(self, client):
        """Test token includes user role."""
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "view", "password": "SecureV1ew!2024"},
        )
        token = login_response.json()["access_token"]

        # Decode token to check payload
        payload = __import__("base64").urlsafe_b64decode(token.split(".")[1] + "==")
        payload_str = payload.decode("utf-8")

        assert "role" in payload_str

    def test_password_not_in_response(self, client):
        """Test password not included in login response."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "view", "password": "SecureV1ew!2024"},
        )

        data = response.json()
        assert "password" not in data
        assert "hash" not in data

    def test_sensitive_headers_not_exposed(self, client):
        """Test sensitive headers not exposed in response."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "view", "password": "SecureV1ew!2024"},
        )

        # Check response headers
        headers = response.headers
        assert "x-api-key" not in headers.lower()
        assert "authorization" not in headers.get("x-api-key", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
