"""
DEPRECATED: Authentication module (v1.0.2).

⚠️ This module is deprecated and will be removed in a future release.
Please use ai_app.auth_v2 or ai_app.routers.auth instead.

This version used insecure SHA256 password hashing.
The new implementation uses bcrypt for secure password storage.

Migration Guide:
===============

1. Update your imports:
   OLD: from ai_app.auth import get_current_user
   NEW: from ai_app.auth_v2 import get_current_user
        or from ai_app.routers.auth import get_current_user

2. Update environment variables:
   JWT_SECRET=your-secure-secret
   API_KEY_SECRET=your-api-key

3. Re-authenticate users:
   Old SHA256 hashes are incompatible with new bcrypt system.
   Users must log in again to generate new password hashes.

See AUTH_SECURITY.md and CHANGES.md for full migration guide.
"""

# Import from new module
from ai_app.auth_v2 import *  # noqa: F401,F403

# Re-export everything with deprecation warnings
import warnings

warnings.warn(
    "ai_app.auth is deprecated. Use ai_app.auth_v2 or ai_app.routers.auth instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "hash_password",
    "verify_password",
    "get_password_hash",
    "set_default_user_passwords",
    "create_access_token",
    "decode_token",
    "get_user",
    "get_user_by_role",
    "create_user",
    "delete_user",
    "authenticate_user",
    "TokenData",
    "get_current_user_from_token",
    "get_api_key",
    "get_current_user_from_api_key",
    "check_user_permission",
    "get_required_role",
    "get_current_user",
    "get_current_user_with_permissions",
    "get_current_api_key_user",
    "get_current_user_or_api_key",
    "oauth2_scheme",
    "initialize_auth",
    "DEFAULT_USERS",
]
