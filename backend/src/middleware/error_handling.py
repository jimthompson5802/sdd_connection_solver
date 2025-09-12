"""
Error handling middleware and logging configuration for NYT Connections Puzzle Assistant.

This module provides comprehensive error handling middleware for the FastAPI application,
including request/response logging, exception handling, and structured error responses.
"""

import logging
import time
import traceback
import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive error handling middleware for the FastAPI application.

    Features:
    - Request/response logging with correlation IDs
    - Structured error responses
    - Exception classification and handling
    - Performance monitoring
    - Security headers
    """

    def __init__(self, app: ASGIApp, debug: bool = False):
        """
        Initialize error handling middleware.

        Args:
            app: ASGI application instance
            debug: Enable debug mode for detailed error responses
        """
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request through error handling middleware.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain

        Returns:
            Response object with proper error handling
        """
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Log request start
        start_time = time.time()
        self._log_request_start(request, correlation_id)

        try:
            # Process request
            response = await call_next(request)

            # Log successful response
            duration = time.time() - start_time
            self._log_request_success(request, response, correlation_id, duration)

            # Add security and correlation headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"

            return response

        except Exception as exc:
            # Handle and log exception
            duration = time.time() - start_time
            return await self._handle_exception(request, exc, correlation_id, duration)

    def _log_request_start(self, request: Request, correlation_id: str) -> None:
        """Log request start with details."""
        logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "content_type": request.headers.get("content-type", ""),
            },
        )

    def _log_request_success(self, request: Request, response: Response, correlation_id: str, duration: float) -> None:
        """Log successful request completion."""
        logger.info(
            "Request completed successfully",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "response_size": len(getattr(response, "body", b"")),
            },
        )

    async def _handle_exception(
        self, request: Request, exc: Exception, correlation_id: str, duration: float
    ) -> JSONResponse:
        """
        Handle exceptions and return structured error responses.

        Args:
            request: FastAPI request object
            exc: Exception that occurred
            correlation_id: Request correlation ID
            duration: Request duration in seconds

        Returns:
            JSONResponse with structured error information
        """
        # Log exception details
        self._log_exception(request, exc, correlation_id, duration)

        # Handle different exception types
        if isinstance(exc, HTTPException):
            return await self._handle_http_exception(exc, correlation_id)
        elif isinstance(exc, RequestValidationError):
            return await self._handle_validation_error(exc, correlation_id)
        elif isinstance(exc, ValidationError):
            return await self._handle_pydantic_validation_error(exc, correlation_id)
        else:
            return await self._handle_unexpected_exception(exc, correlation_id)

    def _log_exception(self, request: Request, exc: Exception, correlation_id: str, duration: float) -> None:
        """Log exception with context."""
        logger.error(
            "Request failed with exception",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration * 1000, 2),
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "client_ip": self._get_client_ip(request),
            },
            exc_info=True if not isinstance(exc, HTTPException) else False,
        )

    async def _handle_http_exception(self, exc: HTTPException, correlation_id: str) -> JSONResponse:
        """Handle HTTPException instances."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_exception",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "correlation_id": correlation_id,
                }
            },
            headers=getattr(exc, "headers", None),
        )

    async def _handle_validation_error(self, exc: RequestValidationError, correlation_id: str) -> JSONResponse:
        """Handle FastAPI validation errors."""
        error_details = []
        for error in exc.errors():
            error_details.append(
                {
                    "field": " -> ".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                    "input": error.get("input"),
                }
            )

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "validation_error",
                    "message": "Request validation failed",
                    "details": error_details,
                    "correlation_id": correlation_id,
                }
            },
        )

    async def _handle_pydantic_validation_error(self, exc: ValidationError, correlation_id: str) -> JSONResponse:
        """Handle Pydantic validation errors."""
        error_details = []
        for error in exc.errors():
            error_details.append(
                {
                    "field": " -> ".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "model_validation_error",
                    "message": "Data validation failed",
                    "details": error_details,
                    "correlation_id": correlation_id,
                }
            },
        )

    async def _handle_unexpected_exception(self, exc: Exception, correlation_id: str) -> JSONResponse:
        """Handle unexpected exceptions."""
        error_message = "Internal server error occurred"

        # Include stack trace in debug mode
        error_content = {
            "error": {
                "type": "internal_error",
                "message": error_message,
                "correlation_id": correlation_id,
            }
        }

        if self.debug:
            error_content["error"]["debug_info"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc(),
            }

        return JSONResponse(status_code=500, content=error_content)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return getattr(request.client, "host", "unknown")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request/response logging.

    Logs request/response bodies for debugging and audit purposes.
    """

    def __init__(self, app: ASGIApp, log_bodies: bool = False, max_body_size: int = 1024):
        """
        Initialize request logging middleware.

        Args:
            app: ASGI application instance
            log_bodies: Enable request/response body logging
            max_body_size: Maximum body size to log (bytes)
        """
        super().__init__(app)
        self.log_bodies = log_bodies
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through logging middleware."""
        # Log request body if enabled
        if self.log_bodies and request.method in ["POST", "PUT", "PATCH"]:
            await self._log_request_body(request)

        response = await call_next(request)

        # Log response body if enabled
        if self.log_bodies:
            await self._log_response_body(request, response)

        return response

    async def _log_request_body(self, request: Request) -> None:
        """Log request body content."""
        try:
            body = await request.body()
            if len(body) <= self.max_body_size:
                logger.debug(
                    "Request body",
                    extra={
                        "correlation_id": getattr(request.state, "correlation_id", "unknown"),
                        "body_size": len(body),
                        "body_content": body.decode("utf-8", errors="replace"),
                    },
                )
            else:
                logger.debug(
                    "Request body (truncated)",
                    extra={
                        "correlation_id": getattr(request.state, "correlation_id", "unknown"),
                        "body_size": len(body),
                        "body_content": body[: self.max_body_size].decode("utf-8", errors="replace"),
                        "truncated": True,
                    },
                )
        except Exception as e:
            logger.warning(f"Failed to log request body: {e}")

    async def _log_response_body(self, request: Request, response: Response) -> None:
        """Log response body content."""
        try:
            if hasattr(response, "body") and response.body:
                body = response.body
                if len(body) <= self.max_body_size:
                    logger.debug(
                        "Response body",
                        extra={
                            "correlation_id": getattr(request.state, "correlation_id", "unknown"),
                            "status_code": response.status_code,
                            "body_size": len(body),
                            "body_content": body.decode("utf-8", errors="replace"),
                        },
                    )
        except Exception as e:
            logger.warning(f"Failed to log response body: {e}")


# Utility functions for error handling


def create_error_response(
    status_code: int,
    error_type: str,
    message: str,
    correlation_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create standardized error response.

    Args:
        status_code: HTTP status code
        error_type: Error type identifier
        message: Human-readable error message
        correlation_id: Request correlation ID
        details: Additional error details

    Returns:
        JSONResponse with structured error format
    """
    content = {
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
        }
    }

    if correlation_id:
        content["error"]["correlation_id"] = correlation_id

    if details:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


def get_correlation_id(request: Request) -> str:
    """
    Get correlation ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        Correlation ID string
    """
    return getattr(request.state, "correlation_id", "unknown")


# Exception classes for specific error scenarios


class PuzzleValidationError(Exception):
    """Exception raised for puzzle validation errors."""

    pass


class SessionNotFoundError(Exception):
    """Exception raised when session is not found."""

    pass


class RecommendationError(Exception):
    """Exception raised for recommendation generation errors."""

    pass


class FileUploadError(Exception):
    """Exception raised for file upload errors."""

    pass
