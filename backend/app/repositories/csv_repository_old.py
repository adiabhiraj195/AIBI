from typing import List, Optional
import json
import logging
from datetime import datetime

from app.database.connection import DatabaseConnection
from psycopg2.extras import Json
from app.models.csv_document import (
    CSVDocumentCreate,
    CSVDocumentResponse,
    CSVDocumentDetail,
    CSVDocumentList,
)

logger = logging.getLogger(__name__)

class CSVRepository:
    @staticmethod
    def _parse_json_field(value):
        """Return a Python object for a JSON/JSONB field regardless of driver decoding.

        - If value is a string, parse via json.loads.
        - If value is already a dict/list (driver decoded), return as-is.
        - If None, return None.
        """
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, (bytes, bytearray)):
            try:
                value = value.decode("utf-8")
            except Exception:
                pass
        if isinstance(value, str):
            return json.loads(value)
        return value
    
    @staticmethod
    async def create_document(document_data: CSVDocumentCreate) -> Optional[CSVDocumentResponse]:
        """Create a new CSV document in the database"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO csv_documents (
                            filename,
                            preview_data,
                            full_data,
                            is_described,
                            row_count,
                            column_count,
                            upload_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, filename, preview_data, is_described, row_count, column_count, upload_date;
                        """,
                        (
                            document_data.filename,
                            Json(document_data.preview_data),
                            Json(document_data.full_data),
                            document_data.is_described,
                            document_data.row_count,
                            document_data.column_count,
                            datetime.utcnow(),
                        ),
                    )
                    doc = cur.fetchone()
                    if doc:
                        return CSVDocumentResponse(
                            id=doc["id"],
                            filename=doc["filename"],
                            preview=CSVRepository._parse_json_field(doc["preview_data"]),
                            is_described=doc["is_described"],
                            row_count=doc["row_count"],
                            column_count=doc["column_count"],
                            upload_date=str(doc["upload_date"]),
                        )
            return None

        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise

    @staticmethod
    async def document_exists_by_filename(filename: str) -> bool:
        """Check if a CSV document exists for the given filename"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 1
                        FROM csv_documents
                        WHERE filename = %s
                        LIMIT 1;
                        """,
                        (filename,),
                    )
                    return cur.fetchone() is not None

        except Exception as e:
            logger.error(f"Error checking document existence for filename '{filename}': {e}")
            raise
    
    @staticmethod
    async def get_document_by_id(document_id: int) -> Optional[CSVDocumentDetail]:
        """Get a CSV document by ID with full data"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, filename, preview_data, full_data, is_described,
                               row_count, column_count, upload_date
                        FROM csv_documents
                        WHERE id = %s
                        LIMIT 1;
                        """,
                        (document_id,),
                    )
                    doc = cur.fetchone()
                    if doc:
                        return CSVDocumentDetail(
                            id=doc["id"],
                            filename=doc["filename"],
                            preview=CSVRepository._parse_json_field(doc["preview_data"]),
                            full_data=CSVRepository._parse_json_field(doc["full_data"]),
                            is_described=doc["is_described"],
                            row_count=doc["row_count"],
                            column_count=doc["column_count"],
                            upload_date=str(doc["upload_date"]),
                        )
            return None

        except Exception as e:
            logger.error(f"Error fetching document {document_id}: {e}")
            raise
    
    @staticmethod
    async def get_document_preview_by_id(document_id: int) -> Optional[CSVDocumentResponse]:
        """Get a CSV document by ID with preview data only"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, filename, preview_data, is_described, row_count, column_count, upload_date
                        FROM csv_documents
                        WHERE id = %s
                        LIMIT 1;
                        """,
                        (document_id,),
                    )
                    doc = cur.fetchone()
                    if doc:
                        return CSVDocumentResponse(
                            id=doc["id"],
                            filename=doc["filename"],
                            preview=CSVRepository._parse_json_field(doc["preview_data"]),
                            is_described=doc["is_described"],
                            row_count=doc["row_count"],
                            column_count=doc["column_count"],
                            upload_date=str(doc["upload_date"]),
                        )
            return None

        except Exception as e:
            logger.error(f"Error fetching document preview {document_id}: {e}")
            raise
    
    @staticmethod
    async def list_documents(limit: int = 100, offset: int = 0) -> List[CSVDocumentList]:
        """List all CSV documents with pagination"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, filename, upload_date, is_described, row_count, column_count
                        FROM csv_documents
                        ORDER BY upload_date DESC
                        LIMIT %s OFFSET %s;
                        """,
                        (limit, offset),
                    )
                    rows = cur.fetchall()
                    return [
                        CSVDocumentList(
                            id=doc["id"],
                            filename=doc["filename"],
                            upload_date=str(doc["upload_date"]),
                            is_described=doc["is_described"],
                            row_count=doc["row_count"],
                            column_count=doc["column_count"],
                        )
                        for doc in rows
                    ]

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
    
    @staticmethod
    async def update_document_description_status(document_id: int, is_described: bool) -> bool:
        """Update the description status of a document"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE csv_documents
                        SET is_described = %s, upload_date = upload_date
                        WHERE id = %s
                        RETURNING id;
                        """,
                        (is_described, document_id),
                    )
                    return cur.fetchone() is not None

        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            raise
    
    @staticmethod
    async def delete_document(document_id: int) -> bool:
        """Delete a CSV document"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM csv_documents WHERE id = %s RETURNING id;",
                        (document_id,),
                    )
                    return cur.fetchone() is not None

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise