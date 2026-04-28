// Database service layer
// In production, these would call your Python backend's database endpoints

export interface DatabaseSchema {
  tables: TableInfo[];
  relationships: Relationship[];
}

export interface TableInfo {
  name: string;
  schema: string;
  columns: ColumnInfo[];
  rowCount?: number;
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  description?: string;
}

export interface Relationship {
  fromTable: string;
  fromColumn: string;
  toTable: string;
  toColumn: string;
  type: 'one-to-many' | 'many-to-one' | 'one-to-one';
}

// Get database schema information
export async function getDatabaseSchema(): Promise<DatabaseSchema> {
  const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) 
    ? import.meta.env.VITE_API_URL 
    : 'http://localhost:8000';

  try {
    const response = await fetch(`${API_BASE_URL}/api/database/schema`);
    if (!response.ok) {
      throw new Error(`Failed to fetch database schema: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch database schema:', error);
    throw error;
  }
}

// Execute a SQL query (via backend)
export async function executeQuery(sql: string): Promise<any[]> {
  const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) 
    ? import.meta.env.VITE_API_URL 
    : 'http://localhost:8000';

  try {
    console.log('Executing SQL:', sql);
    
    const response = await fetch(`${API_BASE_URL}/api/database/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sql })
    });
    
    if (!response.ok) {
      throw new Error(`Query execution failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to execute query:', error);
    throw error;
  }
}

// Get table statistics
export async function getTableStats(tableName: string): Promise<{
  rowCount: number;
  lastUpdated: Date;
  sizeBytes: number;
}> {
  const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) 
    ? import.meta.env.VITE_API_URL 
    : 'http://localhost:8000';

  try {
    const response = await fetch(`${API_BASE_URL}/api/database/table/${tableName}/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch table stats: ${response.status}`);
    }
    
    const data = await response.json();
    return {
      rowCount: data.row_count,
      lastUpdated: new Date(data.last_updated),
      sizeBytes: data.size_bytes
    };
  } catch (error) {
    console.error('Failed to fetch table stats:', error);
    throw error;
  }
}
