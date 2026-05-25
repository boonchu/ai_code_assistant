# AGENTS.md — OpenAI with docker model runner

## Project Overview

OpenAI compatible application to test with docker model runner

## Architecture

- **Model**: Gemma 4 E2B (4.65B params) via Docker Model Runner — OpenAI-compatible endpoint

## Project Structure

```
.
├── app/
│   ├── __init__.py              # Package init (absolute import)
│   ├── agent.py                 # Agent definition (LlmAgent + API Registry MCP)
├── pyproject.toml               # Dependencies (google-adk[extensions])
├── Dockerfile                   # Multi-stage build with uv (Python 3.13)
├── docker-compose.yaml          # ADK agent → Docker Model Runner
├── .envrc                       # Environment variables (direnv)
├── .python-version              # Python 3.13
├── .gitignore
├── .dockerignore
└── uv.lock
```

## Docker Model Runner

Docker Model Runner exposes an OpenAI-compatible API:
- **From host**: `http://localhost:12434/engines/v1`
- **From containers**: `http://host.docker.internal:12434/engines/v1`

Enable TCP access: `docker desktop enable model-runner --tcp 12434`

### Model variants

| Model | Params | Size | Notes |
|-------|--------|------|-------|
| `ai/gemma4` | 7.52B | 4.74 GiB | Default, slower on local |
| `ai/gemma4:E2B` | 4.65B | 2.94 GiB | **Recommended** — fast enough for agent loops |

### Key requirement

Docker Model Runner **must be up-to-date** (v1.1.29+) for Gemma 4 architecture support. Older versions (e.g. v0.1.4) fail with "inference backend took too long to initialize" — this is NOT a memory issue, it's an architecture incompatibility. Update Docker Desktop to fix it.

## Setup and Running

### 1. Prerequisites
- Docker Desktop with Model Runner enabled (v1.1.29+)
- GCP Application Default Credentials (`gcloud auth application-default login`)
- uv and direnv

### 2. Pull the model
```bash
docker desktop enable model-runner --tcp 12434
docker model pull ai/gemma4:E2B
```

### 3. Install and run
```bash
direnv allow
uv sync
uv run adk web
```
Opens at `http://localhost:8000`.

### 4. Run with Docker Compose
```bash
docker compose up --build
```
Agent API at `http://localhost:8080`.

## Troubleshooting

- **"inference backend took too long to initialize"**: Update Docker Desktop to get Model Runner v1.1.29+. This is NOT a memory issue.
