"""Main entry point for AI App Proxy."""

from ai_app import proxy

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "ai_app.proxy:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
