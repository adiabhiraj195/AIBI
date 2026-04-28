"""
Knowledge Base Repository using SQLAlchemy ORM
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from app.database.connection import DatabaseConnection
from app.models.database_models import KnowledgeBase, DocumentMetadata, CSVDocument
from app.models.column_metadata import (
    KnowledgeBaseEntry, 
    ColumnMetadata,
    DocumentMetadataResponse
)
import logging

logger = logging.getLogger(__name__)

class KnowledgeBaseRepository:
    """Repository for knowledge base operations using SQLAlchemy ORM"""
    
    @staticmethod
    async def create_knowledge_entry(
        document_id: int,
        filename: str,
        summary: str,
        data_category: str,
        insights: List[str],
        use_cases: List[str],
        column_analysis: Dict[str, Any],
        data_quality_score: float,
        recommendations: List[str],
        column_metadata: List[ColumnMetadata]
    ) -> int:
        """Create knowledge base entry directly from LLM analysis"""
        try:
            session = DatabaseConnection.get_session()
            try:
                entry = KnowledgeBase(
                    document_id=document_id,
                    filename=filename,
                    summary=summary,
                    data_category=data_category,
                    insights=insights,
                    use_cases=use_cases,
                    column_analysis=column_analysis,
                    data_quality_score=data_quality_score,
                    recommendations=recommendations,
                    column_metadata=[col.dict() for col in column_metadata],
                )
                
                session.add(entry)
                session.commit()
                session.refresh(entry)
                
                logger.info(f"✅ Created knowledge base entry for document {document_id} (ID: {entry.id})")
                return entry.id
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error creating knowledge base entry: {e}")
            raise
    
    @staticmethod
    async def get_knowledge_base_entry_by_document_id(document_id: int) -> Optional[KnowledgeBaseEntry]:
        """Get knowledge base entry by document ID"""
        try:
            session = DatabaseConnection.get_session()
            try:
                entry = session.query(KnowledgeBase).filter(KnowledgeBase.document_id == document_id).first()
                
                if entry:
                    return KnowledgeBaseEntry(
                        id=entry.id,
                        document_id=entry.document_id,
                        filename=entry.filename,
                        summary=entry.summary,
                        data_category=entry.data_category,
                        insights=entry.insights,
                        use_cases=entry.use_cases,
                        column_analysis=entry.column_analysis,
                        data_quality_score=entry.data_quality_score,
                        recommendations=entry.recommendations,
                        created_at=str(entry.created_at),
                        updated_at=str(entry.updated_at)
                    )
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching knowledge base entry for document {document_id}: {e}")
            raise
    
    @staticmethod
    async def get_knowledge_base_entry_by_id(entry_id: int) -> Optional[KnowledgeBaseEntry]:
        """Get knowledge base entry by ID"""
        try:
            session = DatabaseConnection.get_session()
            try:
                entry = session.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
                
                if entry:
                    return KnowledgeBaseEntry(
                        id=entry.id,
                        document_id=entry.document_id,
                        filename=entry.filename,
                        summary=entry.summary,
                        data_category=entry.data_category,
                        insights=entry.insights,
                        use_cases=entry.use_cases,
                        column_analysis=entry.column_analysis,
                        data_quality_score=entry.data_quality_score,
                        recommendations=entry.recommendations,
                        created_at=str(entry.created_at),
                        updated_at=str(entry.updated_at)
                    )
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching knowledge base entry {entry_id}: {e}")
            raise
    
    @staticmethod
    async def list_knowledge_base_entries(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List knowledge base entries with summary info for frontend"""
        try:
            session = DatabaseConnection.get_session()
            try:
                entries = session.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).limit(limit).offset(offset).all()
                
                return [
                    {
                        "id": e.id,
                        "document_id": e.document_id,
                        "filename": e.filename,
                        "summary": e.summary,
                        "data_category": e.data_category,
                        "data_quality_score": e.data_quality_score,
                        "created_at": e.created_at
                    }
                    for e in entries
                ]
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error listing knowledge base entries: {e}")
            raise
    
    @staticmethod
    async def search_knowledge_base(query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search knowledge base entries by filename, summary, or category"""
        try:
            session = DatabaseConnection.get_session()
            try:
                search_pattern = f"%{query}%"
                entries = session.query(KnowledgeBase).filter(
                    (KnowledgeBase.filename.ilike(search_pattern)) |
                    (KnowledgeBase.summary.ilike(search_pattern)) |
                    (KnowledgeBase.data_category.ilike(search_pattern))
                ).order_by(KnowledgeBase.created_at.desc()).limit(limit).all()
                
                return [
                    {
                        "id": e.id,
                        "document_id": e.document_id,
                        "filename": e.filename,
                        "summary": e.summary,
                        "data_category": e.data_category,
                        "data_quality_score": e.data_quality_score,
                        "created_at": e.created_at
                    }
                    for e in entries
                ]
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            raise
    
    @staticmethod
    async def delete_knowledge_base_entry(entry_id: int) -> bool:
        """Delete a knowledge base entry"""
        try:
            session = DatabaseConnection.get_session()
            try:
                entry = session.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
                
                if entry:
                    session.delete(entry)
                    session.commit()
                    logger.info(f"Deleted knowledge base entry {entry_id}")
                    return True
                
                logger.warning(f"Knowledge base entry {entry_id} not found")
                return False
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error deleting knowledge base entry {entry_id}: {e}")
            raise


class DocumentMetadataRepository:
    """Repository for document metadata operations using SQLAlchemy ORM"""
    
    @staticmethod
    async def save_document_metadata(document_id: int, columns: List[ColumnMetadata]) -> Optional[DocumentMetadataResponse]:
        """Save document metadata (column information)"""
        try:
            session = DatabaseConnection.get_session()
            try:
                # Get document filename
                document = session.query(CSVDocument).filter(CSVDocument.id == document_id).first()
                if not document:
                    raise ValueError(f"Document with ID {document_id} not found")
                
                filename = document.filename
                
                # Check if metadata already exists
                existing = session.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).first()
                
                if existing:
                    # Update existing
                    existing.filename = filename
                    existing.column_metadata = [col.dict() for col in columns]
                    session.commit()
                    logger.info(f"Updated metadata for document {document_id}")
                    created_at = existing.created_at
                else:
                    # Create new
                    metadata = DocumentMetadata(
                        document_id=document_id,
                        filename=filename,
                        column_metadata=[col.dict() for col in columns],
                    )
                    session.add(metadata)
                    session.commit()
                    logger.info(f"Created metadata for document {document_id}")
                    created_at = metadata.created_at
                
                return DocumentMetadataResponse(
                    document_id=document_id,
                    filename=filename,
                    columns=columns,
                    created_at=str(created_at),
                    updated_at=str(existing.updated_at if existing else metadata.updated_at)
                )
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error saving document metadata: {e}")
            raise
    
    @staticmethod
    async def get_document_metadata(document_id: int) -> Optional[DocumentMetadataResponse]:
        """Get document metadata by document ID"""
        try:
            session = DatabaseConnection.get_session()
            try:
                entry = session.query(DocumentMetadata).filter(DocumentMetadata.document_id == document_id).first()
                
                if entry:
                    columns = [ColumnMetadata(**col) for col in entry.column_metadata]
                    return DocumentMetadataResponse(
                        document_id=entry.document_id,
                        filename=entry.filename,
                        columns=columns,
                        created_at=str(entry.created_at),
                        updated_at=str(entry.updated_at)
                    )
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching document metadata for document {document_id}: {e}")
            raise
