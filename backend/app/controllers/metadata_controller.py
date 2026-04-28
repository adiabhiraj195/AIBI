from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from app.services.metadata_service import MetadataService
from app.models.column_metadata import (
    ColumnMetadata,
    DocumentMetadataRequest,
    DocumentMetadataResponse,
    ProcessDocumentRequest,
    ProcessDocumentResponse,
    KnowledgeBaseEntry,
    ColumnExtractionResponse,
    KnowledgeBaseSummary
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metadata", tags=["Document Metadata & Knowledge Base"])

def get_metadata_service() -> MetadataService:
    """Dependency to get MetadataService instance"""
    return MetadataService()

# Frontend-focused endpoints

@router.get(
    "/extract/{document_id}",
    response_model=ColumnExtractionResponse,
    summary="Extract Column Information",
    description="Extract column names, data types, and sample data for frontend form"
)
async def extract_document_info(
    document_id: int,
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    Extract basic column information for frontend metadata form.
    
    - **document_id**: ID of the CSV document
    - Returns: Column info with sample data for user to fill metadata
    """
    try:
        result = await metadata_service.extract_document_info_for_frontend(document_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error extracting document info for {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while extracting document info")

@router.post(
    "/save",
    response_model=DocumentMetadataResponse,
    summary="Save Complete Metadata",
    description="Save complete column metadata with all user inputs"
)
async def save_complete_metadata(
    request: DocumentMetadataRequest,
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    Save complete document metadata with all user-provided information.
    
    - **request**: Complete metadata with column descriptions, aliases, connection keys
    - Returns: Saved metadata confirmation
    """
    try:
        result = await metadata_service.save_document_metadata(request)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while saving metadata")

@router.post(
    "/process/{document_id}",
    response_model=ProcessDocumentResponse,
    summary="Process with AI",
    description="Process document metadata with LLM and create knowledge base entry"
)
async def process_document_with_ai(
    document_id: int,
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    Process saved document metadata with AI and create knowledge base entry.
    
    - **document_id**: ID of the CSV document (must have saved metadata)
    - Returns: Processing result with knowledge base entry ID
    """
    try:
        result = await metadata_service.process_document_with_ai(document_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing document {document_id} with AI: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing with AI")

@router.get(
    "/knowledge-base",
    response_model=List[KnowledgeBaseSummary],
    summary="List Knowledge Base",
    description="Get paginated list of knowledge base entries for frontend display"
)
async def list_knowledge_base(
    limit: int = Query(20, description="Number of entries to return", ge=1, le=100),
    offset: int = Query(0, description="Number of entries to skip", ge=0),
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    List knowledge base entries with summary information for frontend.
    
    - **limit**: Number of entries to return (1-100)
    - **offset**: Number of entries to skip for pagination
    - Returns: List of knowledge base summaries
    """
    try:
        entries = await metadata_service.list_knowledge_base_summaries(limit, offset)
        return entries
        
    except Exception as e:
        logger.error(f"Unexpected error listing knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while listing knowledge base")

@router.get(
    "/knowledge-base/{document_id}",
    response_model=KnowledgeBaseEntry,
    summary="Get Knowledge Base Entry",
    description="Get complete knowledge base entry for a specific document"
)
async def get_knowledge_base_entry(
    document_id: int,
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    Get complete knowledge base entry for a document.
    
    - **document_id**: ID of the CSV document
    - Returns: Complete knowledge base entry with analysis
    """
    try:
        entry = await metadata_service.get_knowledge_base_entry(document_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Knowledge base entry not found")
        
        return entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching knowledge base entry for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching knowledge base entry")

@router.get(
    "/knowledge-base/search",
    response_model=List[KnowledgeBaseSummary],
    summary="Search Knowledge Base",
    description="Search knowledge base entries by filename, summary, or category"
)
async def search_knowledge_base(
    query: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(20, description="Maximum number of results", ge=1, le=50),
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    Search knowledge base entries for frontend.
    
    - **query**: Search query string
    - **limit**: Maximum number of results (1-50)
    - Returns: List of matching knowledge base summaries
    """
    try:
        entries = await metadata_service.search_knowledge_base(query, limit)
        return entries
        
    except Exception as e:
        logger.error(f"Unexpected error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while searching knowledge base")

@router.get(
    "/document/{document_id}",
    response_model=DocumentMetadataResponse,
    summary="Get Saved Metadata",
    description="Get previously saved document metadata"
)
async def get_saved_metadata(
    document_id: int,
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    Get saved document metadata.
    
    - **document_id**: ID of the CSV document
    - Returns: Saved metadata if exists
    """
    try:
        metadata = await metadata_service.get_document_metadata(document_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Document metadata not found")
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching metadata for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching metadata")

@router.delete(
    "/knowledge-base/{entry_id}",
    summary="Delete Knowledge Base Entry",
    description="Delete a knowledge base entry"
)
async def delete_knowledge_base_entry(
    entry_id: int,
    metadata_service: MetadataService = Depends(get_metadata_service)
):
    """
    Delete a knowledge base entry.
    
    - **entry_id**: ID of the knowledge base entry to delete
    - Returns: Success confirmation
    """
    try:
        success = await metadata_service.delete_knowledge_base_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge base entry not found")
        
        return {"success": True, "message": "Knowledge base entry deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting knowledge base entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while deleting entry")

# File Registry Endpoints

@router.get(
    "/registry/summary",
    summary="Get File Registry Summary",
    description="Get summary statistics of all registered files"
)
async def get_registry_summary():
    """
    Get a summary of all registered files:
    - Total files uploaded
    - Verified files (user has reviewed metadata)
    - Files with dynamic tables created
    """
    try:
        from app.repositories.file_registry_repository import FileRegistryRepository
        summary = await FileRegistryRepository.get_registry_summary()
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting registry summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get registry summary")

@router.get(
    "/registry/files",
    summary="List All Registered Files",
    description="Get list of all uploaded and registered files with their metadata"
)
async def list_registered_files(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    verified_only: bool = Query(False, description="Show only verified files")
):
    """
    Get list of all registered files with details:
    - File ID, name, and type
    - Dynamic table name if created
    - Data category from LLM analysis
    - Row/column counts
    - is_described flag (user verified)
    - Upload date and table creation date
    """
    try:
        from app.repositories.file_registry_repository import FileRegistryRepository
        entries = await FileRegistryRepository.list_all_files(limit, offset, verified_only)
        
        return {
            "success": True,
            "count": len(entries),
            "files": [entry.to_dict() for entry in entries]
        }
        
    except Exception as e:
        logger.error(f"Error listing registered files: {e}")
        raise HTTPException(status_code=500, detail="Failed to list registered files")

@router.get(
    "/registry/file/{document_id}",
    summary="Get File Registry Entry",
    description="Get detailed registry information for a specific file"
)
async def get_file_registry(document_id: int):
    """
    Get complete registry information for a file including:
    - Upload metadata
    - Dynamic table details
    - Verification status
    """
    try:
        from app.repositories.file_registry_repository import FileRegistryRepository
        entry = await FileRegistryRepository.get_registry_entry(document_id)
        
        if not entry:
            raise HTTPException(status_code=404, detail=f"File registry entry for document {document_id} not found")
        
        return {
            "success": True,
            "file": entry.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting registry entry for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get registry entry")

@router.get(
    "/registry/category/{category}",
    summary="Get Files by Category",
    description="Get all files in a specific data category"
)
async def get_files_by_category(category: str):
    """
    Get all files that belong to a specific data category (determined by LLM analysis).
    Examples: "Financial", "Customer Data", "Sales", "Operations", etc.
    """
    try:
        from app.repositories.file_registry_repository import FileRegistryRepository
        entries = await FileRegistryRepository.get_files_by_category(category)
        
        return {
            "success": True,
            "category": category,
            "count": len(entries),
            "files": [entry.to_dict() for entry in entries]
        }
        
    except Exception as e:
        logger.error(f"Error getting files for category {category}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get files by category")