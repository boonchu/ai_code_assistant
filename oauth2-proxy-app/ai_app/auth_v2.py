"""
Authentication module for AI App Proxy (v2 - Security Hardened).

Provides:
- OAuth2 Password Flow with JWT tokens
- API Key authentication
- User management with role-based access control
- Secure password hashing with bcrypt
"""

import os
import re
from datetime import datetime, timedelta
from typing import Any, cast, Dict, List, Optional, Union

import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ConfigDict
from pydantic.functional_validators import field_validator

from ai_app.settings import (
    DEFAULT_TIMEOUT,
    API_KEY_SECRET,
    JWT_SECRET,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Configuration
ALGORITHM = "HS256"


# =============================================================================
# User Models
# =============================================================================


class User(BaseModel):
    """User model."""

    username: str
    password_hash: str
    role: str
    full_name: str = ""
    is_active: bool = True

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not (3 <= len(v) <= 30):
            raise ValueError("Username must be 3-30 characters")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("admin", "viewer", "editor"):
            raise ValueError("Role must be 'admin', 'viewer', or 'editor'")
        return v


# Default users (in production, use a database)
DEFAULT_USERS: Dict[str, User] = {
    "view": User(
        username="view",
        password_hash="",  # Will be set after hashing
        role="viewer",
        full_name="View User",
    ),
    "demo": User(
        username="demo",
        password_hash="",  # Will be set after hashing
        role="admin",
        full_name="Demo Admin",
    ),
}


# =============================================================================
# Pydantic Models
# =============================================================================


class LoginRequest(BaseModel):
    """Login request."""

    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response."""

    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    message: str = "AI Proxy is running"
    version: str = "1.0.3"


# =============================================================================
# Password Hashing (bcrypt - secure)
# =============================================================================


def hash_password(plain_password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hashed password."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(plain_password: str) -> str:
    """Hash a password using bcrypt."""
    return hash_password(plain_password)


def set_default_user_passwords() -> None:
    """Set default user passwords."""
    # Production-ready default passwords - CHANGE THESE BEFORE PRODUCTION!
    # Minimum password requirements: 8 chars, mix of upper/lower/number/symbol
    DEFAULT_USERS["view"].password_hash = hash_password(
        "SecureV1ew!2024"
    )  # Viewer account
    DEFAULT_USERS["demo"].password_hash = hash_password(
        "D3mo!Admin@2024"
    )  # Admin account


# =============================================================================
# JWT Token Functions
# =============================================================================


def create_access_token(data: Dict[str, Any]) -> str:
    """Create a JWT access token."""
    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use integer timestamps to ensure consistent expiration calculation
    to_encode = {
        **data,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
    }
    # jwt.encode returns Any due to jose library lacking type stubs
    return cast(str, jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM))


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    # jwt.decode returns Any due to jose library lacking type stubs
    return cast(Dict[str, Any], jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM]))


# User Management
# =============================================================================


def get_user(username: str) -> Optional[User]:
    """Get user from database by username."""
    for user in DEFAULT_USERS.values():
        if user.username == username:
            return user
    return None


def get_user_by_role(role: str) -> List[User]:
    """Get all users with specified role."""
    return [user for user in DEFAULT_USERS.values() if user.role == role]


def create_user(
    username: str,
    password: str,
    role: str,
    full_name: str = "",
) -> Optional[User]:
    """Create a new user."""
    # Check if username already exists
    for existing_user in DEFAULT_USERS.values():
        if existing_user.username == username:
            return None

    user = User(username=username, password_hash="", role=role, full_name=full_name)
    user.password_hash = hash_password(password)
    DEFAULT_USERS[username] = user
    return user


def delete_user(username: str) -> bool:
    """Delete a user from the database."""
    if username in DEFAULT_USERS:
        del DEFAULT_USERS[username]
        return True
    return False


# =============================================================================
# Authentication
# =============================================================================


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    user = get_user(username)
    if not user or not user.is_active:
        return None
    if verify_password(password, user.password_hash):
        return user
    return None


class TokenData(BaseModel):
    """Token payload data."""

    username: str
    role: str
    sub: str = ""  # Subject claim (username)


def get_current_user_from_token(token: str) -> TokenData:
    """Get current user from JWT token."""
    try:
        payload = decode_token(token)
        username = payload.get("sub") or payload.get("username")
        role = payload.get("role")

        if not username or not role:
            raise ValueError("Invalid token: missing required claims")

        user = get_user(username)
        if not user:
            raise ValueError("User not found")

        return TokenData(
            username=username,
            role=role,
        )
    except JWTError:
        raise ValueError("Invalid token")


# =============================================================================
# API Key Authentication
# =============================================================================


def get_api_key(api_key: str) -> Optional[str]:
    """Validate API key."""
    return api_key if api_key == API_KEY_SECRET else None


def get_current_user_from_api_key(api_key: str) -> Optional[Dict[str, str]]:
    """Get current user from API key."""
    if api_key == API_KEY_SECRET:
        return {"username": "api_user", "role": "admin", "method": "api_key"}
    return None


# =============================================================================
# Permissions
# =============================================================================


def check_user_permission(user: TokenData, required_role: str) -> bool:
    """Check if user has required permission. Returns True if authorized."""
    # Admin can do anything
    if user.role == "admin":
        return True
    # Check if user has the required role
    return user.role == required_role


def get_required_role(user: TokenData, required_roles: List[str]) -> bool:
    """Check if user has one of the required roles."""
    if user.role == "admin":
        return True
    return user.role in required_roles


# =============================================================================
# FastAPI Dependencies
# =============================================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    description="JWT authentication via OAuth2 Password Flow",
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Dependency to get current authenticated user from JWT token."""
    return get_current_user_from_token(token)


async def get_current_user_with_permissions(
    token: str = Depends(oauth2_scheme),
) -> Dict[str, str]:
    """Dependency to get current user with role validation."""
    user: Optional[TokenData] = get_current_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return {
        "username": user.username,
        "role": user.role,
    }


async def get_current_api_key_user(request: Request) -> Dict[str, Any]:
    """Dependency to get current user from API key."""
    api_key_value = request.headers.get("X-API-Key")
    if api_key_value and api_key_value == API_KEY_SECRET:
        return {"username": "api_user", "role": "admin", "method": "api_key"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "API-Key"},
    )


async def get_current_user_or_api_key(
    request: Request,
) -> Optional[Union[TokenData, Dict[str, Any]]]:
    """Dependency for protected endpoints - checks JWT token or API key."""
    # Try JWT token first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
        try:
            return get_current_user_from_token(token=token)
        except ValueError:
            pass

    # Try API key
    api_key = request.headers.get("X-API-Key")
    if api_key == API_KEY_SECRET:
        return {"username": "api_user", "role": "admin", "method": "api_key"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Use JWT token or API key.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_role(user: TokenData, required_role: str) -> TokenData:
    """Dependency to require specific role."""
    if not check_user_permission(user, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin or required role needed.",
        )
    return user


# =============================================================================
# Initialization
# =============================================================================


def initialize_auth() -> None:
    """Initialize authentication module."""
    set_default_user_passwords()
    print(f"Initialized {len(DEFAULT_USERS)} default users")


# Initialize on import
initialize_auth()
