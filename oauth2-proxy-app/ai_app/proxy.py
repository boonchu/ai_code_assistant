"""OpenAI-compatible proxy to local chat backend."""

import logging
import time
from typing import Any

from fastapi import Depends, FastAPI, Form, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from ai_app.auth_v2 import (
    User,
    TokenData,
    oauth2_scheme,
    get_current_user_from_token,
    get_current_user_with_permissions,
    create_access_token,
    decode_token,
    get_user,
    verify_password,
)
from ai_app.settings import (
    API_KEY_SECRET,
    BACKEND_URL,
    CORS_ALLOW_ORIGINS,
    DEFAULT_TIMEOUT,
    RATE_LIMIT_LOCK,
    RATE_LIMIT_MAX_REQUESTS,
    RATE_LIMIT_WINDOW,
)

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(title="AI App Proxy", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting storage
request_counts: dict[str, int] = {}

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# Authentication dependencies
def require_auth(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate JWT token and require admin role."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user_from_token(token)
        # Check if user has admin role
        if user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required for this endpoint",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except ValueError as e:
        raise credentials_exception


# Async helper for admin authentication
async def require_viewer_auth(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate JWT token and allow viewer or admin roles."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = get_current_user_from_token(token)
        # Allow viewer and admin roles
        if user.role not in ["viewer", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Viewer or admin access required for this endpoint",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except ValueError as e:
        raise credentials_exception


async def _get_admin_user(request: Request) -> dict[str, str]:
    """Validate JWT token with admin role requirement."""
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    from ai_app.auth_v2 import (
        get_current_user_with_permissions as gcuwp,
        check_user_permission,
    )

    user = await gcuwp(token)
    if not check_user_permission(
        type("TokenData", (), {"role": user["role"]})(), "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(request: Request) -> dict[str, str]:
    """Validate JWT token with admin role requirement."""
    return await _get_admin_user(request)


def _get_client_key(request: Request) -> str:
    """Get client identifier for rate limiting."""
    return request.client.host if request.client else "default"


async def check_rate_limit(request: Request) -> tuple[bool, int]:
    """Check if the request is within rate limits."""
    with RATE_LIMIT_LOCK:
        current_time = time.time()
        stale_keys = [
            key
            for key, value in request_counts.items()
            if current_time - value < RATE_LIMIT_WINDOW
        ]
        for key in stale_keys:
            del request_counts[key]

        client_key = _get_client_key(request)
        request_counts[client_key] = request_counts.get(client_key, 0) + 1
        current_count = request_counts[client_key]

        allowed = current_count <= RATE_LIMIT_MAX_REQUESTS
        return allowed, current_count


async def _proxy_request(
    method: str,
    url: str,
    data: dict[str, Any],
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Proxy request to backend with unified error handling."""
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=data, timeout=timeout)

    if response.status_code >= 400:
        if "application/json" in response.headers.get("content-type", ""):
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
        else:
            error_msg = response.text
        raise HTTPException(status_code=response.status_code, detail=error_msg)

    response.raise_for_status()
    result = response.json()
    return result  # type: ignore


# =============================================================================
# Health Endpoints
# =============================================================================


@app.get("/health")
@app.get("/api/v1/health")
async def health_check() -> JSONResponse:
    """Health check endpoint with actual backend verification."""

    backend_healthy = False
    backend_response_text = ""

    import httpx

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(f"{BACKEND_URL}/health", follow_redirects=True)
            response.raise_for_status()
            backend_response_text = response.text

            if (
                "status: ok" in backend_response_text.lower()
                or '"status":"ok"' in backend_response_text.lower()
            ):
                backend_healthy = True
            elif "status" in backend_response_text.lower():
                backend_healthy = False
            else:
                backend_healthy = True
    except (httpx.ConnectError, httpx.TimeoutException):
        backend_response_text = "Connection timeout or refused"
    except Exception as e:
        backend_response_text = str(e)

    if backend_healthy:
        return JSONResponse(
            status_code=200, content={"status": "healthy", "backend_url": BACKEND_URL}
        )
    else:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "backend_url": BACKEND_URL,
                "error": backend_response_text,
            },
        )


# =============================================================================
# Authentication Endpoints
# =============================================================================


@app.post("/api/v1/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, Any]:
    """
    OAuth2 login endpoint.

    Validates:
    - Username length (3-30 characters)
    - SQL injection patterns
    - Password verification

    Returns JWT token with user info.
    """
    username = form_data.username.strip()
    password = form_data.password

    # Validate username length
    if len(username) < 3 or len(username) > 30:
        raise HTTPException(
            status_code=400,
            detail="Username must be between 3 and 30 characters",
        )

    # Validate username and password are not empty
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    if not password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")

    # Check for SQL injection patterns
    if any(char in username for char in ["'", '"', ";", "--", "/*", "*/"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid username format",
        )

    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
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
    payload = decode_token(token)
    username = payload["sub"]
    role = payload["role"]

    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"username": user.username, "role": user.role}


@app.post("/api/v1/auth/logout")
async def logout(request: Request) -> dict[str, Any]:
    """
    Logout endpoint (JWT tokens are stateless).

    In production, implement token blacklist with Redis.
    """
    # In production: add token to blacklist
    logger.info("User logged out")
    return {"detail": "Successfully logged out"}


@app.get("/api/v1/auth/health")
async def auth_health() -> dict[str, Any]:
    """Authentication service health check."""
    return {"status": "healthy", "service": "auth"}


@app.get("/api/v1/auth/users/{username}")
async def get_user_info(username: str) -> dict[str, Any]:
    """
    Get user information.

    Requires admin role.
    """
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Don't return password hash
    return {"username": user.username, "role": user.role, "full_name": user.full_name}


@app.post("/api/v1/auth/api-key")
async def validate_api_key(api_key: str = Form(...)) -> dict[str, Any]:
    """
    Validate API key and return user info.
    """
    if api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    return {"username": "api_user", "role": "admin", "method": "api_key"}


@app.get("/api/v1/auth/api-key")
async def api_key_info(request: Request) -> dict[str, Any]:
    """
    Get authenticated user info via API key.

    Requires X-API-Key header.
    """
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "API-Key"},
        )

    if api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    return {"username": "api_user", "role": "admin", "method": "api_key"}


# =============================================================================
# Chat Endpoints (Protected)
# =============================================================================


@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    token: TokenData = Depends(require_auth),
):
    """Proxy chat completions to local backend."""
    username_val = token.username

    allowed, _ = await check_rate_limit(request)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    data = await request.json()
    return await _proxy_request(
        "POST", f"{BACKEND_URL}/v1/chat/completions", data=data, timeout=60.0
    )


@app.post("/v1/completions")
async def completions(
    request: Request,
    token: TokenData = Depends(require_auth),
):
    """Proxy completions to local backend."""
    username_val = token.username

    allowed, _ = await check_rate_limit(request)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    data = await request.json()
    return await _proxy_request(
        "POST", f"{BACKEND_URL}/v1/completions", data=data, timeout=60.0
    )


@app.post("/v1/embeddings")
async def embeddings(
    request: Request,
    token: TokenData = Depends(require_auth),
):
    """Proxy embeddings to local backend."""
    username_val = token.username

    allowed, _ = await check_rate_limit(request)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    data = await request.json()
    return await _proxy_request(
        "POST", f"{BACKEND_URL}/v1/embeddings", data=data, timeout=60.0
    )


@app.get("/v1/models")
async def list_models(token: TokenData = Depends(require_viewer_auth)):
    """List available models (viewer or admin)."""
    return await _proxy_request("GET", f"{BACKEND_URL}/v1/models", {}, 30.0)


@app.get("/v1/models/{model_id}")
async def get_model(model_id: str, token: TokenData = Depends(require_viewer_auth)):
    """Proxy model info to local backend."""
    return await _proxy_request("GET", f"{BACKEND_URL}/v1/models/{model_id}", {}, 30.0)


# =============================================================================
# Exception Handlers
# =============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    if request.url.path == "/health":
        return JSONResponse(status_code=503, content={"detail": "Health check failed"})
    return JSONResponse(status_code=500, content={"detail": str(exc)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
