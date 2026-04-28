"""Simple verification: Check tables and manually test insertion"""
import asyncio
from sqlalchemy import text
from app.database.connection import DatabaseConnection
from app.repositories.csv_repository import CSVRepository

async def main():
    print("\n" + "="*70)
    print(" CHECKING DYNAMIC TABLES AND DATA")
    print("="*70 + "\n")
    
    from app.database.connection import init_and_get_engine
    engine = init_and_get_engine()
    
    # List all dynamic tables
    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT IN ('csv_documents', 'document_metadata', 'knowledge_base', 'users', 'alembic_version')
            ORDER BY tablename
        """))
        tables = [row[0] for row in result.fetchall()]
        
    print(f"Found {len(tables)} dynamic tables:")
    for table in tables:
        print(f"  - {table}")
    
    print("\n" + "="*70)
    print(" CHECKING ROW COUNTS")
    print("="*70 + "\n")
    
    # Check row counts
    for table in tables:
        with engine.begin() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"{table}: {count} rows")
    
    print("\n" + "="*70)
    print(" CHECKING DOCUMENTS WITH DATA")
    print("="*70 + "\n")
    
    # Check which documents have full_data
    for doc_id in [14, 16]:
        doc = await CSVRepository.get_document_by_id(doc_id)
        if doc and doc.full_data:
            print(f"Doc {doc_id} ({doc.filename}):")
            print(f"  - Has full_data: {len(doc.full_data)} rows")
            print(f"  - Sample keys: {list(doc.full_data[0].keys())[:5]}")
        else:
            print(f"Doc {doc_id}: No data")

if __name__ == "__main__":
    asyncio.run(main())
