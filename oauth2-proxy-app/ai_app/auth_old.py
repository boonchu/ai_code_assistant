"""
Authentication module for AI App Proxy.

Provides:
- OAuth2 Password Flow with JWT tokens
- API Key authentication
- User management with role-based access control
"""

import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ai_app.settings import DEFAULT_TIMEOUT, API_KEY_SECRET

# Configuration
SECRET_KEY = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# User database
USERS_DB: Dict[str, Dict[str, Any]] = {
    "view": {
        "username": "view",
        "password": "656d604dfdba41a262963cce53699bbc56cd7a2c0da1ad5ead45fc49214159d6",
        "password_hash": "656d604dfdba41a262963cce53699bbc56cd7a2c0da1ad5ead45fc49214159d6",
        "role": "viewer",
    },
    "demo": {
        "username": "demo",
        "password": "d3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791",
        "password_hash": "d3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791",
        "role": "admin",
    },
}


# Pydantic models
class TokenData(BaseModel):
    """Token payload data."""

    username: str
    role: str
    exp: float
    iat: float


class LoginRequest(BaseModel):
    """Login request."""

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
    version: str = "1.0.2"


# OAuth2 Security
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    description="JWT authentication via OAuth2 Password Flow",
)


# Password hashing (simple SHA256 for testing)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a SHA256 hashed password."""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: Dict[str, Any]) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {**data, "exp": expire, "iat": datetime.utcnow().timestamp()}
    # Cast to str to satisfy mypy
    return str(jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get user from database by username."""
    return USERS_DB.get(username)


def get_api_key(api_key: str) -> Optional[str]:
    """Validate API key against settings."""
    return API_KEY_SECRET if api_key == API_KEY_SECRET else None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username and password."""
    user = get_user(username)
    if not user:
        return None
    # Verify password using SHA256
    if verify_password(password, user.get("password_hash", "")):
        return user
    return None


def get_current_user(token: str) -> TokenData:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(
            username=username,
            role=role,
            exp=payload.get("exp"),
            iat=payload.get("iat"),
        )
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return token_data


async def get_current_user_dep(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    token_data = get_current_user(token)
    return {"username": token_data.username, "role": token_data.role}


async def get_current_user_or_api_key_from_header(request: Request) -> dict[str, Any]:
    """Dependency for protected endpoints - checks Authorization or X-API-Key header."""
    # Try JWT token first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
        return get_current_user_or_api_key(token=token)

    # Try API key
    api_key = request.headers.get("X-API-Key")
    if api_key and api_key == API_KEY_SECRET:
        return {"username": "api_user", "role": "admin", "method": "api_key"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Use JWT token or API key.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_api_key(request: Request) -> Dict[str, str]:
    """Validate API key from header."""
    api_key_value = request.headers.get("X-API-Key")
    if api_key_value != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    return {"username": "api_user", "role": "admin"}


async def check_user_permission(user: TokenData, required_role: str) -> None:
    """Check if user has required permission."""
    if user.role != "admin" and user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin or required role needed.",
        )


def get_current_user_or_api_key(token: Optional[str] = None) -> Dict[str, Any]:
    """Get current user via OAuth2 token."""
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            role = payload.get("role")
            if username:
                return {"username": username, "role": role, "method": "oauth2"}
        except JWTError:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Use OAuth2 token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Simple dependency for protected endpoints
async def get_authenticated_user(
    token: Optional[str] = Depends(oauth2_scheme),
) -> dict[str, Any]:
    """Dependency for protected endpoints - accepts JWT token."""
    return get_current_user_or_api_key(token)
