"""
FastAPI application entry point for NYT Connections Puzzle Assistant

This file will be populated with the main FastAPI application setup
in subsequent tasks (T002).
"""

from fastapi import FastAPI

app = FastAPI(
    title="NYT Connections Puzzle Assistant",
    description="Web application for solving NYT Connections puzzles with AI assistance",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "NYT Connections Puzzle Assistant API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
