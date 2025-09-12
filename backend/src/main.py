"""
FastAPI application entry point for NYT Connections Puzzle Assistant.

This module sets up the main FastAPI application with:
- CORS middleware for cross-origin requests
- Error handling middleware
- API router integration
- Health check endpoints
- Comprehensive logging configuration
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Import API routers
from .api.puzzles import router as puzzles_router
from .api.sessions import router as sessions_router
from .api.recommendations import router as recommendations_router
from .api.history import router as history_router

# Import WebSocket handlers
from .websockets.recommendation_handler import RecommendationWebSocketHandler
from .services.session_service import SessionService
from .services.llm_service import LLMService
from .services.context_service import ContextService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info("Starting NYT Connections Puzzle Assistant API")
    logger.info("Initializing services and middleware")

    yield

    # Shutdown
    logger.info("Shutting down NYT Connections Puzzle Assistant API")


# Create FastAPI application with lifespan events
app = FastAPI(
    title="NYT Connections Puzzle Assistant API",
    description="Backend API for the NYT Connections puzzle solving web application with AI assistance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development server
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:5173",
        # Add production URLs as needed
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.localhost",
        "testserver",  # Allow TestClient requests
        # Add production domains as needed
    ],
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for request validation errors.

    Returns structured error responses for validation failures.
    """
    logger.warning(f"Validation error on {request.url}: {exc}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": exc.errors(), "body": str(exc.body) if hasattr(exc, "body") else None},
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTP exceptions.

    Ensures consistent error response format across all endpoints.
    """
    logger.warning(f"HTTP exception on {request.url}: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """
    Custom handler for internal server errors.

    Logs the full exception and returns a safe error response.
    """
    logger.error(f"Internal server error on {request.url}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500, content={"error": "INTERNAL_SERVER_ERROR", "message": "An internal server error occurred"}
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests and responses.

    Logs request method, URL, processing time, and response status.
    """
    import time

    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f"Response: {response.status_code} for {request.method} {request.url} " f"(processed in {process_time:.4f}s)"
    )

    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Include API routers
app.include_router(puzzles_router)
app.include_router(sessions_router)
app.include_router(recommendations_router)
app.include_router(history_router)


# Initialize services for WebSocket
session_service = SessionService()
llm_service = LLMService()
context_service = ContextService()
websocket_handler = RecommendationWebSocketHandler(session_service, llm_service, context_service)


# WebSocket endpoint for real-time recommendations
@app.websocket("/ws/sessions/{session_id}/recommendations")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time AI recommendations.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier for the connection
    """
    await websocket_handler.handle_connection(websocket, session_id)


# Root endpoint
@app.get("/", response_model=Dict[str, Any])
async def root():
    """
    Root endpoint returning API information.

    Returns:
        Basic API information and available endpoints
    """
    return {
        "message": "NYT Connections Puzzle Assistant API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {"docs": "/docs", "redoc": "/redoc", "openapi": "/openapi.json", "health": "/health"},
    }


# Health check endpoint
@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Application health status and basic system information
    """
    import psutil
    import sys

    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        from datetime import datetime

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "system": {
                "python_version": sys.version,
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
            },
            "services": {
                "puzzle_service": "operational",
                "session_service": "operational",
                "llm_service": "operational",
                "evaluation_service": "operational",
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


# Application is ready to be imported and run via uvicorn
# Use: uvicorn backend.src.main:app --reload
# Or use the run.py script in the backend directory
