# AI App Proxy

OpenAI-compatible proxy server that forwards requests to your local LLM backend running on `localhost:8080`.

**Recommended Backend**: [FastAPI](https://fastapi.tiangolo.com/) - Python's modern, high-performance web framework for building APIs with Python, featuring automatic interactive API docs, dependency injection, data validation, and async support out of the box.

## Features

- ✅ OpenAI API fully compatible
- ✅ CORS enabled for browser access
- ✅ Request/response logging (optional)
- ✅ Automatic request forwarding to local backend
- ✅ Health check endpoint with proper status codes (200/503)
- ✅ Docker support
- ✅ uv package management

## Prerequisites

- Python 3.10+
- uv package manager

## Quick Start

### Using uv (Recommended)

```bash
# Navigate to project directory
cd ai-app

# Install dependencies
uv sync

# Run the proxy
uv run python main.py
```

The proxy will start on `http://localhost:8000`.

### Using Docker

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f ai-proxy
```

### Using pip (alternative)

```bash
pip install -r requirements.txt
python main.py
```

## Configuration

Edit `pyproject.toml` or create a config file:

```toml
# Backend URL (default: localhost:8080)
BACKEND_URL = "http://localhost:8080"

# Optional: Enable logging
LOG_LEVEL = "DEBUG"
```

## API Endpoints

All endpoints forward to your local backend at `http://localhost:8080`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check - returns `{"status": "healthy"}` |
| `/v1/chat/completions` | POST | Chat completion (OpenAI format) |
| `/v1/completions` | POST | Text completion |
| `/v1/embeddings` | POST | Text embeddings |
| `/v1/models` | GET | List available models |
| `/v1/models/{id}` | GET | Get specific model info |

### Chat Completions Example

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is machine learning?"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### Completions Example

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "prompt": "Say hello",
    "temperature": 0.7
  }'
```

### Embeddings Example

```bash
curl http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "input": "The quick brown fox"
  }'
```

## Usage Examples

### Python

```python
import httpx

async def chat_with_proxy():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "model": "my-model",
                "messages": [{"role": "user", "content": "Hello!"}]
            }
        )
        print(response.json())
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function chatWithProxy() {
  const response = await fetch('http://localhost:8000/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'my-model',
      messages: [{ role: 'user', content: 'Hello!' }]
    })
  });
  return await response.json();
}
```

## Development

### Code Formatting

This project uses [Black](https://black.readthedocs.io/) for code formatting.

```bash
# Format all Python files
uv run black ai_app/ main.py

# Check formatting (without modifying)
uv run black --check ai_app/ main.py
```

### Running the Proxy

```bash
# Watch for file changes and auto-reload
uv run python main.py

# With detailed logs
uv run python main.py --log-level debug
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output and coverage
uv run pytest -v --cov=ai_app

# Run specific test class
uv run pytest tests/test_proxy.py::TestChatCompletions

# Generate HTML coverage report
uv run pytest --cov=ai_app --cov-report=html --cov-report=term

# Run tests with timeout
uv run pytest --timeout=30
```

### Test Coverage

```bash
# Show coverage in terminal
uv run pytest --cov=ai_app --cov-report=term-missing

# Generate detailed HTML report
uv run pytest --cov=ai_app --cov-report=html:htmlcov
# Then open: open htmlcov/index.html
```

### Test Coverage

```bash
# Generate coverage report
uv run pytest --cov=ai_app --cov-report=term-missing

# Open HTML coverage report in browser
open htmlcov/index.html  # macOS/Linux
start htmlcov\index.html  # Windows
```

## Troubleshooting

### Connection Refused

Make sure your backend is running on `localhost:8080`:

```bash
# Check backend
curl http://localhost:8080/health

# If using Docker, ensure backend container is running
docker ps
```

### CORS Issues

If you're getting CORS errors in the browser, ensure your frontend is accessing `http://localhost:8000`.

### Rate Limiting

Add rate limiting middleware if needed:

```python
from fastapi import HTTPException

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    # Implement rate limiting here
    pass
```

## Authentication

The AI App includes comprehensive **JWT token and API key authentication** to secure proxy endpoints.

**Release 1.0.3** includes major security improvements:
- ✅ bcrypt password hashing (industry standard, OWASP recommended)
- ✅ Environment variable secrets (no hardcoded credentials)
- ✅ Comprehensive input validation (SQL injection protection)
- ✅ Role-based access control (admin/editor/viewer)
- ✅ Token expiration and refresh support

**New Documentation**: See [AUTHENTICATION.md](AUTHENTICATION.md) for complete security documentation, including:
- bcrypt vs SHA256 comparison
- Password migration guide
- Environment configuration
- Security best practices
- Troubleshooting

### Features

- **JWT Token Authentication**: OAuth2 password flow for secure token-based access
- **API Key Authentication**: Simple key-based authentication via `X-API-Key` header
- **Role-Based Access**: Demo user (admin) and View user (limited permissions)
- **Public Endpoints**: Health checks remain publicly accessible

### Protected Endpoints

All `/v1/*` endpoints require authentication:

- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completion
- `POST /v1/completions` - Text completion
- `POST /v1/embeddings` - Text embeddings

### Authentication Methods

**Method 1: JWT Token**
```bash
# Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d 'username=demo&password=D3mo!Admin@2024' | jq -r '.access_token')

# Use token for protected endpoints
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/v1/models
```

**Method 2: API Key**
```bash
curl -H "X-API-Key: your-super-secret-api-key" \
  http://localhost:8000/v1/models
```

### Default Credentials

**⚠️ CRITICAL: Change these passwords before production!**

**Demo User (Full Access)**
- Username: `demo`
- Password: `D3mo!Admin@2024`
- Role: `admin`

**View User (Limited Access)**
- Username: `view`
- Password: `SecureV1ew!2024`
- Role: `viewer`

```
 ┌──────────────────────┬─────────┬───────────────┬───────────────┐
 │ Endpoint             │ No Auth │ Viewer        │ Admin         │
 ├──────────────────────┼─────────┼───────────────┼───────────────┤
 │ /v1/models           │ ❌ 401  │ ✅ 1 model    │ ✅ 1 model    │
 ├──────────────────────┼─────────┼───────────────┼───────────────┤
 │ /v1/models/{id}      │ ❌ 401  │ ✅ Model info │ ✅ Model info │
 ├──────────────────────┼─────────┼───────────────┼───────────────┤
 │ /v1/chat/completions │ ❌ 401  │ ❌ 403        │ ✅ Response   │
 ├──────────────────────┼─────────┼───────────────┼───────────────┤
 │ /v1/embeddings       │ ❌ 401  │ ❌ 403        │ ✅ Response   │
 ├──────────────────────┼─────────┼───────────────┼───────────────┤
 │ /v1/completions      │ ❌ 401  │ ❌ 403        │ ✅ Response   │
 └──────────────────────┴─────────┴───────────────┴───────────────┘
```

**Migration**: If you were using the old SHA256 system (`admin123`, `view123`), you must update to the new bcrypt system immediately.

### Security Best Practices

- **Never use default credentials in production**
- **Change `API_KEY_SECRET` before deployment**
- **Use bcrypt instead of SHA256 for password hashing**
- **Implement HTTPS in production**
- **Monitor for brute force attacks**



## Changelog

### [1.0.3] - 2026-05-31

#### Security (Major)
- **bcrypt Password Hashing**: Replaced SHA256 with industry-standard bcrypt (12 rounds, configurable via `BCRYPT_ROUNDS`). Old SHA256 passwords are **incompatible** - all users must re-authenticate.
- **Environment Variable Secrets**: Moved `JWT_SECRET`, `API_KEY_SECRET` from hardcoded values to environment variables. No secrets in source code.
- **Input Validation**: Added comprehensive username validation (3-30 chars, alphanumeric+underscore+hyphen) and SQL injection protection.
- **Consolidated Authentication**: Unified authentication logic in `ai_app/auth_v2.py` and endpoints in `ai_app/routers/auth.py`. Removed code duplication.
- **Role-Based Access Control**: Implemented admin/editor/viewer roles with permission separation.
- **Default Credentials Updated**: Changed from weak passwords (`view123`, `admin123`) to production-ready secure passwords (`SecureV1ew!2024`, `D3mo!Admin@2024`).

#### Added
- **JWT Token Authentication**: OAuth2 password flow with configurable token expiration (default: 15 minutes).
- **API Key Authentication**: Server-to-server authentication via `X-API-Key` header.
- **Protected Endpoints**: All `/v1/*` endpoints require JWT token or API key authentication.
- **Comprehensive Test Suite**: 57 tests covering password hashing, token creation, user management, input validation, login endpoints, API keys, and security.
- **Environment Configuration**: Added `.env.example`, `.env`, `pytest.ini`, and Docker environment variables.
- **Documentation**: Created `AUTHENTICATION.md` combining authentication and security documentation.

#### Refactored
- **Settings Consolidation** (`ai_app/settings.py`):
  - Created `ai_app/settings.py` module for all configuration constants
  - Added `JWT_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `API_KEY_SECRET`, `BCRYPT_ROUNDS`
  - All secrets now use `os.getenv()` with secure fallbacks
- **Auth Module Split** (`ai_app/auth_v2.py`, `ai_app/routers/auth.py`):
  - Separated authentication logic (`auth_v2.py`) from endpoints (`routers/auth.py`)
  - Single source of truth for authentication functions
  - RESTful API design with proper error handling
- **User Management** (`ai_app/auth_v2.py`):
  - `hash_password()`: bcrypt password hashing
  - `verify_password()`: bcrypt password verification
  - `create_user()`, `delete_user()`, `get_user()`: User CRUD operations
  - `get_user_by_role()`: Role-based user queries
  - `DEFAULT_USERS`: Pre-initialized default users with secure passwords

#### Security Improvements
- **Password Hashing**: SHA256 → bcrypt (OWASP recommended)
- **Secret Management**: Hardcoded → Environment variables
- **Input Validation**: None → Comprehensive (Pydantic validators)
- **Token Security**: JWT with 15-min expiration, role claims
- **Rate Limiting**: Implemented (100 req/60s per client IP)
- **CORS Configuration**: Configurable via environment variables

#### Performance
- **bcrypt overhead**: ~40ms per password hash vs 0.001ms SHA256
- **Trade-off**: Acceptable for security (users wait <1s for login)
- **Configurable**: `BCRYPT_ROUNDS` can be adjusted (10-14 range)

#### Files Changed
- **New**: `ai_app/auth_v2.py`, `ai_app/routers/auth.py`, `AUTHENTICATION.md`, `.env.example`, `.env`
- **Modified**: `ai_app/settings.py`, `Dockerfile`, `docker-compose.yml`, `main.py`, all test files
- **Deprecated**: `ai_app/auth.py` (kept for backward compatibility)

#### Migration Guide
1. **Update environment variables** before deployment:
   ```bash
   export JWT_SECRET="your-32-char-random-secret"
   export API_KEY_SECRET="your-api-key-secret"
   export BCRYPT_ROUNDS="12"
   ```

2. **Reset default user passwords** (or change immediately after login):
   - Viewer: `view` / `SecureV1ew!2024`
   - Admin: `demo` / `D3mo!Admin@2024`

3. **Update code imports**:
   ```python
   # Old:
   from ai_app.auth import hash_password, verify_password

   # New:
   from ai_app.auth_v2 import hash_password, verify_password
   ```

4. **Test authentication**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -d 'username=demo&password=D3mo!Admin@2024'
   ```

#### Breaking Changes
- **Password Hashing**: bcrypt replaces SHA256. All existing passwords become unusable.
- **Default Credentials**: Weak passwords replaced with secure ones.
- **Import Paths**: Authentication functions moved to `ai_app/auth_v2`.
- **API Endpoints**: Auth endpoints now in `/api/v1/auth/*` router.

#### Backward Compatibility
- Old SHA256 password hashes are **incompatible** with bcrypt
- Users must re-authenticate or admin must create new account
- Test suite updated to use bcrypt

### [1.0.2] - 2026-05-30

#### Refactored
- **Settings Consolidation** (`ai_app/settings.py`, `ai_app/proxy.py`):
  - Created `ai_app/settings.py` to consolidate all global configuration constants
  - Moved `BACKEND_URL`, `DEFAULT_TIMEOUT`, `RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_WINDOW`, `RATE_LIMIT_LOCK`, `ALLOWED_ORIGINS`, `API_KEY_SECRET` to settings module
  - Updated `ai_app/proxy.py` to import configuration from settings instead of defining globals
  - Improved maintainability by centralizing configuration in single location

#### Added
- **JWT Authentication**: OAuth2 password flow with JWT token support for secure API access
- **API Key Authentication**: Alternative authentication method using `X-API-Key` header
- **Protected Endpoints**: All `/v1/*` endpoints require authentication (JWT or API key)
- **Public Health Endpoints**: `/health`, `/api/v1/health`, `/api/v1/auth/health` remain publicly accessible
- **Default Credentials**: Demo user (admin) and View user (limited access) for testing
- **Password Hashing**: SHA256 for testing, bcrypt recommended for production
- **Comprehensive Documentation**: `AUTH.md` with complete authentication guide and security best practices

> **🔐 Authentication Overview**: The proxy now supports JWT token and API key authentication for protected endpoints. See [AUTH.md](AUTH.md) for detailed security configuration, credential management, and best practices.

#### Improved
- **Module Structure** (`ai_app/__init__.py`, `ai_app/settings.py`):
  - Created proper Python package structure with `__init__.py`
  - Added type hints and documentation to settings module
  - Separated configuration concerns from application logic

#### Development
- **Pre-commit Hooks** (`.pre-commit-config.yaml`):
  - Configured pre-commit hooks for automated code quality
  - Integrated Black for code formatting
  - Integrated mypy for type checking
  - Added trailing whitespace and file ending fixes
  - Hook automatically runs on `git commit`

### [1.0.1] - 2026-05-30

#### Added
- **Health Check Status Code Fix** (`ai_app/proxy.py:97-144`):
  - Changed `health_check()` return type from `dict[str, Any]` to `Response`
  - Now returns `JSONResponse(status_code=200)` for healthy backends
  - Returns `JSONResponse(status_code=503)` for unreachable/timed-out/failed backends
  - Proper error handling with detailed error messages in response body

#### Tests
- **Health Check Tests** (`tests/test_proxy.py`):
  - `test_health_check_returns_200_with_healthy_backend()`: Verifies 200 status for healthy backends
  - `test_health_check_returns_503_with_unhealthy_backend()`: Verifies 503 status for unhealthy backends
- **All 8 tests passing** with mock backend fixtures

### [1.0.0] - 2026-05-30

#### Added
- **Test Suite**: Complete test coverage with 7 passing tests covering:
  - Health endpoint validation
  - Rate limiting functionality
  - Chat completions forwarding
  - Completions endpoint forwarding
  - Embeddings endpoint forwarding
  - Models listing endpoint
  - CORS middleware configuration
- **Type Checking**: Added mypy with strict configuration for type safety
- **Code Formatting**: Black integration with project-wide formatting (88 char lines)
- **Development Scripts**: `check-types.sh` and `format-check.sh` for automated quality checks
- **Pre-commit Configuration** (`.pre-commit-config.yaml`, `scripts/`):
  - Configured pre-commit hooks for automated code quality checks
  - Added scripts for type checking and formatting validation

#### Fixed
- **Rate Limiting Bug** (`ai_app/proxy.py:40`):
  - Fixed `_get_client_key()` parameter bug - was using `Request` class instead of `request` variable
  - This caused rate limiting to fail for all requests
- **Race Condition** (`ai_app/proxy.py:60-64`):
  - Fixed dict comprehension in rate limit checking that could cause race conditions
  - Restructured logic to safely handle concurrent requests
- **Code Duplication** (`ai_app/proxy.py:108-140`):
  - Extracted `_proxy_request()` helper function to eliminate duplicate proxying logic
  - Now all endpoint proxying uses unified error handling
- **Missing Import** (`ai_app/proxy.py:4`):
  - Added `import time` for timestamp tracking
- **Health Check** (`ai_app/proxy.py:97-139`):
  - Implemented actual backend health verification
  - Returns 200 with "healthy" status when backend responds with "status: ok"
  - Returns 503 with "unhealthy" status when backend is unreachable or fails
- **Type Annotations** (`ai_app/proxy.py`):
  - Added proper type hints to all functions
  - Used `cast()` for proper type handling in JSON responses
- **CORS Configuration** (`ai_app/proxy.py:19-21`):
  - Properly configured CORS middleware with allowed origins
  - Added Vary header for security

#### Improved
- **Error Handling**:
  - Unified error handling in `_proxy_request()` function
  - Proper JSON error message extraction from backend responses
  - Graceful handling of non-JSON error responses
- **Logging**:
  - Added debug logging for request tracking
  - Removed duplicate logging configuration in main.py
- **Documentation**:
  - Updated README with development workflow
  - Added code formatting guidelines
  - Documented CORS configuration

#### Dependencies Added
- `pytest>=9.0.3` - Testing framework
- `pytest-asyncio>=1.4.0` - Async test support
- `mypy>=2.1.0` - Type checking
- `black>=26.5.1` - Code formatting

### [0.1.0] - 2024-01-01

#### Added
- Initial OpenAI-compatible proxy implementation
- Health check endpoint
- Chat completions, completions, embeddings, and models endpoints
- Rate limiting with per-client tracking
- CORS middleware for browser compatibility

## License

MIT License

## Development Scripts

### Type Checking

```bash
# Run mypy type checker
./scripts/check-types.sh

# Or directly with uv
uv run mypy ai_app main.py tests
```

### Formating

```bash
# Check formatting
uv run black --check ai_app main.py

# Format code
uv run black ai_app main.py
```

### Full Development Workflow

```bash
# Install dev dependencies
uv sync --dev

# Run type check
./scripts/check-types.sh

# Run tests
uv run pytest -v

# Format code
uv run black .
```
