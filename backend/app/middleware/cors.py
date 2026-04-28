from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to the FastAPI app"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this for production
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )