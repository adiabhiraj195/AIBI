"""
EmbeddingManager for Multi-Agent Chatbot Copilot
Manages embedding operations and model loading for RAG system
"""

import os
import logging
from typing import List, Optional, Dict, Any
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from config import settings

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages embedding generation and storage operations"""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self._model_loaded = False
    
    def load_model(self) -> None:
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {settings.rag.embedding_model}")
            self.model = SentenceTransformer(settings.rag.embedding_model)
            self._model_loaded = True
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode_text(self, text: str) -> List[float]:
        """
        Encode a single text into embedding vector
        
        Args:
            text: Text to encode
            
        Returns:
            List of float values representing the embedding
        """
        if not self._model_loaded:
            self.load_model()
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode multiple texts into embedding vectors
        
        Args:
            texts: List of texts to encode
            
        Returns:
            List of embedding vectors
        """
        if not self._model_loaded:
            self.load_model()
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            raise
    
    def create_embeddings_table(self) -> None:
        """Create the rag_embeddings table if it doesn't exist"""
        try:
            conn = psycopg2.connect(
                host=settings.database.host,
                port=settings.database.port,
                database=settings.database.name,
                user=settings.database.user,
                password=settings.database.password
            )
            cur = conn.cursor()
            
            # Create extension and table
            cur.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;
                
                CREATE TABLE IF NOT EXISTS rag_embeddings (
                    doc_id              BIGINT PRIMARY KEY,
                    source_file         TEXT,
                    data_type           TEXT,
                    business_context    TEXT,
                    customer_name       TEXT,
                    state               TEXT,
                    formatted_period    TEXT,
                    project_phase       TEXT,
                    fiscalyear          TEXT,
                    ryear               TEXT,
                    business_module     TEXT,
                    wtg_model           TEXT,
                    wtg_type            TEXT,
                    capacity            FLOAT,
                    model_bucket        TEXT,
                    wtg_count           FLOAT,
                    mwg                 FLOAT,
                    wtg_count_deviation FLOAT,
                    mwg_deviation       FLOAT,
                    content             TEXT,
                    embedding           vector(768)
                );
            """)
            
            # Create vector index
            cur.execute("""
                DO $
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_rag_embeddings'
                    ) THEN
                        CREATE INDEX idx_rag_embeddings
                        ON rag_embeddings USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100);
                    END IF;
                END$;
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info("RAG embeddings table and index created successfully")
            
        except Exception as e:
            if "could not open extension control file" in str(e) and "vector.control" in str(e):
                logger.warning(f"⚠️ 'pgvector' extension not installed on Postgres server. RAG capabilities will be disabled. Error: {e}")
                # Do NOT raise, allow app to start without RAG
                return
            
            logger.error(f"Failed to create embeddings table: {e}")
            raise
    
    def generate_embeddings_from_csv(self, csv_path: str, batch_size: int = 100) -> None:
        """
        Generate embeddings from CSV data and store in database
        
        Args:
            csv_path: Path to CSV file with data
            batch_size: Number of records to process in each batch
        """
        try:
            # Load dataset
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded dataset: {len(df)} records from {csv_path}")
            
            # Load model
            if not self._model_loaded:
                self.load_model()
            
            # Connect to database
            conn = psycopg2.connect(
                host=settings.database.host,
                port=settings.database.port,
                database=settings.database.name,
                user=settings.database.user,
                password=settings.database.password
            )
            cur = conn.cursor()
            
            # Process in batches
            data_to_insert = []
            
            for i, row in tqdm(df.iterrows(), total=len(df), desc="Processing records"):
                text = str(row["content"])
                emb = self.encode_text(text)
                
                data_to_insert.append((
                    int(row["doc_id"]),
                    row["source_file"],
                    row["data_type"],
                    row["business_context"],
                    row["customer_name"],
                    row.get("state") if pd.notna(row.get("state")) else None,
                    row["formatted_period"],
                    row["project_phase"],
                    row["fiscalyear"],
                    row.get("ryear") if pd.notna(row.get("ryear")) else None,
                    row.get("business_module") if pd.notna(row.get("business_module")) else None,
                    row.get("wtg_model") if pd.notna(row.get("wtg_model")) else None,
                    row.get("wtg_type") if pd.notna(row.get("wtg_type")) else None,
                    float(row.get("capacity")) if pd.notna(row.get("capacity")) else None,
                    row.get("model_bucket") if pd.notna(row.get("model_bucket")) else None,
                    float(row["wtg_count"]) if pd.notna(row["wtg_count"]) else None,
                    float(row["mwg"]) if pd.notna(row["mwg"]) else None,
                    float(row["wtg_count_deviation"]) if pd.notna(row["wtg_count_deviation"]) else 0.0,
                    float(row["mwg_deviation"]) if pd.notna(row["mwg_deviation"]) else 0.0,
                    row["content"],
                    emb
                ))
                
                # Batch insert
                if len(data_to_insert) >= batch_size:
                    self._insert_batch(cur, data_to_insert)
                    conn.commit()
                    data_to_insert = []
            
            # Insert remaining records
            if data_to_insert:
                self._insert_batch(cur, data_to_insert)
                conn.commit()
            
            cur.close()
            conn.close()
            
            logger.info(f"Successfully processed {len(df)} records")
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings from CSV: {e}")
            raise
    
    def _insert_batch(self, cursor, data_batch: List[tuple]) -> None:
        """Insert a batch of data into the database"""
        execute_batch(cursor, """
            INSERT INTO rag_embeddings (
                doc_id, source_file, data_type, business_context,
                customer_name, state, formatted_period, project_phase, fiscalyear, ryear,
                business_module, wtg_model, wtg_type, capacity, model_bucket,
                wtg_count, mwg, wtg_count_deviation, mwg_deviation, content, embedding
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
            ON CONFLICT (doc_id) DO NOTHING;
        """, data_batch)