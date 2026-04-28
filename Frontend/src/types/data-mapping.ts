export type Stage = 'overview' | 'folder' | 'mapping';

export type SqlType =
    | 'INTEGER'
    | 'BIGINT'
    | 'FLOAT'
    | 'DECIMAL'
    | 'VARCHAR'
    | 'TEXT'
    | 'BOOLEAN'
    | 'DATE'
    | 'TIMESTAMP'
    | 'JSON';

export interface FilePreview {
    columns: string[];
    rows: Array<Record<string, string>>;
}

export interface FileData {
    id: number;
    name: string;
    type: string;
    rows: number;
    columns: number;
    mappingStatus: 'Not Started' | 'In Progress' | 'Mapped';
    preview: FilePreview;
    folderId?: number;
}

export interface FolderData {
    id: number;
    name: string;
    uploadDate: string;
    fileCount: number;
    totalRows: number;
    mappingProgress: number; // 0-100
}

export interface ColumnDefinition {
    id: string;
    name: string;
    suggestedType: SqlType;
}

export interface ColumnMapping extends ColumnDefinition {
    selectedType: SqlType;
    alias: string;
    description: string;
    connectionKey: string;
}
