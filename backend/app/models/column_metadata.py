from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ColumnMetadata(BaseModel):
    column_name: str = Field(..., description="Name of the column")
    data_type: str = Field(..., description="Data type of the column (string, integer, float, boolean, date)")
    connection_key: Optional[str] = Field(None, description="Connection key to link with other CSV files")
    alias: Optional[str] = Field(None, description="User-friendly alias for the column")
    description: str = Field(..., description="Detailed description of what this column represents")

class DocumentMetadataRequest(BaseModel):
    document_id: int = Field(..., description="ID of the CSV document")
    columns: List[ColumnMetadata] = Field(..., description="Complete column metadata with all required fields")

class DocumentMetadataResponse(BaseModel):
    document_id: int = Field(..., description="ID of the CSV document")
    filename: str = Field(..., description="Name of the CSV file")
    columns: List[ColumnMetadata] = Field(..., description="Column metadata information")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class KnowledgeBaseEntry(BaseModel):
    id: int = Field(..., description="Knowledge base entry ID")
    document_id: int = Field(..., description="Referenced CSV document ID")
    filename: str = Field(..., description="CSV filename")
    summary: str = Field(..., description="Brief summary of the dataset")
    data_category: str = Field(..., description="Category/domain of the data")
    insights: List[str] = Field(..., description="Key insights about the data")
    use_cases: List[str] = Field(..., description="Potential use cases for this dataset")
    column_analysis: Dict[str, Any] = Field(..., description="Detailed analysis of each column")
    data_quality_score: float = Field(..., description="Overall data quality score (0-100)")
    recommendations: List[str] = Field(..., description="Recommendations for data usage")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class ProcessDocumentRequest(BaseModel):
    document_id: int = Field(..., description="CSV document ID to process")
    columns: List[ColumnMetadata] = Field(..., description="Complete column metadata with descriptions")

class ProcessDocumentResponse(BaseModel):
    success: bool = Field(..., description="Processing success status")
    knowledge_base_id: int = Field(..., description="Created knowledge base entry ID")
    message: str = Field(..., description="Response message")
    summary: str = Field(..., description="Brief summary of the analysis")

# Frontend-focused models
class ColumnExtractionResponse(BaseModel):
    document_id: int = Field(..., description="Document ID")
    filename: str = Field(..., description="CSV filename")
    columns: List[Dict[str, str]] = Field(..., description="Basic column info (name and inferred type)")
    total_columns: int = Field(..., description="Total number of columns")
    sample_data: List[Dict[str, Any]] = Field(..., description="First few rows for reference")

class KnowledgeBaseSummary(BaseModel):
    id: int = Field(..., description="Knowledge base entry ID")
    document_id: int = Field(..., description="Document ID")
    filename: str = Field(..., description="CSV filename")
    summary: str = Field(..., description="Brief summary")
    data_category: str = Field(..., description="Data category")
    data_quality_score: float = Field(..., description="Quality score")
    created_at: datetime = Field(..., description="Creation date")