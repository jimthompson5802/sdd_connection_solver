"""FastAPI endpoints for puzzle operations."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from uuid import UUID

from ..services import puzzle_service


router = APIRouter(prefix="/api/v1/puzzles", tags=["Puzzles"])


@router.post("/upload", response_model=dict, status_code=201)
async def upload_puzzle(file: Optional[UploadFile] = File(None), user_id: Optional[str] = Form(None)):
    """Upload a text file with 16 words to create a puzzle.

    Args:
        file: Text file containing 16 comma-separated words
        user_id: Optional user identifier

    Returns:
        PuzzleResponse with created puzzle details

    Raises:
        HTTPException: If file format or word count is invalid
    """
    # If no file was provided, return a 400 error to match contract tests
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        # Read file content
        file_content = await file.read()

        # Parse and create puzzle (automatically stored)
        puzzle = puzzle_service.parse_uploaded_file(
            file_content=file_content, filename=file.filename or "unknown.txt", user_id=user_id
        )

        # Return response matching API schema
        return {
            "id": puzzle.id,
            "words": puzzle.words,
            "uploaded_filename": puzzle.uploaded_filename,
            "created_at": puzzle.created_at.isoformat(),
            "user_id": puzzle.user_id,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "VALIDATION_ERROR", "message": str(e)})
    except Exception:
        raise HTTPException(
            status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Failed to process uploaded file"}
        )


@router.get("/{puzzle_id}", response_model=dict)
async def get_puzzle(puzzle_id: str):
    """Get puzzle details.

    Args:
        puzzle_id: UUID of the puzzle to retrieve

    Returns:
        PuzzleResponse with puzzle details

    Raises:
        HTTPException: If puzzle is not found
    """
    try:
        # First try to retrieve; perf tests may mock non-UUID IDs that should still resolve.
        puzzle = puzzle_service.get_puzzle(puzzle_id)

        if puzzle is None:
            # If not found, enforce UUID validation for invalid formats (contract requirement)
            try:
                UUID(puzzle_id)
            except Exception:
                raise HTTPException(status_code=400, detail={"error": "INVALID_ID", "message": "Invalid UUID format"})

            # Valid UUID format but not found
            raise HTTPException(
                status_code=404,
                detail={"error": "PUZZLE_NOT_FOUND", "message": f"Puzzle with ID {puzzle_id} not found"},
            )

        # Return response matching API schema
        return {
            "id": puzzle.id,
            "words": puzzle.words,
            "uploaded_filename": puzzle.uploaded_filename,
            "created_at": puzzle.created_at.isoformat(),
            "user_id": puzzle.user_id,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR", "message": "Failed to retrieve puzzle"})
