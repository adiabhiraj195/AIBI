import asyncio
import os
import logging
from dotenv import load_dotenv
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# List of CORE tables that should NOT be dropped
# Note: 'rag_embeddings' is a core table but contains data derived from CSVs, so we truncate it but don't drop it.
CORE_TABLES = [
    'alembic_version',
    'users',
    'csv_documents',
    'document_metadata',
    'file_registry',
    'knowledge_base',
    'rag_embeddings',
    'conversation_history',
    'chat_sessions', 
    'messages',
    'dashboard_items',
    'data_sync_state',
    'prediction_cache',
    'spatial_ref_sys' # PostGIS table
]

async def reset_data():
    """
    Reset all CSV-related data:
    1. Drop all dynamic tables (tables not in CORE_TABLES)
    2. Truncate CSV-related core tables: csv_documents, file_registry, etc.
    3. PRESERVE: users, conversation_history, dashboard_items (unless requested otherwise)
    """
    # Use DB_* variables from .env as seen in config.py
    user = os.getenv('DB_USER', 'suzlon_user')
    password = os.getenv('DB_PASSWORD', 'suzlon_password')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    dbname = os.getenv('DB_NAME', 'Suzlon_Backend')

    db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    logger.info(f"Connecting to database at {host}:{port}/{dbname}...")
    try:
        conn = await asyncpg.connect(db_url)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return

    try:
        # 1. Identify dynamic tables
        logger.info("Scanning for dynamic tables to drop...")
        rows = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        
        all_tables = [r['table_name'] for r in rows]
        
        # Identify tables to drop (any table not in CORE_TABLES)
        tables_to_drop = [t for t in all_tables if t not in CORE_TABLES]
        
        logger.info(f"Found {len(tables_to_drop)} dynamic tables to drop: {tables_to_drop}")
        
        if not tables_to_drop:
            logger.info("No dynamic tables found.")
        
        # 2. Drop dynamic tables
        for table in tables_to_drop:
            logger.info(f"Dropping table: {table}")
            await conn.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')

        # 3. Truncate CSV-related core tables (Data cleanup)
        # We assume 'rag_embeddings' should be cleared as it depends on the files.
        # We assume 'knowledge_base', 'file_registry', 'document_metadata', 'csv_documents' should be cleared.
        logger.info("Truncating CSV tracking tables...")
        
        truncatement_tables = [
            'rag_embeddings',
            'knowledge_base',
            'document_metadata',
            'file_registry',
            'csv_documents'
        ]
        
        # Filter to make sure they exist before truncating
        existing_truncate_tables = [t for t in truncatement_tables if t in all_tables]
        
        if existing_truncate_tables:
            logger.info(f"Truncating tables: {existing_truncate_tables}")
            await conn.execute(f"""
                TRUNCATE TABLE {', '.join(existing_truncate_tables)}
                RESTART IDENTITY CASCADE
            """)
        
        logger.info("✅ Data reset complete! All CSV data and dynamic tables have been removed.")
        logger.info("NOTE: User accounts and Chat History were PRESERVED.")
        
    except Exception as e:
        logger.error(f"Error during reset: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(reset_data())
