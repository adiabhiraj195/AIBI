from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class CSVDocumentBase(BaseModel):
    filename: str = Field(..., description="Name of the uploaded CSV file")
    is_described: bool = Field(default=False, description="Whether the document has been described")

class CSVDocumentCreate(CSVDocumentBase):
    preview_data: List[Dict[str, Any]] = Field(..., description="Preview data (first 5 rows)")
    full_data: List[Dict[str, Any]] = Field(..., description="Complete CSV data")
    row_count: int = Field(..., gt=0, description="Total number of rows")
    column_count: int = Field(..., gt=0, description="Total number of columns")

class CSVDocumentResponse(CSVDocumentBase):
    id: int = Field(..., description="Unique document identifier")
    preview: List[Dict[str, Any]] = Field(..., description="Preview data (first 5 rows)")
    row_count: int = Field(..., description="Total number of rows")
    column_count: int = Field(..., description="Total number of columns")
    upload_date: datetime = Field(..., description="Upload timestamp")

class CSVDocumentDetail(CSVDocumentResponse):
    full_data: Optional[List[Dict[str, Any]]] = Field(None, description="Complete CSV data")

class CSVDocumentList(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    is_described: bool
    row_count: int
    column_count: int

class UploadResponse(BaseModel):
    success: bool = Field(..., description="Upload success status")
    data: List[CSVDocumentResponse] = Field(..., description="Uploaded documents data")
    message: str = Field(..., description="Response message")

class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Operation success status")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")