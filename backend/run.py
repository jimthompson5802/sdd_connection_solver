#!/usr/bin/env python3
"""
Entry point script for running the FastAPI application.

This script handles the proper module imports and starts the application.
"""

import sys
import os

# Add the backend/src directory to the Python path
backend_src = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, backend_src)

# Now we can import and run the application
if __name__ == "__main__":
    from main import app
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info", access_log=True)
