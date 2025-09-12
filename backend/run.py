#!/usr/bin/env python3
"""
Entry point script for running the FastAPI application.

This script handles the proper module imports and starts the application.
"""

import sys
import os

# Add the backend directory to the Python path so we can import src as a package
backend_dir = os.path.dirname(__file__)
sys.path.insert(0, backend_dir)

# Now we can import and run the application
if __name__ == "__main__":
    from src.main import app
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info", access_log=True)
