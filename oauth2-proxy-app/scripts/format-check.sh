#!/bin/bash
set -e

echo "🔍 Running black formatting check..."
uv run black --check ai_app main.py tests

echo "✅ Formatting check passed!"
