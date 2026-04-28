"""Check csv_documents table directly"""
import asyncio
from sqlalchemy import text
from app.database.connection import init_and_get_engine

async def main():
    engine = init_and_get_engine()
    
    print("\n" + "="*70)
    print(" CHECKING csv_documents TABLE")
    print("="*70 + "\n")
    
    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT 
                id,
                filename,
                row_count,
                column_count,
                is_described,
                preview_data IS NOT NULL as has_preview,
                full_data IS NOT NULL as has_full_data,
                length(CAST(full_data AS TEXT)) as full_data_size
            FROM csv_documents
            WHERE id IN (7, 8, 9, 10, 11, 12, 14, 16)
            ORDER BY id
        """))
        
        rows = result.fetchall()
        
        for row in rows:
            print(f"Doc {row[0]}: {row[1]}")
            print(f"  Rows: {row[2]}, Columns: {row[3]}")
            print(f"  Is described: {row[4]}")
            print(f"  Has preview: {row[5]}, Has full_data: {row[6]}")
            print(f"  Full_data size: {row[7] or 0} bytes")
            print()

if __name__ == "__main__":
    asyncio.run(main())
