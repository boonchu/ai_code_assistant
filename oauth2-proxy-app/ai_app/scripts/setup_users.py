#!/usr/bin/env python3
"""
Setup script for creating initial user accounts.

Sets up users:
- view (limited access): username=view, password=view123
- demo (full admin): username=demo, password=demo123

Run with: uv run python ai_app/scripts/setup_users.py
"""

import sys
import hashlib

sys.path.insert(0, "/home/bigchoo/Documents/src/llm_pi/ai-app")

from ai_app.auth_v2 import DEFAULT_USERS as USERS_DB
from ai_app.settings import API_KEY_SECRET
import json
import os


def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def setup_users():
    """Create or update users in the database."""
    print("🔐 Setting up user accounts...\n")

    # Define user credentials
    user_data = {
        "view": {
            "username": "view",
            "password": "view123",
            "role": "viewer",
        },
        "demo": {
            "username": "demo",
            "password": "demo123",
            "role": "admin",
        },
    }

    for username, creds in user_data.items():
        print(f"Setting up user: {username}")

        # Hash the password
        password_hash = hash_password(creds["password"])

        # Update the database
        USERS_DB[username] = {
            "username": creds["username"],
            "password": password_hash,
            "role": creds["role"],
        }

        print(f"  ✅ Username: {username}")
        print(f"  ✅ Password: {creds['password']}")
        print(f"  ✅ Role: {creds['role']}")
        print()

    # Save to file for reference
    config_file = os.path.join(os.path.dirname(__file__), "users.json")
    with open(config_file, "w") as f:
        json.dump(
            {
                "view": {"password": "view123"},
                "demo": {"password": "demo123"},
                "api_key": API_KEY_SECRET,
            },
            f,
            indent=2,
        )

    print("💾 Credentials saved to ai_app/scripts/users.json")
    print("\n🎉 Setup complete!")
    print("\nLogin credentials:")
    print("  - Username: view, Password: view123 (limited access)")
    print("  - Username: demo, Password: demo123 (full admin access)")
    print("  - API Key: your-super-secret-api-key (use X-API-Key header)")


if __name__ == "__main__":
    setup_users()
