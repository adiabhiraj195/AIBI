#!/usr/bin/env python3
"""
Test script to verify /api/v1/metadata/process/{document_id} endpoint
creates dynamic table and inserts full_data from csv_documents
"""

import asyncio
import logging
from app.database.connection import DatabaseConnection
from app.repositories.csv_repository import CSVRepository
from app.repositories.knowledge_base_repository import DocumentMetadataRepository
from app.services.metadata_service import MetadataService
from app.models.column_metadata import ColumnMetadata
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_process_endpoint_flow(document_id: int):
    """
    Test the complete flow:
    1. Get document with full_data
    2. Check if metadata exists
    3. Call metadata service process (which creates table)
    4. Verify table exists and has data
    """
    
    try:
        # Step 1: Get document and verify full_data
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing process endpoint for document {document_id}")
        logger.info(f"{'='*60}\n")
        
        document = await CSVRepository.get_document_by_id(document_id)
        if not document:
            logger.error(f"❌ Document {document_id} not found")
            return False
        
        logger.info(f"✅ Document found: {document.filename}")
        logger.info(f"   - Row count: {document.row_count}")
        logger.info(f"   - Column count: {document.column_count}")
        logger.info(f"   - Has full_data: {document.full_data is not None}")
        
        if document.full_data:
            data_len = len(document.full_data) if isinstance(document.full_data, list) else 0
            logger.info(f"   - Full data rows: {data_len}")
        
        # Step 2: Check metadata
        metadata = await DocumentMetadataRepository.get_document_metadata(document_id)
        if not metadata:
            logger.warning(f"⚠️ No metadata found for document {document_id}")
            logger.warning(f"   You need to save metadata first via /api/v1/metadata/save")
            return False
        
        logger.info(f"✅ Metadata found with {len(metadata.columns)} columns:")
        for col in metadata.columns[:3]:  # Show first 3
            logger.info(f"   - {col.column_name} ({col.data_type})")
        
        # Step 3: Simulate table creation (this is what the endpoint does)
        service = MetadataService()
        
        # Generate expected table name
        table_name = service._generate_table_name(document.filename, document_id)
        logger.info(f"\n📊 Expected table name: {table_name}")
        
        # Step 4: Check if table exists and has data
        DatabaseConnection.init_db()
        engine = DatabaseConnection._engine
        
        with engine.begin() as conn:
            # Check if table exists
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                logger.info(f"✅ Table '{table_name}' exists in database")
                
                # Count rows
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
                logger.info(f"✅ Table has {row_count} rows")
                
                # Show sample data
                result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                sample_rows = result.fetchall()
                logger.info(f"📄 Sample rows (first 3):")
                for i, row in enumerate(sample_rows, 1):
                    logger.info(f"   Row {i}: {dict(row._mapping)}")
                
                return True
            else:
                logger.warning(f"⚠️ Table '{table_name}' does NOT exist yet")
                logger.warning(f"   Call POST /api/v1/metadata/process/{document_id} to create it")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error testing process flow: {e}", exc_info=True)
        return False


async def list_all_dynamic_tables():
    """List all dynamically created tables in the database"""
    try:
        DatabaseConnection.init_db()
        engine = DatabaseConnection._engine
        
        with engine.begin() as conn:
            # Get all tables except system tables
            result = conn.execute(text("""
                SELECT table_name, 
                       pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                  AND table_name NOT IN ('csv_documents', 'document_metadata', 'knowledge_base', 'users')
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            
            if tables:
                logger.info(f"\n📊 Found {len(tables)} dynamically created tables:")
                for table in tables:
                    table_name = table[0]
                    size = table[1]
                    
                    # Get row count
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    row_count = count_result.scalar()
                    
                    logger.info(f"   - {table_name}: {row_count} rows, {size}")
            else:
                logger.info("\n📊 No dynamically created tables found yet")
                
    except Exception as e:
        logger.error(f"❌ Error listing dynamic tables: {e}", exc_info=True)


async def main():
    """Main test runner"""
    
    # First, list all dynamic tables
    await list_all_dynamic_tables()
    
    # Then test specific document if you have one
    # Replace with actual document ID
    test_document_id = 1  # Change this to your document ID
    
    logger.info(f"\n\n{'='*60}")
    logger.info("To test the process endpoint:")
    logger.info(f"{'='*60}")
    logger.info(f"1. Make sure document {test_document_id} exists and has metadata")
    logger.info(f"2. curl -X POST http://localhost:8001/api/v1/metadata/process/{test_document_id}")
    logger.info(f"3. Run this script again to verify table was created")
    logger.info(f"{'='*60}\n")
    
    # Uncomment to test specific document:
    # await test_process_endpoint_flow(test_document_id)


if __name__ == "__main__":
    asyncio.run(main())
