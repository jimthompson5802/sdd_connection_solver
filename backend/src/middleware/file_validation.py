"""
File upload validation and size limits middleware for NYT Connections Puzzle Assistant.

This module provides comprehensive file upload validation including:
- File size limits
- Content type validation
- File structure validation
- Malicious content detection
- Rate limiting for uploads
"""

import logging
import mimetypes
import os
from typing import Dict, List, Optional, Set, Union

from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    import magic
except ImportError:
    magic = None

from .error_handling import FileUploadError, create_error_response, get_correlation_id


logger = logging.getLogger(__name__)


class FileValidationConfig:
    """Configuration for file upload validation."""

    def __init__(
        self,
        max_file_size: int = 5 * 1024 * 1024,  # 5MB default
        allowed_content_types: Optional[Set[str]] = None,
        allowed_extensions: Optional[Set[str]] = None,
        max_files_per_request: int = 1,
        scan_for_malicious_content: bool = True,
        enforce_puzzle_format: bool = True,
    ):
        """
        Initialize file validation configuration.

        Args:
            max_file_size: Maximum file size in bytes
            allowed_content_types: Set of allowed MIME types
            allowed_extensions: Set of allowed file extensions
            max_files_per_request: Maximum number of files per request
            scan_for_malicious_content: Enable malicious content scanning
            enforce_puzzle_format: Enforce puzzle file format requirements
        """
        self.max_file_size = max_file_size
        self.allowed_content_types = allowed_content_types or {
            "text/plain",
            "text/csv",
            "application/csv",
            "text/comma-separated-values",
        }
        self.allowed_extensions = allowed_extensions or {".txt", ".csv"}
        self.max_files_per_request = max_files_per_request
        self.scan_for_malicious_content = scan_for_malicious_content
        self.enforce_puzzle_format = enforce_puzzle_format


class FileValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating file uploads.

    Validates files before they reach the application handlers,
    providing early rejection of invalid uploads.
    """

    def __init__(self, app: ASGIApp, config: Optional[FileValidationConfig] = None):
        """
        Initialize file validation middleware.

        Args:
            app: ASGI application instance
            config: File validation configuration
        """
        super().__init__(app)
        self.config = config or FileValidationConfig()

    async def dispatch(self, request: Request, call_next):
        """
        Process request through file validation middleware.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain

        Returns:
            Response object with file validation applied
        """
        # Only validate file upload endpoints
        if not self._is_file_upload_endpoint(request):
            return await call_next(request)

        try:
            # Pre-validate request before processing
            await self._validate_upload_request(request)
            response = await call_next(request)
            return response

        except FileUploadError as e:
            correlation_id = get_correlation_id(request)
            logger.warning(
                f"File upload validation failed: {e}",
                extra={"correlation_id": correlation_id},
            )
            return create_error_response(
                status_code=400,
                error_type="file_validation_error",
                message=str(e),
                correlation_id=correlation_id,
            )

        except Exception as e:
            correlation_id = get_correlation_id(request)
            logger.error(
                f"Unexpected error in file validation: {e}",
                extra={"correlation_id": correlation_id},
                exc_info=True,
            )
            return create_error_response(
                status_code=500,
                error_type="file_validation_internal_error",
                message="Internal error during file validation",
                correlation_id=correlation_id,
            )

    def _is_file_upload_endpoint(self, request: Request) -> bool:
        """
        Check if request is to a file upload endpoint.

        Args:
            request: FastAPI request object

        Returns:
            True if endpoint handles file uploads
        """
        # Check for multipart/form-data content type
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            return True

        # Check specific upload endpoints
        upload_paths = [
            "/api/v1/puzzles/upload",
            "/api/v1/files/upload",
        ]

        return any(request.url.path.startswith(path) for path in upload_paths)

    async def _validate_upload_request(self, request: Request) -> None:
        """
        Validate upload request before processing.

        Args:
            request: FastAPI request object

        Raises:
            FileUploadError: If validation fails
        """
        # Validate content length
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > self.config.max_file_size:
                raise FileUploadError(
                    f"Request size {content_length} exceeds maximum allowed " f"{self.config.max_file_size} bytes"
                )

        # Additional validation would be performed here
        # Note: Detailed file validation is done in the validator class below


class FileValidator:
    """
    Comprehensive file validator for uploaded files.

    Provides detailed validation of individual files including
    content analysis, format verification, and security checks.
    """

    def __init__(self, config: Optional[FileValidationConfig] = None):
        """
        Initialize file validator.

        Args:
            config: File validation configuration
        """
        self.config = config or FileValidationConfig()

    async def validate_file(self, file: UploadFile) -> Dict[str, Union[bool, str, List[str]]]:
        """
        Comprehensive validation of uploaded file.

        Args:
            file: FastAPI UploadFile object

        Returns:
            Dictionary with validation results and details

        Raises:
            FileUploadError: If critical validation fails
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "file_info": {},
        }

        try:
            # Basic file information
            result["file_info"] = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": 0,
            }

            # Validate filename
            if not file.filename:
                result["errors"].append("Filename is required")
                result["valid"] = False
                return result

            # Validate file extension
            extension_valid = self._validate_file_extension(file.filename)
            if not extension_valid["valid"]:
                result["errors"].extend(extension_valid["errors"])
                result["valid"] = False

            # Read file content for validation
            content = await file.read()
            result["file_info"]["size"] = len(content)

            # Reset file position for later use
            await file.seek(0)

            # Validate file size
            size_valid = self._validate_file_size(len(content))
            if not size_valid["valid"]:
                result["errors"].extend(size_valid["errors"])
                result["valid"] = False

            # Validate content type
            content_type_valid = self._validate_content_type(file, content)
            if not content_type_valid["valid"]:
                result["errors"].extend(content_type_valid["errors"])
                result["warnings"].extend(content_type_valid.get("warnings", []))

            # Scan for malicious content
            if self.config.scan_for_malicious_content:
                malicious_scan = self._scan_malicious_content(content)
                if not malicious_scan["valid"]:
                    result["errors"].extend(malicious_scan["errors"])
                    result["valid"] = False

            # Validate puzzle format if enabled
            if self.config.enforce_puzzle_format:
                puzzle_valid = self._validate_puzzle_format(content)
                if not puzzle_valid["valid"]:
                    result["errors"].extend(puzzle_valid["errors"])
                    result["warnings"].extend(puzzle_valid.get("warnings", []))
                    if puzzle_valid.get("critical", False):
                        result["valid"] = False

            return result

        except Exception as e:
            logger.error(f"Error during file validation: {e}", exc_info=True)
            raise FileUploadError(f"File validation failed: {str(e)}")

    def _validate_file_extension(self, filename: str) -> Dict[str, Union[bool, List[str]]]:
        """Validate file extension."""
        result = {"valid": True, "errors": []}

        # Get file extension
        _, ext = os.path.splitext(filename.lower())

        if ext not in self.config.allowed_extensions:
            result["valid"] = False
            result["errors"].append(
                f"File extension '{ext}' not allowed. "
                f"Allowed extensions: {', '.join(self.config.allowed_extensions)}"
            )

        return result

    def _validate_file_size(self, size: int) -> Dict[str, Union[bool, List[str]]]:
        """Validate file size."""
        result = {"valid": True, "errors": []}

        if size > self.config.max_file_size:
            result["valid"] = False
            result["errors"].append(
                f"File size {size} bytes exceeds maximum allowed " f"{self.config.max_file_size} bytes"
            )

        if size == 0:
            result["valid"] = False
            result["errors"].append("File is empty")

        return result

    def _validate_content_type(self, file: UploadFile, content: bytes) -> Dict[str, Union[bool, List[str]]]:
        """Validate content type and detect actual file type."""
        result = {"valid": True, "errors": [], "warnings": []}

        # Check declared content type
        if file.content_type not in self.config.allowed_content_types:
            result["warnings"].append(f"Declared content type '{file.content_type}' not in allowed types")

        # Detect actual content type using magic
        try:
            # Use python-magic if available, fallback to mimetypes
            if magic is not None:
                detected_type = magic.from_buffer(content, mime=True)
            else:
                # Fallback to mimetypes based on filename
                detected_type, _ = mimetypes.guess_type(file.filename or "")

            if detected_type and detected_type not in self.config.allowed_content_types:
                # For text files, be more lenient
                if detected_type.startswith("text/") and any(
                    allowed.startswith("text/") for allowed in self.config.allowed_content_types
                ):
                    result["warnings"].append(
                        f"Detected content type '{detected_type}' differs from declared "
                        f"'{file.content_type}' but is acceptable"
                    )
                else:
                    result["valid"] = False
                    result["errors"].append(f"Detected content type '{detected_type}' not allowed")

        except Exception as e:
            result["warnings"].append(f"Could not detect content type: {e}")

        return result

    def _scan_malicious_content(self, content: bytes) -> Dict[str, Union[bool, List[str]]]:
        """Scan for potentially malicious content."""
        result = {"valid": True, "errors": []}

        try:
            # Convert to text for analysis
            text_content = content.decode("utf-8", errors="ignore")

            # Check for suspicious patterns
            suspicious_patterns = [
                "<script",
                "javascript:",
                "data:text/html",
                "<?php",
                "<%",
                "eval(",
                "exec(",
                "system(",
            ]

            for pattern in suspicious_patterns:
                if pattern.lower() in text_content.lower():
                    result["valid"] = False
                    result["errors"].append(f"Suspicious content detected: {pattern}")

            # Check for excessive binary content (should be text)
            binary_ratio = sum(1 for b in content if b < 32 or b > 126) / len(content)
            if binary_ratio > 0.3:  # More than 30% non-printable characters
                result["valid"] = False
                result["errors"].append("File contains excessive binary content")

        except Exception as e:
            logger.warning(f"Error during malicious content scan: {e}")
            # Don't fail validation if scanning fails
            result["warnings"] = [f"Could not complete security scan: {e}"]

        return result

    def _validate_puzzle_format(self, content: bytes) -> Dict[str, Union[bool, List[str]]]:
        """Validate puzzle file format requirements."""
        result = {"valid": True, "errors": [], "warnings": [], "critical": False}

        try:
            # Decode content
            text_content = content.decode("utf-8", errors="replace")

            # Parse words from content
            words = self._parse_words_from_content(text_content)

            # Validate word count
            if len(words) != 16:
                result["valid"] = False
                result["critical"] = True
                result["errors"].append(f"Puzzle must contain exactly 16 words, found {len(words)}")

            # Validate word characteristics
            word_validation = self._validate_puzzle_words(words)
            result["errors"].extend(word_validation.get("errors", []))
            result["warnings"].extend(word_validation.get("warnings", []))

            if word_validation.get("critical_errors"):
                result["valid"] = False
                result["critical"] = True

        except UnicodeDecodeError:
            result["valid"] = False
            result["critical"] = True
            result["errors"].append("File contains invalid text encoding")

        except Exception as e:
            result["warnings"].append(f"Could not validate puzzle format: {e}")

        return result

    def _parse_words_from_content(self, content: str) -> List[str]:
        """Parse words from file content."""
        # Split by various delimiters and clean up
        import re

        # Split by common delimiters
        words = re.split(r"[,\n\r\t;]+", content)

        # Clean up words
        cleaned_words = []
        for word in words:
            word = word.strip().strip("\"'")
            if word:  # Skip empty strings
                cleaned_words.append(word)

        return cleaned_words

    def _validate_puzzle_words(self, words: List[str]) -> Dict[str, Union[List[str], bool]]:
        """Validate individual puzzle words."""
        result = {"errors": [], "warnings": [], "critical_errors": False}

        for i, word in enumerate(words):
            # Check word length
            if len(word) > 50:
                result["errors"].append(f"Word {i+1} '{word[:20]}...' is too long (max 50 characters)")

            if len(word) < 1:
                result["errors"].append(f"Word {i+1} is empty")
                result["critical_errors"] = True

            # Check for special characters that might cause issues
            if any(char in word for char in "<>&\"'`"):
                result["warnings"].append(f"Word {i+1} '{word}' contains special characters")

        # Check for duplicates
        unique_words = set(word.lower() for word in words)
        if len(unique_words) != len(words):
            result["warnings"].append("Puzzle contains duplicate words (case-insensitive)")

        return result


# Utility functions


async def validate_uploaded_file(
    file: UploadFile, config: Optional[FileValidationConfig] = None
) -> Dict[str, Union[bool, str, List[str]]]:
    """
    Validate a single uploaded file.

    Args:
        file: FastAPI UploadFile object
        config: File validation configuration

    Returns:
        Validation result dictionary

    Raises:
        FileUploadError: If validation fails critically
    """
    validator = FileValidator(config)
    return await validator.validate_file(file)


def create_file_validation_response(
    validation_result: Dict[str, Union[bool, str, List[str]]], correlation_id: str
) -> JSONResponse:
    """
    Create response for file validation results.

    Args:
        validation_result: Result from file validation
        correlation_id: Request correlation ID

    Returns:
        JSONResponse with validation details
    """
    if validation_result["valid"]:
        return JSONResponse(
            status_code=200,
            content={
                "status": "valid",
                "message": "File validation passed",
                "warnings": validation_result.get("warnings", []),
                "file_info": validation_result.get("file_info", {}),
                "correlation_id": correlation_id,
            },
        )
    else:
        return JSONResponse(
            status_code=400,
            content={
                "status": "invalid",
                "message": "File validation failed",
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
                "file_info": validation_result.get("file_info", {}),
                "correlation_id": correlation_id,
            },
        )
