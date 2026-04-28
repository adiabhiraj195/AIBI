"""
CSV Document Repository using SQLAlchemy ORM
"""
from typing import List, Optional
from sqlalchemy import select
from app.database.connection import DatabaseConnection
from app.models.database_models import CSVDocument
from app.models.csv_document import CSVDocumentCreate, CSVDocumentResponse, CSVDocumentDetail, CSVDocumentList
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CSVRepository:
    """Repository for CSV document operations using SQLAlchemy ORM"""
    
    @staticmethod
    async def create_document(document_data: CSVDocumentCreate) -> Optional[CSVDocumentResponse]:
        """Create a new CSV document in the database"""
        try:
            from app.repositories.file_registry_repository import FileRegistryRepository
            
            session = DatabaseConnection.get_session()
            try:
                # Create new document
                document = CSVDocument(
                    filename=document_data.filename,
                    preview_data=document_data.preview_data,
                    full_data=document_data.full_data,
                    is_described=False,
                    row_count=document_data.row_count,
                    column_count=document_data.column_count,
                    upload_date=datetime.utcnow(),
                )
                
                session.add(document)
                session.commit()
                session.refresh(document)
                
                logger.info(f"✅ Created CSV document: {document.filename} (ID: {document.id})")
                
                # Register file in the file registry
                try:
                    await FileRegistryRepository.register_file(
                        document_id=document.id,
                        filename=document.filename,
                        row_count=document.row_count,
                        column_count=document.column_count,
                        file_type="csv"
                    )
                except Exception as e:
                    logger.error(f"⚠️ Failed to register file in registry: {e}")
                    # Don't fail the upload if registry fails, just log it
                
                return CSVDocumentResponse(
                    id=document.id,
                    filename=document.filename,
                    preview=document.preview_data,
                    is_described=bool(document.is_described),
                    row_count=document.row_count,
                    column_count=document.column_count,
                    upload_date=str(document.upload_date),
                )
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    @staticmethod
    async def document_exists_by_filename(filename: str) -> bool:
        """Check if a CSV document exists for the given filename"""
        try:
            session = DatabaseConnection.get_session()
            try:
                stmt = select(CSVDocument).where(CSVDocument.filename == filename).limit(1)
                result = session.execute(stmt).first()
                exists = result is not None
                logger.info(f"Document check for '{filename}': {'exists' if exists else 'not found'}")
                return exists
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error checking document existence for filename '{filename}': {e}")
            raise
    
    @staticmethod
    async def get_document_by_id(document_id: int) -> Optional[CSVDocumentDetail]:
        """Get a CSV document by ID with full data"""
        try:
            session = DatabaseConnection.get_session()
            try:
                document = session.query(CSVDocument).filter(CSVDocument.id == document_id).first()
                
                if document:
                    return CSVDocumentDetail(
                        id=document.id,
                        filename=document.filename,
                        preview=document.preview_data,
                        full_data=document.full_data,
                        is_described=bool(document.is_described),
                        row_count=document.row_count,
                        column_count=document.column_count,
                        upload_date=str(document.upload_date),
                    )
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching document {document_id}: {e}")
            raise
    
    @staticmethod
    async def get_document_preview_by_id(document_id: int) -> Optional[CSVDocumentResponse]:
        """Get a CSV document by ID with preview data only"""
        try:
            session = DatabaseConnection.get_session()
            try:
                document = session.query(CSVDocument).filter(CSVDocument.id == document_id).first()
                
                if document:
                    return CSVDocumentResponse(
                        id=document.id,
                        filename=document.filename,
                        preview=document.preview_data,
                        is_described=bool(document.is_described),
                        row_count=document.row_count,
                        column_count=document.column_count,
                        upload_date=str(document.upload_date),
                    )
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error fetching document preview {document_id}: {e}")
            raise
    
    @staticmethod
    async def list_documents(limit: int = 100, offset: int = 0) -> List[CSVDocumentList]:
        """List all CSV documents with pagination"""
        try:
            from sqlalchemy import select
            
            session = DatabaseConnection.get_session()
            try:
                # Use synchronous SQLAlchemy 2.0 style (with select statement)
                stmt = select(CSVDocument).order_by(CSVDocument.upload_date.desc()).limit(limit).offset(offset)
                result = session.execute(stmt)
                documents = result.scalars().all()
                
                return [
                    CSVDocumentList(
                        id=doc.id,
                        filename=doc.filename,
                        upload_date=str(doc.upload_date),
                        is_described=bool(doc.is_described),
                        row_count=doc.row_count,
                        column_count=doc.column_count,
                    )
                    for doc in documents
                ]
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error listing documents: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def update_document_description_status(document_id: int, is_described: bool) -> bool:
        """Update the description status of a document"""
        try:
            session = DatabaseConnection.get_session()
            try:
                document = session.query(CSVDocument).filter(CSVDocument.id == document_id).first()
                
                if document:
                    document.is_described = bool(is_described)
                    session.commit()
                    logger.info(f"Updated description status for document {document_id}")
                    return True
                
                logger.warning(f"Document {document_id} not found")
                return False
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            raise
    
    @staticmethod
    async def delete_document(document_id: int) -> bool:
        """Delete a CSV document and its related entries including dynamic table"""
        try:
            session = DatabaseConnection.get_session()
            try:
                from sqlalchemy import text
                
                # First, get the dynamic table name from file_registry before deletion
                dynamic_table_name = None
                try:
                    get_table_name = text(
                        "SELECT dynamic_table_name FROM file_registry WHERE document_id = :document_id"
                    )
                    result = session.execute(get_table_name, {"document_id": document_id})
                    row = result.fetchone()
                    if row and row[0]:
                        dynamic_table_name = row[0]
                        logger.info(f"Found dynamic table to delete: {dynamic_table_name}")
                except Exception as e:
                    logger.warning(f"Could not retrieve dynamic table name for document {document_id}: {e}")
                
                # Drop the dynamic table if it exists
                if dynamic_table_name:
                    try:
                        drop_table_query = text(f'DROP TABLE IF EXISTS "{dynamic_table_name}" CASCADE')
                        session.execute(drop_table_query)
                        logger.info(f"✅ Dropped dynamic table: {dynamic_table_name}")
                    except Exception as e:
                        logger.error(f"❌ Failed to drop dynamic table {dynamic_table_name}: {e}")
                        # Don't fail the entire deletion if table drop fails
                
                # Delete related file_registry entries
                delete_file_registry = text(
                    "DELETE FROM file_registry WHERE document_id = :document_id"
                )
                session.execute(delete_file_registry, {"document_id": document_id})
                
                # Then delete the document itself
                document = session.query(CSVDocument).filter(CSVDocument.id == document_id).first()
                
                if document:
                    session.delete(document)
                    session.commit()
                    logger.info(f"✅ Deleted document {document_id} and related entries")
                    return True
                
                session.commit()
                logger.warning(f"Document {document_id} not found, but related entries were cleaned up")
                return True
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
