"""Application settings and configuration constants."""

import os
import threading
import time
from typing import List

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://llama-cpp:8080")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

# Default timeout for health check requests
DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", "5.0"))

# Rate limiting configuration
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds in window

# API configuration
API_VERSION = os.getenv("API_VERSION", "1.0.0")

# CORS configuration
CORS_ALLOW_ORIGINS = os.getenv(
    "CORS_ALLOW_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

# API key for authentication
API_KEY_SECRET = os.getenv(
    "API_KEY_SECRET", "your-super-secret-api-key-change-in-production"
)

# Password hashing configuration
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# Rate limiting lock
RATE_LIMIT_LOCK = threading.Lock()

# User database configuration
ENABLE_DB_MIGRATIONS = os.getenv("ENABLE_DB_MIGRATIONS", "true").lower() == "true"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "ai_app")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_SSL = os.getenv("DB_SSL", "false").lower() == "true"
