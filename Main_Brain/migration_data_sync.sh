#!/bin/bash
# Database schema migration script for data sync functionality
# Run this script to prepare your PostgreSQL database for automatic data synchronization

set -e

# Database connection parameters - update these if needed
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-suzlon_copilot}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 Starting Database Schema Migration for Data Sync...${NC}\n"

# Create SQL migration file
MIGRATION_FILE="/tmp/data_sync_migration_$(date +%s).sql"

cat > "$MIGRATION_FILE" << 'EOF'
-- =============================================================================
-- Data Sync Schema Migration
-- Adds tables and columns for automatic CSV sync from backend to RAG system
-- =============================================================================

-- 1. Create data_sync_state table to track sync status
-- This table monitors the synchronization between backend uploads and RAG embeddings
CREATE TABLE IF NOT EXISTS data_sync_state (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL UNIQUE,
    last_sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_synced_document_id BIGINT DEFAULT 0,
    total_documents_synced BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'healthy', -- healthy, syncing, error
    error_message TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for quick service lookups
CREATE INDEX IF NOT EXISTS idx_sync_state_service ON data_sync_state(service_name);

-- 2. Add metadata columns to csv_documents table for RAG processing tracking
-- These columns help track which documents have been processed by the RAG system
ALTER TABLE csv_documents
ADD COLUMN IF NOT EXISTS is_processed_by_rag BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS rag_processed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS embedding_version INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS data_hash VARCHAR(64);

-- Create indexes for efficient sync queries
CREATE INDEX IF NOT EXISTS idx_csv_documents_processed 
ON csv_documents(is_processed_by_rag, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_csv_documents_hash 
ON csv_documents(data_hash);

-- 3. Initialize sync state for Main Brain service
INSERT INTO data_sync_state (service_name, status) 
VALUES ('suzlon-copilot-main-brain', 'healthy')
ON CONFLICT (service_name) DO NOTHING;

-- 4. Optional: Create a sync history table for auditing (future enhancement)
CREATE TABLE IF NOT EXISTS sync_history (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    documents_processed INT DEFAULT 0,
    documents_failed INT DEFAULT 0,
    sync_start_time TIMESTAMP WITH TIME ZONE,
    sync_end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INT,
    status VARCHAR(20), -- success, partial, failed
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_history_service ON sync_history(service_name);
CREATE INDEX IF NOT EXISTS idx_sync_history_created ON sync_history(created_at DESC);

-- =============================================================================
-- Migration complete
-- =============================================================================
EOF

echo -e "${YELLOW}📝 Executing migration...${NC}\n"

# Execute the migration
if [ -z "$DB_PASSWORD" ]; then
    PGPASSWORD="" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
else
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
fi

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Migration completed successfully!${NC}"
    echo -e "${GREEN}✅ Tables and columns created${NC}"
    echo -e "${GREEN}✅ Indexes created for optimal query performance${NC}"
    
    echo -e "\n${YELLOW}📊 Migration Summary:${NC}"
    echo "   • data_sync_state table: Tracks sync status between services"
    echo "   • csv_documents updates: Added RAG processing metadata columns"
    echo "   • Indexes: Created for efficient sync queries"
    echo "   • Sync history table: For future audit trail"
    
    echo -e "\n${YELLOW}🚀 Next Steps:${NC}"
    echo "   1. Restart Suzlon_Copilot_Main_Brain service"
    echo "   2. Monitor sync status via: GET /api/v1/admin/sync/status"
    echo "   3. Trigger manual sync via: POST /api/v1/admin/sync/trigger"
else
    echo -e "\n${RED}❌ Migration failed!${NC}"
    exit 1
fi

# Cleanup
rm -f "$MIGRATION_FILE"

echo -e "\n${GREEN}Done!${NC}"
