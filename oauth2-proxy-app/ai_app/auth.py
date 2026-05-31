"""
Authentication module (v2 - Security Hardened).

This module provides secure authentication using:
- bcrypt password hashing
- Environment variable secrets
- JWT tokens with short expiration
- API key authentication
- Role-based access control

See AUTH_SECURITY.md for security documentation.
"""

from ai_app.auth_v2 import *  # noqa: F401,F403

__all__ = [
    # Password functions
    "hash_password",
    "verify_password",
    "get_password_hash",
    "set_default_user_passwords",
    # Token functions
    "create_access_token",
    "decode_token",
    # User functions
    "get_user",
    "get_user_by_role",
    "create_user",
    "delete_user",
    "authenticate_user",
    # Token data
    "TokenData",
    # API Key functions
    "get_api_key",
    "get_current_user_from_api_key",
    # Permission functions
    "check_user_permission",
    "get_required_role",
    # Dependencies
    "get_current_user",
    "get_current_user_with_permissions",
    "get_current_user_or_api_key",
    "oauth2_scheme",
    # Initialization
    "initialize_auth",
    # Default users
    "DEFAULT_USERS",
]
