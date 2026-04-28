-- Migration: Add FileRegistry table for central file tracking
-- Purpose: Track all uploaded files, their dynamic tables, and verification status

CREATE TABLE IF NOT EXISTS file_registry (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL UNIQUE REFERENCES csv_documents(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL DEFAULT 'csv',
    dynamic_table_name VARCHAR(255),
    data_category VARCHAR(255),
    row_count INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    is_described BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMP,
    upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    table_created_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_file_registry_document_id ON file_registry(document_id);
CREATE INDEX IF NOT EXISTS idx_file_registry_filename ON file_registry(filename);
CREATE INDEX IF NOT EXISTS idx_file_registry_is_described ON file_registry(is_described);
CREATE INDEX IF NOT EXISTS idx_file_registry_data_category ON file_registry(data_category);
CREATE INDEX IF NOT EXISTS idx_file_registry_upload_date ON file_registry(upload_date DESC);

-- Add comment explaining the table
COMMENT ON TABLE file_registry IS 'Central registry tracking all uploaded files, their dynamic tables, and verification status by users';
COMMENT ON COLUMN file_registry.is_described IS 'Flag indicating whether user has verified and described the file metadata';
COMMENT ON COLUMN file_registry.dynamic_table_name IS 'Name of the dynamically created PostgreSQL table for this file''s data';
COMMENT ON COLUMN file_registry.data_category IS 'Data category determined by LLM analysis (e.g., Financial, Customer, Sales, etc.)';
