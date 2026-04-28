import asyncio
import os
import sys
from dotenv import load_dotenv
import asyncpg

# Load environment variables
load_dotenv()

async def migrate_db():
    print("Starting migration...")
    try:
        # Get DB config from env with defaults from .env if load_dotenv works, 
        # otherwise defaults are here but they should match your production env
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "Suzlon_Backend")
        user = os.getenv("DB_USER", "suzlon_user")
        password = os.getenv("DB_PASSWORD", "suzlon_password")
        ssl_mode = os.getenv("DB_SSL_MODE", "disable")

        print(f"Connecting to Postgres at {host}:{port} / DB: {database} / User: {user}")
        
        # Adjust SSL setting for asyncpg
        ssl = False
        if ssl_mode.lower() == "require":
           ssl = True
        elif ssl_mode.lower() == "prefer":
           # asyncpg doesn't fully support 'prefer' same as libpq, usually True or False or context
           ssl = False 

        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            ssl=ssl
        )
        
        print("Connected successfully.")
        
        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dashboard_items'
            );
        """)
        
        if not table_exists:
            print("Error: Table 'dashboard_items' does not exist. Please run the main app creation script first or ensure the DB is initialized.")
            await conn.close()
            return

        print("Checking for 'category' column...")
        # Add column if not exists
        await conn.execute("""
            ALTER TABLE dashboard_items 
            ADD COLUMN IF NOT EXISTS category VARCHAR(255) DEFAULT 'General';
        """)
        
        print("Migration successful: Added 'category' column if it was missing.")
        await conn.close()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(migrate_db())
