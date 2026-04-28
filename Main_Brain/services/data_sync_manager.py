"""
Sustainable Data Sync Manager
Monitors new CSV uploads from backend and keeps RAG embeddings in sync
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib
import asyncio
import json
from database.connection import db_manager
from logging_config import get_logger

logger = get_logger("data_sync_manager")


class DataSyncManager:
    """Manages synchronization of new data with RAG embeddings"""

    def __init__(self):
        self.sync_interval = 300  # Check every 5 minutes
        self.batch_size = 50  # Process 50 documents at a time
        self._sync_task: Optional[asyncio.Task] = None
        self.service_name = "suzlon-copilot-main-brain"
        self._is_syncing = False

    async def initialize(self) -> None:
        """Initialize sync manager and start background task"""
        logger.info("🔄 Initializing Data Sync Manager...")

        try:
            # Ensure sync state table exists
            await self._ensure_sync_table_exists()

            # Update sync state to healthy
            await self._update_sync_state("healthy")

            # Start background sync task
            self._sync_task = asyncio.create_task(self._sync_loop())
            logger.info("✅ Data Sync Manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Data Sync Manager: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup sync tasks"""
        logger.info("🔄 Cleaning up Data Sync Manager...")
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ Data Sync Manager cleaned up")

    async def _sync_loop(self) -> None:
        """Background task that continuously syncs new data"""
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                await self.sync_new_documents()
            except asyncio.CancelledError:
                logger.info("Sync loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Sync loop error: {e}")
                await self._update_sync_state("error", str(e))
                # Wait before retrying
                await asyncio.sleep(self.sync_interval * 2)

    async def sync_new_documents(self) -> Dict[str, Any]:
        """
        Fetch new documents from backend and generate embeddings
        Returns sync statistics
        """
        if self._is_syncing:
            logger.debug("⏳ Sync already in progress, skipping...")
            return {
                "status": "already_syncing",
                "timestamp": datetime.utcnow().isoformat()
            }

        self._is_syncing = True
        try:
            # Get last sync time
            last_sync_time = await self._get_last_sync_time()

            logger.info(f"🔍 Checking for new documents since {last_sync_time}...")

            # Fetch unprocessed documents
            new_docs = await self._fetch_unprocessed_documents(last_sync_time)

            if not new_docs:
                logger.debug("✅ No new documents to sync")
                await self._update_sync_state("healthy")
                return {
                    "status": "no_changes",
                    "documents_processed": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }

            logger.info(f"📥 Found {len(new_docs)} new documents to process")

            # Process each document
            processed_count = 0
            failed_count = 0

            for doc in new_docs:
                try:
                    await self._process_document(doc)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to process document {doc['id']}: {e}")
                    failed_count += 1
                    continue

            # Update sync state
            await self._update_sync_state("healthy")

            result = {
                "status": "success",
                "documents_processed": processed_count,
                "documents_failed": failed_count,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"✅ Sync complete: {processed_count} processed, {failed_count} failed")
            return result

        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")
            await self._update_sync_state("error", str(e))
            raise
        finally:
            self._is_syncing = False

    async def _fetch_unprocessed_documents(self, last_sync_time: datetime) -> List[Dict]:
        """Fetch documents that haven't been processed by RAG yet"""
        try:
            async with db_manager.get_connection() as conn:
                docs = await conn.fetch(
                    """
                    SELECT 
                        id, filename, full_data, upload_date, 
                        row_count, column_count
                    FROM csv_documents
                    WHERE upload_date > $1 
                    AND (is_processed_by_rag = FALSE OR data_hash IS NULL)
                    ORDER BY upload_date ASC
                    LIMIT $2
                    """,
                    last_sync_time,
                    self.batch_size
                )
                return [dict(doc) for doc in docs] if docs else []
        except Exception as e:
            logger.error(f"Error fetching unprocessed documents: {e}")
            return []

    async def _process_document(self, doc: Dict[str, Any]) -> None:
        """Process a single document and generate embeddings"""
        doc_id = doc['id']
        filename = doc['filename']

        logger.info(f"⚙️ Processing document: {filename} (ID: {doc_id})")

        try:
            # Generate data hash for change detection
            data_hash = await self._generate_data_hash(doc['full_data'])

            # Extract text content for embedding
            content = await self._extract_content(doc['full_data'])

            if not content.strip():
                logger.warning(f"⚠️ Document {doc_id} has empty content")
                # Still mark as processed even if empty
                await self._mark_document_processed(doc_id, data_hash)
                return

            # Store embeddings metadata in database
            # The actual embedding generation will happen lazily when needed by RAG
            async with db_manager.get_connection() as conn:
                # Mark document as processed
                await conn.execute(
                    """
                    UPDATE csv_documents
                    SET is_processed_by_rag = TRUE,
                        rag_processed_at = NOW(),
                        data_hash = $1,
                        embedding_version = 1
                    WHERE id = $2
                    """,
                    data_hash,
                    doc_id
                )

            logger.info(f"✅ Document {doc_id} marked for RAG processing")

        except Exception as e:
            logger.error(f"❌ Error processing document {doc_id}: {e}")
            raise

    async def _extract_content(self, full_data: List[Dict]) -> str:
        """Extract text content from CSV data for embedding"""
        if not full_data:
            return ""

        try:
            # Convert all rows to readable text
            lines = []
            max_rows = 100  # Limit to first 100 rows for efficiency
            
            for i, row in enumerate(full_data[:max_rows]):
                if isinstance(row, dict):
                    row_text = " | ".join(
                        f"{k}: {v}" for k, v in row.items() if v
                    )
                    lines.append(row_text)
                else:
                    lines.append(str(row))

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return ""

    async def _generate_data_hash(self, data: Any) -> str:
        """Generate hash of document data for change detection"""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating data hash: {e}")
            return "unknown"

    async def _mark_document_processed(self, doc_id: int, data_hash: str) -> None:
        """Mark document as processed"""
        try:
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    UPDATE csv_documents
                    SET is_processed_by_rag = TRUE,
                        rag_processed_at = NOW(),
                        data_hash = $1
                    WHERE id = $2
                    """,
                    data_hash,
                    doc_id
                )
        except Exception as e:
            logger.error(f"Error marking document as processed: {e}")
            raise

    async def _get_last_sync_time(self) -> datetime:
        """Get last successful sync timestamp"""
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchval(
                    """
                    SELECT last_sync_timestamp
                    FROM data_sync_state
                    WHERE service_name = $1
                    """,
                    self.service_name
                )

            if result:
                return result
        except Exception as e:
            logger.warning(f"Could not fetch last sync time: {e}")

        # Default to 24 hours ago
        return datetime.utcnow() - timedelta(days=1)

    async def _update_sync_state(self, status: str, error_msg: str = None) -> None:
        """Update sync state in database"""
        try:
            async with db_manager.get_connection() as conn:
                await conn.execute(
                    """
                    UPDATE data_sync_state
                    SET status = $1,
                        last_sync_timestamp = NOW(),
                        error_message = $2,
                        updated_at = NOW()
                    WHERE service_name = $3
                    """,
                    status,
                    error_msg,
                    self.service_name
                )
        except Exception as e:
            logger.error(f"Failed to update sync state: {e}")

    async def _ensure_sync_table_exists(self) -> None:
        """Create sync state table if it doesn't exist"""
        try:
            async with db_manager.get_connection() as conn:
                # Create the table
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

                # Create index
                await conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_sync_state_service 
                    ON data_sync_state(service_name);
                    """
                )

                # Ensure this service exists in the table
                await conn.execute(
                    """
                    INSERT INTO data_sync_state (service_name, status) 
                    VALUES ($1, 'healthy')
                    ON CONFLICT (service_name) DO NOTHING
                    """,
                    self.service_name
                )

                logger.info("✅ Sync state table is ready")
        except Exception as e:
            logger.error(f"Error ensuring sync table exists: {e}")
            raise


# Global instance
data_sync_manager = DataSyncManager()
