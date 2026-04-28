"""
Repository for FileRegistry table operations
Manages tracking of all uploaded files and their dynamic tables
"""
import logging
from typing import Optional, List
from app.models.database_models import FileRegistry
from app.database.connection import DatabaseConnection
from sqlalchemy import select, update
from datetime import datetime

logger = logging.getLogger(__name__)


class FileRegistryRepository:
    """Repository for file registry operations"""
    
    @staticmethod
    async def register_file(
        document_id: int,
        filename: str,
        row_count: int,
        column_count: int,
        file_type: str = "csv"
    ) -> FileRegistry:
        """Register a newly uploaded file in the registry"""
        try:
            session = DatabaseConnection.get_session()
            
            registry_entry = FileRegistry(
                document_id=document_id,
                filename=filename,
                file_type=file_type,
                row_count=row_count,
                column_count=column_count,
                is_described=False,
                upload_date=datetime.utcnow()
            )
            
            session.add(registry_entry)
            session.commit()
            session.refresh(registry_entry)
            
            logger.info(f"✅ Registered file: {filename} (Doc ID: {document_id})")
            return registry_entry
            
        except Exception as e:
            logger.error(f"❌ Error registering file {filename}: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    async def update_dynamic_table(
        document_id: int,
        dynamic_table_name: str,
        data_category: Optional[str] = None
    ) -> bool:
        """Update registry entry with dynamic table information"""
        try:
            session = DatabaseConnection.get_session()
            
            stmt = update(FileRegistry).where(
                FileRegistry.document_id == document_id
            ).values(
                dynamic_table_name=dynamic_table_name,
                table_created_at=datetime.utcnow(),
                data_category=data_category
            )
            
            result = session.execute(stmt)
            session.commit()
            
            logger.info(f"✅ Updated dynamic table for Doc {document_id}: {dynamic_table_name}")
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"❌ Error updating dynamic table for Doc {document_id}: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    async def mark_as_described(
        document_id: int,
        is_described: bool = True
    ) -> bool:
        """Mark a file as verified/described by user"""
        try:
            session = DatabaseConnection.get_session()
            
            stmt = update(FileRegistry).where(
                FileRegistry.document_id == document_id
            ).values(
                is_described=is_described,
                verified_at=datetime.utcnow() if is_described else None
            )
            
            result = session.execute(stmt)
            session.commit()
            
            status = "verified" if is_described else "unverified"
            logger.info(f"✅ Marked Doc {document_id} as {status}")
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"❌ Error updating is_described for Doc {document_id}: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    async def get_registry_entry(document_id: int) -> Optional[FileRegistry]:
        """Get registry entry for a document"""
        try:
            session = DatabaseConnection.get_session()
            
            stmt = select(FileRegistry).where(FileRegistry.document_id == document_id)
            result = session.execute(stmt)
            entry = result.scalars().first()
            
            return entry
            
        except Exception as e:
            logger.error(f"❌ Error fetching registry entry for Doc {document_id}: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    async def list_all_files(
        limit: int = 100,
        offset: int = 0,
        only_verified: bool = False
    ) -> List[FileRegistry]:
        """List all registered files"""
        try:
            session = DatabaseConnection.get_session()
            
            stmt = select(FileRegistry)
            
            if only_verified:
                stmt = stmt.where(FileRegistry.is_described == True)
            
            stmt = stmt.offset(offset).limit(limit).order_by(FileRegistry.upload_date.desc())
            
            result = session.execute(stmt)
            entries = result.scalars().all()
            
            return entries
            
        except Exception as e:
            logger.error(f"❌ Error listing files: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    async def get_files_by_category(category: str) -> List[FileRegistry]:
        """Get all files in a specific data category"""
        try:
            session = DatabaseConnection.get_session()
            
            stmt = select(FileRegistry).where(
                FileRegistry.data_category == category
            ).order_by(FileRegistry.upload_date.desc())
            
            result = session.execute(stmt)
            entries = result.scalars().all()
            
            return entries
            
        except Exception as e:
            logger.error(f"❌ Error fetching files by category {category}: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    async def get_registry_summary() -> dict:
        """Get summary statistics of registered files"""
        try:
            session = DatabaseConnection.get_session()
            
            # Total files
            total_result = session.execute(select(FileRegistry))
            total_files = len(total_result.scalars().all())
            
            # Verified files
            verified_result = session.execute(
                select(FileRegistry).where(FileRegistry.is_described == True)
            )
            verified_files = len(verified_result.scalars().all())
            
            # Files with dynamic tables
            with_tables_result = session.execute(
                select(FileRegistry).where(FileRegistry.dynamic_table_name.isnot(None))
            )
            with_tables = len(with_tables_result.scalars().all())
            
            return {
                "total_files": total_files,
                "verified_files": verified_files,
                "with_dynamic_tables": with_tables,
                "unverified_files": total_files - verified_files,
                "without_tables": total_files - with_tables
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting registry summary: {e}")
            raise
        finally:
            session.close()
