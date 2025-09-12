"""
Middleware package for NYT Connections Puzzle Assistant.

This package contains middleware components for request/response processing,
error handling, and file validation.
"""

from .error_handling import (
    ErrorHandlingMiddleware,
    RequestLoggingMiddleware,
    create_error_response,
    get_correlation_id,
    PuzzleValidationError,
    SessionNotFoundError,
    RecommendationError,
    FileUploadError,
)

from .file_validation import (
    FileValidationMiddleware,
    FileValidator,
    FileValidationConfig,
    validate_uploaded_file,
    create_file_validation_response,
)

__all__ = [
    "ErrorHandlingMiddleware",
    "RequestLoggingMiddleware",
    "create_error_response",
    "get_correlation_id",
    "PuzzleValidationError",
    "SessionNotFoundError",
    "RecommendationError",
    "FileUploadError",
    "FileValidationMiddleware",
    "FileValidator",
    "FileValidationConfig",
    "validate_uploaded_file",
    "create_file_validation_response",
]
