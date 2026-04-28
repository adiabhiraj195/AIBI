"""
Database schema migration for data sync functionality
Run this script to prepare your PostgreSQL database for automatic data synchronization
"""

import asyncio
import sys
import logging
from datetime import datetime
from database.connection import db_manager
from config import settings
from logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger("migration")


async def run_migration():
    """Execute database schema migration"""
    logger.info("=" * 80)
    logger.info("🔧 Starting Database Schema Migration for Data Sync")
    logger.info("=" * 80)

    try:
        # Initialize database connection
        await db_manager.initialize()

        async with db_manager.get_connection() as conn:
            # 1. Create data_sync_state table
            logger.info("\n📋 Creating data_sync_state table...")
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS data_sync_state (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(50) NOT NULL UNIQUE,
                    last_sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_synced_document_id BIGINT DEFAULT 0,
                    total_documents_synced BIGINT DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'healthy',
                    error_message TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
            )
            logger.info("✅ data_sync_state table created")

            # 2. Create index on data_sync_state
            logger.info("📋 Creating index on data_sync_state...")
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sync_state_service 
                ON data_sync_state(service_name);
                """
            )
            logger.info("✅ Index created")

            # 3. Add columns to csv_documents table
            logger.info("\n📋 Adding RAG processing columns to csv_documents...")
            
            try:
                await conn.execute(
                    """
                    ALTER TABLE csv_documents
                    ADD COLUMN IF NOT EXISTS is_processed_by_rag BOOLEAN DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS rag_processed_at TIMESTAMP WITH TIME ZONE,
                    ADD COLUMN IF NOT EXISTS embedding_version INT DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS data_hash VARCHAR(64);
                    """
                )
                logger.info("✅ Columns added to csv_documents")
            except Exception as e:
                logger.warning(f"⚠️  Some columns may already exist: {e}")

            # 4. Create indexes on csv_documents
            logger.info("📋 Creating indexes on csv_documents...")
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_csv_documents_processed 
                ON csv_documents(is_processed_by_rag, created_at DESC);
                """
            )
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_csv_documents_hash 
                ON csv_documents(data_hash);
                """
            )
            logger.info("✅ Indexes created")

            # 5. Initialize sync state
            logger.info("\n📋 Initializing sync state for Main Brain service...")
            await conn.execute(
                """
                INSERT INTO data_sync_state (service_name, status) 
                VALUES ($1, 'healthy')
                ON CONFLICT (service_name) DO NOTHING
                """,
                "suzlon-copilot-main-brain"
            )
            logger.info("✅ Sync state initialized")

            # 6. Create sync_history table (optional audit table)
            logger.info("\n📋 Creating sync_history table...")
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sync_history (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(50) NOT NULL,
                    documents_processed INT DEFAULT 0,
                    documents_failed INT DEFAULT 0,
                    sync_start_time TIMESTAMP WITH TIME ZONE,
                    sync_end_time TIMESTAMP WITH TIME ZONE,
                    duration_seconds INT,
                    status VARCHAR(20),
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
            )
            logger.info("✅ sync_history table created")

            # Create indexes on sync_history
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sync_history_service 
                ON sync_history(service_name);
                """
            )
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sync_history_created 
                ON sync_history(created_at DESC);
                """
            )
            logger.info("✅ Indexes created on sync_history")

        # Verify migration
        logger.info("\n📊 Verifying migration...")
        async with db_manager.get_connection() as conn:
            table_count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('data_sync_state', 'sync_history', 'csv_documents')
                """
            )
            
            logger.info(f"✅ Verified {table_count} core tables exist")

        logger.info("\n" + "=" * 80)
        logger.info("✅ Migration completed successfully!")
        logger.info("=" * 80)

        logger.info("\n📋 Migration Summary:")
        logger.info("   • data_sync_state table: Tracks sync status between services")
        logger.info("   • csv_documents: Added RAG processing metadata columns")
        logger.info("   • Indexes: Created for efficient sync queries")
        logger.info("   • sync_history table: For future audit trail")

        logger.info("\n🚀 Next Steps:")
        logger.info("   1. Restart Suzlon_Copilot_Main_Brain service")
        logger.info("   2. Monitor sync status via: GET /api/v1/admin/sync/status")
        logger.info("   3. Trigger manual sync via: POST /api/v1/admin/sync/trigger")

        return True

    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}", exc_info=True)
        return False

    finally:
        await db_manager.cleanup()


if __name__ == "__main__":
    logger.info(f"Database: {settings.database.host}:{settings.database.port}/{settings.database.name}")
    
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)
