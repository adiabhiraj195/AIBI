import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
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
from app.repositories.csv_repository import CSVRepository
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository, DocumentMetadataRepository
from app.services.llm_service import LLMService
from app.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class MetadataService:
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def extract_document_info_for_frontend(self, document_id: int) -> ColumnExtractionResponse:
        """Extract document info optimized for frontend form display"""
        try:
            # Get document with preview data
            document = await CSVRepository.get_document_preview_by_id(document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            if not document.preview:
                raise HTTPException(status_code=400, detail="No preview data available")
            
            # Extract basic column information
            columns = []
            first_row = document.preview[0] if document.preview else {}
            
            for column_name, sample_value in first_row.items():
                data_type = self._infer_data_type(sample_value, document.preview, column_name)
                columns.append({
                    "column_name": column_name,
                    "data_type": data_type
                })
            
            return ColumnExtractionResponse(
                document_id=document_id,
                filename=document.filename,
                columns=columns,
                total_columns=len(columns),
                sample_data=document.preview[:3]  # First 3 rows for reference
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extracting document info for frontend: {e}")
            raise HTTPException(status_code=500, detail="Failed to extract document information")
    
    def _infer_data_type(self, sample_value: Any, preview_data: List[Dict[str, Any]], column_name: str) -> str:
        """Infer data type from sample values"""
        try:
            # Collect all non-null values for this column
            values = [row.get(column_name) for row in preview_data if row.get(column_name) is not None]
            
            if not values:
                return "string"
            
            # Check if all values are numeric
            numeric_count = 0
            integer_count = 0
            float_count = 0
            
            for value in values:
                try:
                    if isinstance(value, (int, float)):
                        numeric_count += 1
                        if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
                            integer_count += 1
                        else:
                            float_count += 1
                    elif isinstance(value, str):
                        # Try to parse as number
                        if '.' in value:
                            float(value)
                            numeric_count += 1
                            float_count += 1
                        else:
                            int(value)
                            numeric_count += 1
                            integer_count += 1
                except (ValueError, TypeError):
                    pass
            
            # Determine data type based on analysis
            if numeric_count == len(values):
                if float_count > 0:
                    return "float"
                else:
                    return "integer"
            
            # Check for boolean-like values
            boolean_values = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n'}
            if all(str(v).lower() in boolean_values for v in values):
                return "boolean"
            
            # Check for date-like patterns
            if self._looks_like_date(values):
                return "date"
            
            return "string"
            
        except Exception:
            return "string"
    
    def _looks_like_date(self, values: List[Any]) -> bool:
        """Check if values look like dates"""
        try:
            date_indicators = ['-', '/', ':', 'T', 'Z']
            for value in values[:3]:  # Check first 3 values
                str_value = str(value)
                if any(indicator in str_value for indicator in date_indicators) and len(str_value) > 8:
                    return True
            return False
        except:
            return False
    
    async def save_document_metadata(self, request: DocumentMetadataRequest) -> DocumentMetadataResponse:
        """Save complete document metadata with all user inputs"""
        try:
            # Validate document exists
            document = await CSVRepository.get_document_preview_by_id(request.document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Validate that all required fields are provided
            for col in request.columns:
                if not col.description or col.description.strip() == "":
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Description is required for column '{col.column_name}'"
                    )
            
            # Save metadata
            result = await DocumentMetadataRepository.save_document_metadata(
                request.document_id, 
                request.columns
            )
            
            if not result:
                raise HTTPException(status_code=500, detail="Failed to save document metadata")
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving document metadata: {e}")
            raise HTTPException(status_code=500, detail="Failed to save document metadata")
    
    async def get_document_metadata(self, document_id: int) -> Optional[DocumentMetadataResponse]:
        """Get saved document metadata"""
        try:
            return await DocumentMetadataRepository.get_document_metadata(document_id)
        except Exception as e:
            logger.error(f"Error fetching document metadata: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch document metadata")
    
    async def process_document_with_ai(self, document_id: int) -> ProcessDocumentResponse:
        """Process document with AI using saved metadata"""
        try:
            # Get saved metadata
            metadata = await self.get_document_metadata(document_id)
            if not metadata:
                raise HTTPException(
                    status_code=404, 
                    detail="Document metadata not found. Please save metadata first."
                )
            
            # Get full document (with all data, not just preview)
            document = await CSVRepository.get_document_by_id(document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Create process request
            process_request = ProcessDocumentRequest(
                document_id=document_id,
                columns=metadata.columns
            )
            
            # Process with LLM and store directly
            knowledge_base_id = await self.llm_service.process_and_store_knowledge(
                process_request, 
                document.filename, 
                document.preview
            )
            
            # Generate schema and create dynamic table for CSV data
            table_created = False
            table_name = None
            try:
                table_name, rows_inserted = await self._generate_and_create_table(
                    document_id, 
                    document.filename, 
                    metadata.columns, 
                    document.full_data or []
                )
                if table_name:
                    logger.info(f"✅ Dynamic table created and populated for document {document_id}")
                    table_created = True
                    
                    # Update file registry with dynamic table information
                    try:
                        from app.repositories.file_registry_repository import FileRegistryRepository
                        kb_entry = await KnowledgeBaseRepository.get_knowledge_base_entry_by_document_id(document_id)
                        data_category = kb_entry.data_category if kb_entry else None
                        
                        await FileRegistryRepository.update_dynamic_table(
                            document_id=document_id,
                            dynamic_table_name=table_name,
                            data_category=data_category
                        )
                    except Exception as e:
                        logger.error(f"⚠️ Failed to update file registry: {e}")
                else:
                    logger.error(f"❌ Dynamic table creation returned False for document {document_id}")
            except Exception as e:
                logger.error(f"❌ Failed to create dynamic table for document {document_id}: {e}", exc_info=True)
                # Don't fail the entire process if table creation fails, but log it prominently
            
            # Update document description status
            await CSVRepository.update_document_description_status(document_id, True)
            
            # Update file registry to mark as described
            try:
                from app.repositories.file_registry_repository import FileRegistryRepository
                await FileRegistryRepository.mark_as_described(document_id, True)
            except Exception as e:
                logger.error(f"⚠️ Failed to mark file as described in registry: {e}")
            
            # Get the created entry for summary
            kb_entry = await KnowledgeBaseRepository.get_knowledge_base_entry_by_document_id(document_id)
            summary = kb_entry.summary if kb_entry else "Knowledge base entry created successfully"
            
            return ProcessDocumentResponse(
                success=True,
                knowledge_base_id=knowledge_base_id,
                message="Document processed successfully with AI and data table created",
                summary=summary
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing document {document_id} with AI: {e}")
            raise HTTPException(status_code=500, detail="Failed to process document with AI")
    
    async def get_knowledge_base_entry(self, document_id: int) -> Optional[KnowledgeBaseEntry]:
        """Get knowledge base entry for a document"""
        try:
            return await KnowledgeBaseRepository.get_knowledge_base_entry_by_document_id(document_id)
        except Exception as e:
            logger.error(f"Error fetching knowledge base entry: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch knowledge base entry")
    
    async def list_knowledge_base_summaries(self, limit: int = 20, offset: int = 0) -> List[KnowledgeBaseSummary]:
        """List knowledge base entries with summary info for frontend"""
        try:
            entries_data = await KnowledgeBaseRepository.list_knowledge_base_entries(limit, offset)
            
            summaries = []
            for entry in entries_data:
                summaries.append(KnowledgeBaseSummary(
                    id=entry["id"],
                    document_id=entry["document_id"],
                    filename=entry["filename"],
                    summary=entry["summary"],
                    data_category=entry["data_category"],
                    data_quality_score=entry["data_quality_score"],
                    created_at=entry["created_at"]
                ))
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error listing knowledge base summaries: {e}")
            raise HTTPException(status_code=500, detail="Failed to list knowledge base entries")
    
    async def search_knowledge_base(self, query: str, limit: int = 20) -> List[KnowledgeBaseSummary]:
        """Search knowledge base entries for frontend"""
        try:
            entries_data = await KnowledgeBaseRepository.search_knowledge_base(query, limit)
            
            summaries = []
            for entry in entries_data:
                summaries.append(KnowledgeBaseSummary(
                    id=entry["id"],
                    document_id=entry["document_id"],
                    filename=entry["filename"],
                    summary=entry["summary"],
                    data_category=entry["data_category"],
                    data_quality_score=entry["data_quality_score"],
                    created_at=entry["created_at"]
                ))
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            raise HTTPException(status_code=500, detail="Failed to search knowledge base")
    
    async def delete_knowledge_base_entry(self, entry_id: int) -> bool:
        """Delete knowledge base entry"""
        try:
            return await KnowledgeBaseRepository.delete_knowledge_base_entry(entry_id)
        except Exception as e:
            logger.error(f"Error deleting knowledge base entry: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete knowledge base entry")
    
    async def _generate_and_create_table(self, document_id: int, filename: str, columns: List[ColumnMetadata], full_data: List[Dict[str, Any]]) -> tuple:
        """Generate schema and create a dynamic table for the CSV data using SQLAlchemy
        Returns: (table_name, rows_inserted) or (None, 0) if creation failed"""
        try:
            from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, MetaData, Table, text
            from datetime import datetime
            
            # Fetch full document data from csv_documents table to ensure we have all data
            logger.info(f"Fetching full CSV data for document {document_id}...")
            document = await CSVRepository.get_document_by_id(document_id)
            if not document or not document.full_data:
                logger.warning(f"No full data found for document {document_id}")
                return None, 0
            
            # Use the fetched full_data (ensure it's parsed as list of dicts)
            csv_full_data = document.full_data
            if isinstance(csv_full_data, str):
                import json
                csv_full_data = json.loads(csv_full_data)
            
            if not isinstance(csv_full_data, list):
                logger.error(f"Full data for document {document_id} is not a list. Type: {type(csv_full_data)}")
                return None, 0
            
            logger.info(f"✅ Fetched {len(csv_full_data)} rows from CSV document {document_id}")
            
            # Log sample of data for debugging
            if csv_full_data:
                logger.info(f"Sample data keys: {list(csv_full_data[0].keys())}")
                logger.info(f"First row sample: {csv_full_data[0]}")
            
            # Log column metadata
            logger.info(f"Column metadata: {[f'{col.column_name} ({col.data_type})' for col in columns]}")
            
            # Generate table name from filename (remove extension and special chars)
            table_name = self._generate_table_name(filename, document_id)
            
            # Initialize database if not already done
            DatabaseConnection.init_db()
            
            # Get SQLAlchemy engine
            engine = DatabaseConnection._engine
            metadata = MetaData()
            
            # Define dynamic columns using SQLAlchemy
            table_columns = [
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('created_at', DateTime, default=datetime.utcnow)
            ]
            
            # Add columns from metadata
            for col in columns:
                col_name = col.column_name.replace(' ', '_').replace('-', '_').lower()
                sql_type = self._get_sqlalchemy_type(col.data_type)
                table_columns.append(Column(col_name, sql_type, nullable=True))
            
            # Create the dynamic table
            dynamic_table = Table(table_name, metadata, *table_columns)
            
            logger.info(f"Creating table '{table_name}' for document {document_id}...")
            
            # Drop existing table if it exists
            with engine.begin() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                logger.info(f"Dropped existing table '{table_name}' if it existed")
                
                # Create new table
                metadata.create_all(conn)
                logger.info(f"✅ Created new table '{table_name}'")
            
            # Insert full CSV data into the table using SQLAlchemy
            rows_inserted = 0
            print(csv_full_data, columns, table_name, "all details above")
            if csv_full_data:
                rows_inserted = await self._insert_data_into_table_sqlalchemy(table_name, columns, csv_full_data, engine)
                logger.info(f"✅ Inserted {rows_inserted} rows into table '{table_name}'")
                
                # Verify data was actually inserted
                with engine.begin() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    actual_count = result.scalar()
                    logger.info(f"✅ VERIFICATION: Table '{table_name}' now contains {actual_count} rows")
                    
                    if actual_count != rows_inserted:
                        logger.error(f"❌ MISMATCH: Expected {rows_inserted} rows but found {actual_count} rows!")
                    
                    # Show sample data from table
                    result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                    sample_rows = result.fetchall()
                    logger.info(f"Sample data from table: {sample_rows}")
            else:
                logger.warning(f"No data to insert into table '{table_name}'")
            
            logger.info(f"✅ Table '{table_name}' successfully created and populated")
            return table_name, rows_inserted
            
        except Exception as e:
            logger.error(f"Error creating dynamic table for document {document_id}: {e}", exc_info=True)
            return None, 0
    
    def _generate_table_name(self, filename: str, document_id: int) -> str:
        """Generate a valid PostgreSQL table name from filename"""
        import re
        # Remove extension
        name = filename.rsplit('.', 1)[0]
        # Replace invalid characters with underscore
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = f"tbl_{name}"
        # Truncate to 63 characters (PostgreSQL limit) and add document ID
        name = f"{name[:50]}_{document_id}"
        return name.lower()
    
    def _generate_create_table_sql(self, table_name: str, columns: List[ColumnMetadata]) -> str:
        """Generate CREATE TABLE statement from column metadata"""
        sql_columns = ["id SERIAL PRIMARY KEY", "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"]
        
        for col in columns:
            col_name = col.column_name.replace(' ', '_').replace('-', '_').lower()
            pg_type = self._map_data_type_to_postgres(col.data_type)
            sql_columns.append(f"{col_name} {pg_type}")
        
        columns_def = ",\n    ".join(sql_columns)
        return f"CREATE TABLE {table_name} (\n    {columns_def}\n);"
    
    def _map_data_type_to_postgres(self, data_type: str) -> str:
        """Map inferred data types to PostgreSQL types"""
        type_mapping = {
            "integer": "INTEGER",
            "float": "NUMERIC",
            "boolean": "BOOLEAN",
            "date": "DATE",
            "datetime": "TIMESTAMP",
            "string": "TEXT",
            "text": "TEXT"
        }
        return type_mapping.get(data_type.lower(), "TEXT")
    
    def _get_sqlalchemy_type(self, data_type: str):
        """Map inferred data types to SQLAlchemy type objects"""
        from sqlalchemy import Integer, Float, Boolean, Date, DateTime, String, Text
        
        type_mapping = {
            "integer": Integer,
            "float": Float,
            "boolean": Boolean,
            "date": Date,
            "datetime": DateTime,
            "string": String(255),
            "text": Text
        }
        return type_mapping.get(data_type.lower(), Text)
    
    def _clean_value(self, value: Any, target_type: str = None) -> Any:
        """Clean individual cell values"""
        try:
            if value is None:
                return None

            
            # Convert to string and strip
            cleaned = str(value).strip()
            
            # Handle empty strings
            if not cleaned:
                return None
            
            # Common NaN/Null patterns
            nan_patterns = {'nan', 'none', 'null', 'n/a', 'na', '#n/a', '#na', 'undefined'}
            if cleaned.lower() in nan_patterns:
                return None
            
            # Check for corrupted patterns like multiple special characters
            if cleaned in ['---', '???', '...', '###', 'N/A', 'NULL']:
                return None

            # Handle DATE type specific cleanup
            if target_type and target_type.upper() == 'DATE':
                import re
                # Match YYYY-MM pattern and convert to YYYY-MM-01
                if re.match(r'^\d{4}-\d{2}$', cleaned):
                    return f"{cleaned}-01"
            
            # Return cleaned string
            return cleaned
            
        except Exception as e:
            logger.warning(f"Error cleaning value '{value}': {e}. Returning None.")
            return None
    
    async def _insert_data_into_table_sqlalchemy(self, table_name: str, columns: List[ColumnMetadata], full_data: List[Dict[str, Any]], engine) -> int:
        """Insert CSV data into the dynamically created table using SQLAlchemy and return rows inserted count"""
        if not full_data:
            logger.warning(f"No data to insert into {table_name}")
            return 0
        
        try:
            import re
            from sqlalchemy import text, MetaData, Table, inspect
            
            def normalize_column_name(name: str) -> str:
                """Normalize column name the same way as table creation: spaces and dashes to underscore, then lowercase"""
                return name.replace(' ', '_').replace('-', '_').lower()
            
            logger.info(f"Starting data insertion for table '{table_name}'")
            logger.info(f"Total rows to insert: {len(full_data)}")
            
            # First, get the ACTUAL column names from the database table
            raw_conn = engine.raw_connection()
            cursor = raw_conn.cursor()
            
            try:
                cursor.execute(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name NOT IN ('id', 'created_at', 'upload_date')
                    ORDER BY ordinal_position
                """)
                actual_table_cols = [row[0] for row in cursor.fetchall()]
                logger.info(f"✅ Actual table columns from database: {actual_table_cols}")
            finally:
                cursor.close()
                raw_conn.close()
            
            # Get actual column keys from first row of data
            first_row = full_data[0]
            actual_data_keys = list(first_row.keys())
            logger.info(f"Actual data column keys: {actual_data_keys}")
            
            # Create mapping from actual table column names to data keys
            # The table columns are already normalized (from table creation)
            # The data keys are NOT normalized yet
            column_data_to_table = {}  # Maps table_col_name -> data_key
            
            for table_col in actual_table_cols:
                # For each table column (which is already normalized), find the matching data key
                # by normalizing the data key and comparing
                found_match = False
                
                logger.info(f"Looking for match for table column: '{table_col}'")
                
                for data_key in actual_data_keys:
                    # Normalize the data key the same way the table column was normalized
                    data_key_normalized = normalize_column_name(data_key)
                    
                    logger.info(f"  Checking data_key '{data_key}' -> normalized '{data_key_normalized}'")
                    
                    if data_key_normalized == table_col:
                        # Found match!
                        column_data_to_table[table_col] = data_key
                        logger.info(f"  ✅ MATCH! Mapping table col '{table_col}' -> data_key '{data_key}'")
                        found_match = True
                        break
                
                if not found_match:
                    logger.warning(f"⚠️ No matching data key for table column '{table_col}' - will insert as NULL")
            
            logger.info(f"Final column mapping: {column_data_to_table}")
            
            # Insert rows one-by-one, each with its own transaction
            inserted_count = 0
            failed_count = 0
            
            for idx, row in enumerate(full_data):
                raw_conn = None
                cursor = None
                try:
                    # Prepare this specific row with data cleaning
                    row_vals = {}
                    for table_col, data_key in column_data_to_table.items():
                        raw_value = row.get(data_key)
                        
                        # Find target column type to help cleaning
                        target_type = next((c.data_type for c in columns if normalize_column_name(c.column_name) == table_col), None)
                        
                        # Clean the value (replace NaN, empty, corrupted with None/NULL)
                        cleaned_value = self._clean_value(raw_value, target_type)
                        row_vals[table_col] = cleaned_value
                    
                    # Log first few rows for debugging
                    if idx < 3:
                        logger.info(f"Row {idx}: {row_vals}")
                    
                    # Open a new connection for each row
                    raw_conn = engine.raw_connection()
                    cursor = raw_conn.cursor()
                    
                    # Build the INSERT statement for this row
                    cols = []
                    vals = []
                    for table_col in actual_table_cols:
                        # Quote column names to handle special characters like colons
                        cols.append(f'"{table_col}"')
                        vals.append(row_vals.get(table_col))
                    
                    # Build SQL with %s placeholders for psycopg2
                    # Quote the table name as well to handle special characters and numbers
                    columns_str = ", ".join(cols)
                    placeholders = ", ".join(["%s"] * len(cols))
                    insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'
                    
                    if idx < 2:
                        logger.info(f"SQL: {insert_sql}")
                        logger.info(f"Values: {vals}")
                    
                    # Execute the INSERT
                    cursor.execute(insert_sql, vals)
                    
                    # Commit this row's transaction
                    raw_conn.commit()
                    cursor.close()
                    raw_conn.close()
                    
                    inserted_count += 1
                    
                    if idx % 10 == 0:
                        logger.info(f"Progress: Inserted {inserted_count} rows so far...")
                    
                except Exception as row_error:
                    failed_count += 1
                    logger.error(f"Error inserting row {idx}: {row_error}")
                    logger.error(f"Error type: {type(row_error).__name__}")
                    logger.error(f"Full error: {str(row_error)}")
                    if idx < 5:
                        logger.error(f"Row data: {row}")
                        logger.error(f"SQL attempted: {insert_sql if 'insert_sql' in locals() else 'N/A'}")
                        logger.error(f"Values attempted: {vals if 'vals' in locals() else 'N/A'}")
                    
                    # Make sure to close and rollback this row's transaction
                    if cursor:
                        try:
                            cursor.close()
                        except:
                            pass
                    if raw_conn:
                        try:
                            raw_conn.rollback()
                            raw_conn.close()
                        except:
                            pass
                    # Continue to next row
                    continue
            
            logger.info(f"✅ Successfully inserted {inserted_count} out of {len(full_data)} rows into {table_name}")
            logger.info(f"❌ Failed to insert {failed_count} rows")
            
            if inserted_count == 0:
                logger.error(f"❌ No rows were inserted! Check SQL statement and data format.")
                raise Exception("Insert operation returned 0 rows inserted")
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}", exc_info=True)
            raise