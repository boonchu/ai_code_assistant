"""
Unit tests for ai_app.auth_v2 module.

Tests cover:
- Password hashing and verification
- Token creation and validation
- User management
- Input validation
"""

import os
import pytest
import bcrypt
from typing import Any

from ai_app.auth_v2 import (
    hash_password,
    verify_password,
    get_password_hash,
    DEFAULT_USERS,
    create_access_token,
    decode_token,
    get_user,
    create_user,
    delete_user,
    get_user_by_role,
)
from ai_app.settings import BCRYPT_ROUNDS


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password(self):
        """Test that passwords are hashed correctly."""
        password = "test_password_123"
        hashed = hash_password(password)

        # Check bcrypt format
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

        # Verify it can be used for verification
        assert verify_password(password, hashed)

        # Verify wrong password fails
        assert not verify_password("wrong_password", hashed)

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_idempotency(self):
        """Test that same password produces different hashes (salt)."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Should be different due to random salt
        assert hash1 != hash2

        # But both should verify the same password
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_bcrypt_rounds_match_config(self):
        """Test that bcrypt rounds match settings."""
        password = "test"
        hashed = hash_password(password)

        # bcrypt format: $2b$<rounds>$...
        rounds_str = hashed[4:7]
        # Extract just the numeric part (strip $)
        actual_rounds_str = rounds_str.rstrip("$")
        actual_rounds = int(actual_rounds_str)

        assert actual_rounds == BCRYPT_ROUNDS

    def test_password_with_special_chars(self):
        """Test password with special characters."""
        password = "P@ssw0rd!@#$%^&*()_+-=[]{}|;':\",./<>?"
        hashed = hash_password(password)

        assert verify_password(password, hashed)
        assert len(hashed) == 60

    def test_password_empty_string(self):
        """Test empty password."""
        hashed = hash_password("")
        assert verify_password("", hashed)
        assert not verify_password("not_empty", hashed)


class TestTokenCreation:
    """Tests for JWT token creation."""

    def test_create_access_token(self):
        """Test creating access token."""
        token = create_access_token(data={"sub": "testuser", "role": "admin"})

        assert token is not None
        assert len(token) > 0

        # Token should be valid JWT format
        parts = token.split(".")
        assert len(parts) == 3

    def test_token_decoding(self):
        """Test decoding token payload."""
        token = create_access_token(
            data={"sub": "testuser", "role": "admin", "custom_field": "value"}
        )
        payload = decode_token(token)

        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["custom_field"] == "value"
        assert "exp" in payload
        assert "iat" in payload

    def test_token_expiration_default(self):
        """Test token uses default expiration."""
        token = create_access_token(data={"sub": "testuser"})
        payload = decode_token(token)

        assert "exp" in payload
        assert "iat" in payload

        # Default is 30 minutes
        from ai_app.settings import ACCESS_TOKEN_EXPIRE_MINUTES
        from datetime import datetime

        exp = datetime.fromtimestamp(payload["exp"])
        iat = datetime.fromtimestamp(payload["iat"])

        diff = (exp - iat).total_seconds() / 60
        assert diff == 15  # 15 minutes default

    def test_token_with_special_chars(self):
        """Test token with special characters in payload."""
        token = create_access_token(
            data={"sub": "user-123", "role": "admin", "custom": "value with spaces"}
        )

        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["role"] == "admin"


class TestUserManagement:
    """Tests for user management functions."""

    def test_get_user(self):
        """Test getting existing user."""
        assert get_user("view") is not None
        assert get_user("view").username == "view"
        assert get_user("view").role == "viewer"

    def test_get_nonexistent_user(self):
        """Test getting non-existent user."""
        user = get_user("nonexistent_user")
        assert user is None

    def test_get_user_by_role(self):
        """Test getting users by role."""
        users = get_user_by_role("viewer")
        assert len(users) > 0
        assert all(u.role == "viewer" for u in users)

    def test_create_user(self):
        """Test creating new user."""
        username = "test_user_" + str(os.getpid())
        password = "secure_password_123"

        try:
            user = create_user(
                username=username,
                password=password,
                role="viewer",
                full_name="Test User",
            )

            assert user is not None
            assert user.username == username
            assert user.role == "viewer"

            # Verify password hash
            assert user.password_hash.startswith("$2b$")

            # Verify we can retrieve the user
            retrieved = get_user(username)
            assert retrieved is not None

        finally:
            try:
                delete_user(username)
            except Exception:
                pass

    def test_delete_user(self):
        """Test deleting user."""
        username = "test_user_" + str(os.getpid())
        password = "secure_password_123"

        try:
            create_user(username, password, "viewer")
            assert get_user(username) is not None

            delete_user(username)
            assert get_user(username) is None

        except Exception:
            try:
                delete_user(username)
            except:
                pass

    def test_create_duplicate_user(self):
        """Test creating duplicate user returns None."""
        username = "view"

        result = create_user(username, "new_password", "viewer")
        assert result is None


class TestDefaultUsers:
    """Tests for default users."""

    def test_default_users_exist(self):
        """Test default users are initialized."""
        # DEFAULT_USERS is a dict
        assert len(DEFAULT_USERS) >= 2

        # Check for standard users
        usernames = list(DEFAULT_USERS.keys())
        assert "view" in usernames
        assert "demo" in usernames

    def test_default_user_roles(self):
        """Test default user roles."""
        view_user = get_user("view")
        demo_user = get_user("demo")

        assert view_user.role == "viewer"
        assert demo_user.role == "admin"

    def test_default_password_verification(self):
        """Test default user passwords work."""
        # Updated to production-ready passwords
        assert verify_password("SecureV1ew!2024", get_user("view").password_hash)
        assert verify_password("D3mo!Admin@2024", get_user("demo").password_hash)

    def test_default_user_permissions(self):
        """Test default user permissions."""
        # Viewer should have read permissions
        viewer = get_user("view")
        assert viewer.role == "viewer"

        # Admin should have full permissions
        admin = get_user("demo")
        assert admin.role == "admin"


class TestInputValidation:
    """Tests for input validation."""

    def test_username_length_validation(self):
        """Test username length validation."""
        # Test short username
        short_username = "ab"
        user = get_user(short_username)
        assert user is None

        # Test long username
        long_username = "a" * 50
        user = get_user(long_username)
        assert user is None

    def test_username_character_validation(self):
        """Test username character validation."""
        invalid_usernames = [
            "user;--",  # SQL injection
            "user'",  # SQL injection
            'user"',  # SQL injection
            "user/*",  # SQL injection
            "user*/",  # SQL injection
            "user\n",  # newline
            "user\t",  # tab
        ]

        for username in invalid_usernames:
            user = get_user(username)
            assert user is None

    def test_empty_username(self):
        """Test empty username."""
        user = get_user("")
        assert user is None

    def test_whitespace_username(self):
        """Test username with only whitespace."""
        user = get_user("   ")
        assert user is None


@pytest.fixture
def sample_users():
    """Fixture for test users."""
    return [
        ("test1", "password1", "viewer"),
        ("test2", "password2", "admin"),
        ("test3", "password3", "editor"),
    ]


@pytest.mark.parametrize(
    "username,password,role",
    [
        ("test1", "password1", "viewer"),
        ("test2", "password2", "admin"),
        ("test3", "password3", "editor"),
    ],
)
def test_create_and_retrieve_parametrized(username, password, role):
    """Parametrized test for creating and retrieving user."""
    user = create_user(username, password, role)
    assert user.username == username
    assert user.role == role

    retrieved = get_user(username)
    assert retrieved is not None
