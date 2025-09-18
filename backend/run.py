#!/usr/bin/env python3
"""
Entry point script for running the FastAPI application.

This script exposes a module-level `app` so Uvicorn can import `backend.run:app`,
and also supports direct execution to start the development server.
"""

import sys
import os

# Add the backend directory to the Python path so we can import src as a package
backend_dir = os.path.dirname(__file__)
sys.path.insert(0, backend_dir)

# Expose module-level app for `uvicorn backend.run:app --reload`
from src.main import app  # noqa: E402  (import after sys.path manipulation)

# Support `python backend/run.py` direct execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info", access_log=True)
