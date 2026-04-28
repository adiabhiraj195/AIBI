from typing import List, Optional, Dict, Any
from app.database.connection import DatabaseConnection
from app.models.column_metadata import (
    KnowledgeBaseEntry, 
    ColumnMetadata,
    DocumentMetadataResponse
)
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def _parse_json_field(value):
    """Return a Python object for a JSON/JSONB field regardless of driver decoding.

    - If value is a string, parse via json.loads.
    - If value is already a dict/list (driver decoded), return as-is.
    - If bytes, decode and then parse.
    - If None or other types, return as-is.
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

class KnowledgeBaseRepository:
    
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
            now = datetime.utcnow()
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO knowledge_base (
                            document_id,
                            filename,
                            summary,
                            data_category,
                            insights,
                            use_cases,
                            column_analysis,
                            data_quality_score,
                            recommendations,
                            column_metadata,
                            created_at,
                            updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """,
                        (
                            document_id,
                            filename,
                            summary,
                            data_category,
                            json.dumps(insights),
                            json.dumps(use_cases),
                            json.dumps(column_analysis),
                            data_quality_score,
                            json.dumps(recommendations),
                            json.dumps([col.dict() for col in column_metadata]),
                            now,
                            now,
                        ),
                    )
                    row = cur.fetchone()
                    if row:
                        return row["id"]
                    raise ValueError("Failed to create knowledge base entry")
            
        except Exception as e:
            logger.error(f"Error creating knowledge base entry: {e}")
            raise
    
    @staticmethod
    async def get_knowledge_base_entry_by_document_id(document_id: int) -> Optional[KnowledgeBaseEntry]:
        """Get knowledge base entry by document ID"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM knowledge_base WHERE document_id = %s LIMIT 1;",
                        (document_id,),
                    )
                    entry = cur.fetchone()
                    if entry:
                        return KnowledgeBaseEntry(
                            id=entry["id"],
                            document_id=entry["document_id"],
                            filename=entry["filename"],
                            summary=entry["summary"],
                            data_category=entry["data_category"],
                            insights=_parse_json_field(entry["insights"]),
                            use_cases=_parse_json_field(entry["use_cases"]),
                            column_analysis=_parse_json_field(entry["column_analysis"]),
                            data_quality_score=entry["data_quality_score"],
                            recommendations=_parse_json_field(entry["recommendations"]),
                            created_at=str(entry["created_at"]),
                            updated_at=str(entry["updated_at"])
                        )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching knowledge base entry for document {document_id}: {e}")
            raise
    
    @staticmethod
    async def get_knowledge_base_entry_by_id(entry_id: int) -> Optional[KnowledgeBaseEntry]:
        """Get knowledge base entry by ID"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM knowledge_base WHERE id = %s LIMIT 1;",
                        (entry_id,),
                    )
                    entry = cur.fetchone()
                    if entry:
                        return KnowledgeBaseEntry(
                            id=entry["id"],
                            document_id=entry["document_id"],
                            filename=entry["filename"],
                            summary=entry["summary"],
                            data_category=entry["data_category"],
                            insights=_parse_json_field(entry["insights"]),
                            use_cases=_parse_json_field(entry["use_cases"]),
                            column_analysis=_parse_json_field(entry["column_analysis"]),
                            data_quality_score=entry["data_quality_score"],
                            recommendations=_parse_json_field(entry["recommendations"]),
                            created_at=str(entry["created_at"]),
                            updated_at=str(entry["updated_at"])
                        )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching knowledge base entry {entry_id}: {e}")
            raise
    
    @staticmethod
    async def list_knowledge_base_entries(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List knowledge base entries with summary info for frontend"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, document_id, filename, summary, data_category, data_quality_score, created_at
                        FROM knowledge_base
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s;
                        """,
                        (limit, offset),
                    )
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error listing knowledge base entries: {e}")
            raise
    
    @staticmethod
    async def search_knowledge_base(query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search knowledge base entries by filename, summary, or category"""
        try:
            search_pattern = f"%{query}%"
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, document_id, filename, summary, data_category, data_quality_score, created_at
                        FROM knowledge_base
                        WHERE filename ILIKE %s OR summary ILIKE %s OR data_category ILIKE %s
                        ORDER BY created_at DESC
                        LIMIT %s;
                        """,
                        (search_pattern, search_pattern, search_pattern, limit),
                    )
                    rows = cur.fetchall()
                    return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            raise
    
    @staticmethod
    async def delete_knowledge_base_entry(entry_id: int) -> bool:
        """Delete a knowledge base entry"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM knowledge_base WHERE id = %s RETURNING id;",
                        (entry_id,),
                    )
                    return cur.fetchone() is not None
            
        except Exception as e:
            logger.error(f"Error deleting knowledge base entry {entry_id}: {e}")
            raise

class DocumentMetadataRepository:
    
    @staticmethod
    async def save_document_metadata(document_id: int, columns: List[ColumnMetadata]) -> Optional[DocumentMetadataResponse]:
        """Save document metadata (column information)"""
        try:
            now = datetime.utcnow()
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get document filename
                    cur.execute(
                        "SELECT filename FROM csv_documents WHERE id = %s LIMIT 1;",
                        (document_id,),
                    )
                    doc = cur.fetchone()
                    if not doc:
                        raise ValueError(f"Document with ID {document_id} not found")
                    filename = doc["filename"]
                    
                    # Check if metadata already exists
                    cur.execute(
                        "SELECT created_at FROM document_metadata WHERE document_id = %s LIMIT 1;",
                        (document_id,),
                    )
                    existing = cur.fetchone()
                    created_at = existing["created_at"] if existing else now
                    
                    if existing:
                        # Update existing
                        cur.execute(
                            """
                            UPDATE document_metadata
                            SET filename = %s, column_metadata = %s, updated_at = %s
                            WHERE document_id = %s
                            RETURNING document_id;
                            """,
                            (filename, json.dumps([col.dict() for col in columns]), now, document_id),
                        )
                    else:
                        # Create new
                        cur.execute(
                            """
                            INSERT INTO document_metadata (document_id, filename, column_metadata, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING document_id;
                            """,
                            (document_id, filename, json.dumps([col.dict() for col in columns]), now, now),
                        )
                    
                    if cur.fetchone():
                        return DocumentMetadataResponse(
                            document_id=document_id,
                            filename=filename,
                            columns=columns,
                            created_at=str(created_at),
                            updated_at=str(now)
                        )
            return None
            
        except Exception as e:
            logger.error(f"Error saving document metadata: {e}")
            raise
    
    @staticmethod
    async def get_document_metadata(document_id: int) -> Optional[DocumentMetadataResponse]:
        """Get document metadata by document ID"""
        try:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM document_metadata WHERE document_id = %s LIMIT 1;",
                        (document_id,),
                    )
                    entry = cur.fetchone()
                    if entry:
                        return DocumentMetadataResponse(
                            document_id=entry["document_id"],
                            filename=entry["filename"],
                            columns=[ColumnMetadata(**col) for col in _parse_json_field(entry["column_metadata"])],
                            created_at=str(entry["created_at"]),
                            updated_at=str(entry["updated_at"])
                        )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching document metadata for document {document_id}: {e}")
            raise