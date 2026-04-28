#!/usr/bin/env python3
"""
Flush/clear the local PostgreSQL database - drops all tables and recreates the schema
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "Suzlon_Backend")
DB_USER = os.getenv("DB_USER", "suzlon_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "suzlon_password")

def flush_database():
    """Drop all tables from the database"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        logger.info(f"Connected to database: {DB_NAME}")
        
        # Drop all tables
        logger.info("Dropping all tables...")
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            logger.info("No tables found to drop")
        else:
            for table in tables:
                table_name = table[0]
                cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                    sql.Identifier(table_name)
                ))
                logger.info(f"✅ Dropped table: {table_name}")
        
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Database flushed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error flushing database: {e}")
        return False

if __name__ == "__main__":
    confirm = input(f"⚠️  WARNING: This will DROP ALL TABLES from '{DB_NAME}' database. Are you sure? (yes/no): ")
    if confirm.lower() == "yes":
        success = flush_database()
        sys.exit(0 if success else 1)
    else:
        logger.info("Operation cancelled")
        sys.exit(0)
