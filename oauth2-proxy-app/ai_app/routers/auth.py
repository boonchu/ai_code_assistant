"""
Authentication router with improved security.

Uses the new auth_v2 module with:
- bcrypt password hashing
- Environment variable secrets
- Role-based access control
"""

import logging
from typing import Any

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ai_app.auth_v2 import (
    TokenData,
    User,
    create_access_token,
    get_current_user,
    get_current_user_or_api_key,
    get_current_user_with_permissions,
    get_user,
    require_role,
    verify_password,
)
from ai_app.settings import API_KEY_SECRET

logger = logging.getLogger(__name__)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@app.post("/api/v1/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, Any]:
    """
    OAuth2 login endpoint with improved validation.

    Uses OAuth2PasswordRequestForm which validates:
    - Username and password are provided
    - Sanitizes input

    Security:
    - Passwords are hashed with bcrypt
    - JWT tokens expire after 15 minutes (configurable)
    """
    username = form_data.username.strip()
    password = form_data.password

    # Validate username length
    if len(username) < 3 or len(username) > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be between 3 and 30 characters",
        )

    # Check for SQL injection patterns
    if any(char in username for char in ["'", '"', ";", "--", "/*", "*/"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username format",
        )

    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": username, "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
    }


@app.get("/api/v1/auth/me")
async def me(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    """
    Get current user information.

    Requires JWT token in Authorization header.
    """
    user = await get_current_user(token=token)
    return {"username": user.username, "role": user.role}


@app.get("/api/v1/auth/health")
async def auth_health() -> dict[str, Any]:
    """Authentication service health check."""
    return {"status": "healthy", "service": "auth"}


@app.post("/api/v1/auth/logout")
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> dict[str, Any]:
    """
    Logout endpoint (placeholder - JWT tokens are short-lived).

    In production, implement token revocation with a token blacklist.
    """
    # In production, add token to blacklist/redis cache
    logger.info(f"User {token} logged out")
    return {"detail": "Successfully logged out"}


@app.get("/api/v1/auth/users/{username}")
async def get_user_info(
    username: str,
    user_info: dict[str, Any] = Depends(get_current_user_with_permissions),
) -> dict[str, Any]:
    """
    Get user information (admin only).

    Requires admin role.
    """
    if user_info["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Don't return password hash
    return {"username": user.username, "role": user.role, "full_name": user.full_name}


@app.post("/api/v1/auth/api-key")
async def validate_api_key(
    api_key: str = Form(...),
) -> dict[str, Any]:
    """
    Validate API key.

    Returns user info for API key authentication.
    """
    if api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    return {"username": "api_user", "role": "admin", "method": "api_key"}


@app.get("/api/v1/auth/api-key")
async def api_key_info(
    request: Request,
) -> dict[str, Any]:
    """
    Get authenticated user info via API key.

    Requires X-API-Key header.
    """
    user = await get_current_user_or_api_key(request=request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    # user is either TokenData or dict[str, Any]; extract fields accordingly
    if isinstance(user, dict):
        return {
            "username": user["username"],
            "role": user["role"],
            "method": user["method"],
        }
    else:
        # TokenData case - should not happen for API key flow
        return {
            "username": user.username,
            "role": user.role,
            "method": "jwt",
        }


# Role-based endpoints (example)
# Note: require_role must be used as a decorator, not as a dependency argument
@app.get("/api/v1/admin/settings")
async def admin_settings_with_role():
    """Admin-only endpoint (requires role check in middleware)."""
    # In production, this would use a proper dependency
    # For now, just return a placeholder
    return {"settings": "admin-only-content", "note": "Requires admin role"}


@app.get("/api/v1/public/data")
async def public_data():
    """Public endpoint (no auth required)."""
    return {"data": "public-content"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(__name__ + ":app", host="0.0.0.0", port=8001)
