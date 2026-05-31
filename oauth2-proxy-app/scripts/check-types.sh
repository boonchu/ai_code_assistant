#!/bin/bash
set -e

echo "🔍 Running mypy type check..."

# Run type checks separately for each package
uv run mypy ai_app
uv run mypy main.py
uv run mypy tests

echo "✅ Type check passed!"
