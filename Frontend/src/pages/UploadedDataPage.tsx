
import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import clsx from 'clsx';
import { Button } from '../components/ui/button';
import { FileSpreadsheet, RotateCcw, Save, Send, X, ArrowLeft, ArrowRight } from 'lucide-react';
import type { Stage, FileData, FolderData, ColumnMapping, ColumnDefinition } from '../types/data-mapping';
import { FileCard } from '../components/data-mapping/FileCard';
import { FolderCard } from '../components/data-mapping/FolderCard';
import { FileListItem } from '../components/data-mapping/FileListItem';
import { ColumnMappingRow } from '../components/data-mapping/ColumnMappingRow';
import { getUploadedFiles, getDocumentById, saveMetadata, processMetadata, deleteUploadedFile } from '../services/api';
import { Dialog, DialogContent } from '../components/ui/dialog';
import { DataSourceModal } from '../components/popups/DatasourcePopup/DataSourceModal';
const UPLOAD_GROUPS_KEY = 'uploadFileGroups';

type UploadGroup = {
    id: number;
    name: string;
    fileIds: number[];
    createdAt: string;
};

const loadUploadGroups = (): UploadGroup[] => {
    if (typeof window === 'undefined') return [];
    try {
        const raw = localStorage.getItem(UPLOAD_GROUPS_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (err) {
        console.warn('[UploadedDataPage] Failed to read upload groups from localStorage:', err);
        return [];
    }
};

const saveUploadGroups = (groups: UploadGroup[]) => {
    if (typeof window === 'undefined') return;
    try {
        localStorage.setItem(UPLOAD_GROUPS_KEY, JSON.stringify(groups));
    } catch (err) {
        console.warn('[UploadedDataPage] Failed to persist upload groups to localStorage:', err);
    }
};

const removeUploadGroup = (groupId: number) => {
    const existing = loadUploadGroups();
    const next = existing.filter((group) => group.id !== groupId);
    saveUploadGroups(next);
};

const updateUploadGroupFiles = (groupId: number, fileIds: number[]) => {
    const existing = loadUploadGroups();
    const next = existing
        .map((group) => (group.id === groupId ? { ...group, fileIds } : group))
        .filter((group) => group.fileIds.length > 0);
    saveUploadGroups(next);
};



const createInitialMappings = (fileId: number): ColumnMapping[] => [];

export default function UploadedDataPage() {
    const navigate = useNavigate();
    const [folders, setFolders] = useState<FolderData[]>([]);
    const [files, setFiles] = useState<FileData[]>([]);
    const [activeFolder, setActiveFolder] = useState<FolderData | null>(null);
    const [activeFile, setActiveFile] = useState<FileData | null>(null);
    const [stage, setStage] = useState<Stage>('overview');
    const [mappings, setMappings] = useState<Record<number, ColumnMapping[]>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [loadingFileId, setLoadingFileId] = useState<number | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [processResult, setProcessResult] = useState<{ message: string; summary?: string } | null>(null);
    const [isFolderLoading, setIsFolderLoading] = useState(false);
    const [deletingFolderId, setDeletingFolderId] = useState<number | null>(null);
    const [showSourceModal, setShowSourceModal] = useState(false);

    // Auto-dismiss notification after 8 seconds
    useEffect(() => {
        if (processResult) {
            const timer = setTimeout(() => {
                setProcessResult(null);
            }, 8000);
            return () => clearTimeout(timer);
        }
    }, [processResult]);

    // Fetch uploaded files function
    const fetchFiles = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const documents = await getUploadedFiles();

            // Transform API response to FileData format
            const baseFiles: FileData[] = documents.map((doc) => ({
                id: doc.id,
                name: doc.filename,
                type: doc.filename.split('.').pop()?.toUpperCase() || 'FILE',
                rows: doc.row_count || 0,
                columns: doc.column_count || 0,
                mappingStatus: doc.is_described ? 'Mapped' : 'Not Started',
                folderId: undefined,
                preview: {
                    columns: [],
                    rows: []
                }
            }));

            const uploadGroups = loadUploadGroups();

            // Attach folderId based on saved upload groups
            const filesWithFolders = baseFiles.map((file) => {
                const group = uploadGroups.find((g) => g.fileIds.includes(file.id));
                return group ? { ...file, folderId: group.id } : file;
            });

            // Build folders from groups that still have existing files
            const derivedFolders: FolderData[] = uploadGroups
                .map((group) => {
                    const groupedFiles = filesWithFolders.filter((f) => f.folderId === group.id);
                    if (groupedFiles.length === 0) return null;

                    const totalRows = groupedFiles.reduce((sum, f) => sum + (f.rows || 0), 0);
                    const mappedCount = groupedFiles.filter((f) => f.mappingStatus === 'Mapped').length;
                    const mappingProgress = Math.round((mappedCount / groupedFiles.length) * 100);

                    return {
                        id: group.id,
                        name: group.name || `Upload Batch ${new Date(group.createdAt).toLocaleString()} `,
                        uploadDate: new Date(group.createdAt).toLocaleString(),
                        fileCount: groupedFiles.length,
                        totalRows,
                        mappingProgress
                    } as FolderData;
                })
                .filter(Boolean) as FolderData[];

            setFolders(derivedFolders);
            setFiles(filesWithFolders);

            // Initialize mappings for fetched files
            const initial: Record<number, ColumnMapping[]> = {};
            filesWithFolders.forEach((file) => {
                initial[file.id] = createInitialMappings(file.id);
            });
            setMappings(initial);
        } catch (err: any) {
            console.error('[UploadedDataPage] Failed to fetch files:', err);
            setError(err?.message || 'Failed to load uploaded files');
        } finally {
            setIsLoading(false);
        }
    };

    // Fetch uploaded files on mount
    useEffect(() => {
        fetchFiles();
    }, []);

    const leftBasisClass = stage === 'overview' ? 'basis-[92%]' : stage === 'folder' ? 'basis-[92%]' : 'basis-[25%]';
    const rightBasisClass = stage === 'overview' ? 'basis-[8%]' : stage === 'folder' ? 'basis-[8%]' : 'basis-[75%]';

    const currentFolderFiles = activeFolder ? files.filter((f) => f.folderId === activeFolder.id) : [];

    const connectionOptions = useMemo(() => {
        if (!activeFile || !activeFile.folderId) return [];
        // Only allow connection keys within the same folder (upload batch)
        const otherFiles = files.filter((file) => file.id !== activeFile.id && file.folderId === activeFile.folderId);
        const optionSet = new Set<string>();
        otherFiles.forEach((file) => {
            (mappings[file.id] || []).forEach((column) => {
                optionSet.add(`${column.name} — ${file.name} `);
            });
        });
        return Array.from(optionSet).sort();
    }, [activeFile, files, mappings]);

    const fetchFileDetails = async (file: FileData) => {
        try {
            const document = await getDocumentById(file.id);
            const columns = document.preview && document.preview.length > 0 ? Object.keys(document.preview[0]) : [];

            const columnMappings: ColumnMapping[] = columns.map((colName) => ({
                id: colName,
                name: colName,
                suggestedType: inferDataType(document.preview, colName),
                selectedType: inferDataType(document.preview, colName),
                alias: colName,
                description: '',
                connectionKey: ''
            }));

            const updatedFile: FileData = {
                ...file,
                rows: document.row_count ?? file.rows,
                columns: document.column_count ?? file.columns,
                preview: {
                    columns,
                    rows: document.preview || []
                }
            };

            return { file: updatedFile, mapping: columnMappings };
        } catch (err) {
            console.error('[UploadedDataPage] Failed to fetch document (batch):', err);
            return { file, mapping: mappings[file.id] || createInitialMappings(file.id) };
        }
    };

    const handleFolderSelect = async (folder: FolderData) => {
        setActiveFolder(folder);
        setActiveFile(null);
        const folderFiles = files.filter((f) => f.folderId === folder.id);

        if (folderFiles.length === 0) {
            setStage('folder');
            return;
        }

        setIsFolderLoading(true);
        try {
            const results = await Promise.all(folderFiles.map((f) => fetchFileDetails(f)));

            setFiles((prev) => {
                const map = new Map<number, FileData>(prev.map((f) => [f.id, f] as const));
                results.forEach(({ file }) => {
                    map.set(file.id, file);
                });
                return Array.from(map.values());
            });

            setMappings((prev) => {
                const next = { ...prev };
                results.forEach(({ file, mapping }) => {
                    next[file.id] = mapping;
                });
                return next;
            });

            const first = results[0]?.file;
            if (first) {
                setActiveFile(first);
                setStage('mapping');
            } else {
                setStage('folder');
            }
        } finally {
            setIsFolderLoading(false);
        }
    };

    const handleFolderDelete = async (folder: FolderData) => {
        const folderFiles = files.filter((f) => f.folderId === folder.id);

        // Nothing to delete server-side if folder is empty (stale group)
        if (folderFiles.length === 0) {
            removeUploadGroup(folder.id);
            setFolders((prev) => prev.filter((f) => f.id !== folder.id));
            if (activeFolder?.id === folder.id) {
                setActiveFolder(null);
                setActiveFile(null);
                setStage('overview');
            }
            setProcessResult({ message: 'Folder deleted successfully' });
            return;
        }

        setDeletingFolderId(folder.id);

        const deletedIds = new Set<number>();
        const errors: string[] = [];

        for (const file of folderFiles) {
            try {
                await deleteUploadedFile(file.id);
                deletedIds.add(file.id);
            } catch (err: any) {
                errors.push(`${file.name}: ${err?.message || 'Failed to delete file'} `);
            }
        }

        const updatedFiles = files.filter((f) => !deletedIds.has(f.id));
        setFiles(updatedFiles);

        // Drop mappings for removed files
        setMappings((prev) => {
            const next = { ...prev };
            deletedIds.forEach((id) => delete next[id]);
            return next;
        });

        // Clear active selections if they were deleted
        if (activeFile && deletedIds.has(activeFile.id)) {
            setActiveFile(null);
            setStage(activeFolder?.id === folder.id ? 'folder' : 'overview');
        }

        const remainingFiles = updatedFiles.filter((f) => f.folderId === folder.id);

        if (remainingFiles.length === 0) {
            removeUploadGroup(folder.id);
            setFolders((prev) => prev.filter((f) => f.id !== folder.id));
            if (activeFolder?.id === folder.id) {
                setActiveFolder(null);
                setStage('overview');
            }
        } else {
            const totalRows = remainingFiles.reduce((sum, f) => sum + (f.rows || 0), 0);
            const mappedCount = remainingFiles.filter((f) => f.mappingStatus === 'Mapped').length;
            const progress = Math.round((mappedCount / remainingFiles.length) * 100);

            setFolders((prev) =>
                prev.map((f) =>
                    f.id === folder.id
                        ? { ...f, fileCount: remainingFiles.length, totalRows, mappingProgress: progress }
                        : f
                )
            );

            updateUploadGroupFiles(folder.id, remainingFiles.map((f) => f.id));
        }

        if (errors.length > 0) {
            alert(`Some files could not be deleted: \n${errors.join('\n')} `);
        } else {
            setProcessResult({ message: 'Folder deleted successfully' });
        }

        setDeletingFolderId(null);
    };

    const handleCardSelect = async (file: FileData) => {
        setLoadingFileId(file.id);
        try {
            // If we already have preview data, reuse it without refetching
            if (file.preview?.columns?.length) {
                setActiveFile(file);
                setStage('mapping');
                return;
            }

            // Fetch document details
            const document = await getDocumentById(file.id);

            // Extract columns from preview array (first object's keys)
            const columns = document.preview && document.preview.length > 0
                ? Object.keys(document.preview[0])
                : [];

            // Update file with preview data
            setFiles(prev => prev.map(f =>
                f.id === file.id
                    ? {
                        ...f,
                        preview: {
                            columns: columns,
                            rows: document.preview || []
                        }
                    }
                    : f
            ));

            // Create mappings from preview columns
            if (columns.length > 0) {
                const columnMappings: ColumnMapping[] = columns.map(colName => ({
                    id: colName,
                    name: colName,
                    suggestedType: inferDataType(document.preview, colName),
                    selectedType: inferDataType(document.preview, colName),
                    alias: colName,
                    description: '',
                    connectionKey: ''
                }));

                setMappings(prev => ({
                    ...prev,
                    [file.id]: columnMappings
                }));
            }

            setActiveFile({
                ...file,
                preview: {
                    columns: columns,
                    rows: document.preview || []
                }
            });
            setStage('mapping');
        } catch (err: any) {
            console.error('[UploadedDataPage] Failed to fetch document:', err);
            // Still allow selection but show error
            setActiveFile(file);
            setStage('mapping');
        } finally {
            setLoadingFileId(null);
        }
    };

    const handleListSelect = async (file: FileData) => {
        await handleCardSelect(file);
    };

    // Helper function to infer data type from sample data
    const inferDataType = (data: any[], columnName: string): 'VARCHAR' | 'INTEGER' | 'FLOAT' | 'DECIMAL' | 'DATE' | 'TIMESTAMP' | 'BOOLEAN' => {
        if (!data || data.length === 0) return 'VARCHAR';

        const sampleValues = data.slice(0, 10).map(row => row[columnName]).filter(val => val != null && val !== '');
        if (sampleValues.length === 0) return 'VARCHAR';

        // Check if all values are numbers
        const allNumbers = sampleValues.every(val => !isNaN(Number(val)));
        if (allNumbers) {
            const hasDecimals = sampleValues.some(val => String(val).includes('.'));
            return hasDecimals ? 'DECIMAL' : 'INTEGER';
        }

        // Check if values are dates
        const allDates = sampleValues.every(val => !isNaN(Date.parse(String(val))));
        if (allDates) {
            const hasTime = sampleValues.some(val => String(val).includes(':'));
            return hasTime ? 'TIMESTAMP' : 'DATE';
        }

        // Check if boolean
        const allBooleans = sampleValues.every(val =>
            String(val).toLowerCase() === 'true' ||
            String(val).toLowerCase() === 'false' ||
            val === '1' || val === '0'
        );
        if (allBooleans) return 'BOOLEAN';

        return 'VARCHAR';
    };

    const handleMappingChange = (fileId: number, columnId: string, updates: Partial<ColumnMapping>) => {
        setMappings((prev) => {
            const next = { ...prev };
            next[fileId] = (next[fileId] || []).map((column) =>
                column.id === columnId ? { ...column, ...updates } : column
            );
            return next;
        });

        setFiles((prev) =>
            prev.map((file) =>
                file.id === fileId && file.mappingStatus !== 'Mapped'
                    ? { ...file, mappingStatus: 'In Progress' }
                    : file
            )
        );
    };

    const handleReset = (fileId: number) => {
        setMappings((prev) => ({ ...prev, [fileId]: createInitialMappings(fileId) }));
        setFiles((prev) => prev.map((file) => (file.id === fileId ? { ...file, mappingStatus: 'Not Started' } : file)));
    };

    const handleSave = (fileId: number) => {
        setFiles((prev) => prev.map((file) => (file.id === fileId ? { ...file, mappingStatus: 'Mapped' } : file)));

        // Update folder progress
        if (activeFolder) {
            const folderFiles = files.filter(f => f.folderId === activeFolder.id);
            const mappedCount = folderFiles.filter(f => f.id === fileId || f.mappingStatus === 'Mapped').length;
            const progress = Math.round((mappedCount / folderFiles.length) * 100);
            setFolders(prev => prev.map(folder =>
                folder.id === activeFolder.id ? { ...folder, mappingProgress: progress } : folder
            ));
        }
    };

    const handleSubmit = async (fileId: number) => {
        if (!activeFile) return;

        // Validate all descriptions are filled
        const currentMappings = mappings[fileId] || [];
        const hasEmptyDescriptions = currentMappings.some(col => !col.description?.trim());

        if (hasEmptyDescriptions) {
            alert('Please fill in descriptions for all columns');
            return;
        }

        setIsSubmitting(true);
        try {
            // Prepare payload for save metadata
            const payload = {
                document_id: fileId,
                columns: currentMappings.map(col => ({
                    column_name: col.name,
                    data_type: col.selectedType,
                    connection_key: col.connectionKey || '',
                    alias: col.alias,
                    description: col.description
                }))
            };

            // Step 1: Save metadata
            await saveMetadata(payload);
            console.log('[UploadedDataPage] Metadata saved successfully');

            // Step 2: Process metadata
            const result = await processMetadata(fileId);
            console.log('[UploadedDataPage] Metadata processed:', result);

            // Update file status
            setFiles((prev) => prev.map((file) =>
                file.id === fileId ? { ...file, mappingStatus: 'Mapped' } : file
            ));

            // Show result
            setProcessResult({
                message: result.message,
                summary: result.summary
            });

            // Mark as successfully submitted
            console.log('[UploadedDataPage] Process complete - KB ID:', result.knowledge_base_id);
        } catch (err: any) {
            console.error('[UploadedDataPage] Submit failed:', err);
            alert('Failed to submit: ' + (err?.message || 'Unknown error'));
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleFileDelete = (fileId: number) => {
        // Remove file from list
        setFiles(prev => prev.filter(f => f.id !== fileId));
        // Remove mappings for deleted file
        setMappings(prev => {
            const next = { ...prev };
            delete next[fileId];
            return next;
        });
        // Clear active file if it was deleted
        if (activeFile?.id === fileId) {
            setActiveFile(null);
            setStage('overview');
        }
        // Show success message
        setProcessResult({
            message: 'File deleted successfully'
        });
    };

    const handleBackToFolders = () => {
        setActiveFolder(null);
        setActiveFile(null);
        setStage('overview');
    };

    const handleBackToFiles = () => {
        setActiveFile(null);
        setStage('folder');
    };

    const currentMappings = activeFile ? mappings[activeFile.id] || [] : [];
    const ungroupedFiles = files.filter((f) => !f.folderId);

    // Loading state
    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-white text-lg font-medium">Loading uploaded files...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 flex items-center justify-center">
                <div className="text-center max-w-md">
                    <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <X className="w-8 h-8 text-red-400" />
                    </div>
                    <p className="text-white text-lg font-medium mb-2">Failed to load files</p>
                    <p className="text-slate-400 mb-4">{error}</p>
                    <Button
                        onClick={() => window.location.reload()}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white"
                    >
                        <RotateCcw className="mr-2 h-4 w-4" />
                        Retry
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 overflow-hidden">
            {/* Result Notification */}
            {processResult && (
                <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-emerald-900/95 to-emerald-800/95 border-b border-emerald-500/30 p-4 backdrop-blur-sm">
                    <div className="max-w-7xl mx-auto px-10 flex items-start justify-between gap-4">
                        <div className="flex-1">
                            <p className="text-sm font-semibold text-emerald-300 mb-1">✓ {processResult.message}</p>
                            {processResult.summary && (
                                <p className="text-sm text-emerald-100/80">{processResult.summary}</p>
                            )}
                        </div>
                        <button
                            onClick={() => setProcessResult(null)}
                            className="flex-shrink-0 text-emerald-300 hover:text-emerald-100 transition-colors mt-0.5"
                            aria-label="Close notification"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            )}

            {/* Data Source Dialog */}
            <Dialog open={showSourceModal} onOpenChange={setShowSourceModal}>
                <DialogContent className="min-w-[65vw] max-w-[960px] max-h-[90vh] border-emerald-500/20 bg-linear-to-br from-slate-900 via-slate-950 to-slate-900 shadow-2xl shadow-emerald-900/40 z-50">
                    <DataSourceModal
                        open={showSourceModal}
                        onClose={() => setShowSourceModal(false)}
                        onUploadComplete={fetchFiles}
                    />
                </DialogContent>
            </Dialog>

            <div className="mx-auto px-10 py-6" style={{ paddingTop: processResult ? 'calc(1.5rem + 70px)' : '1.5rem' }}>
                <header className="mb-6 flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-4">
                            <div>
                                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Data onboarding</p>
                                <div className="mt-1 flex items-center gap-2 text-2xl font-semibold text-white">
                                    <FileSpreadsheet className="h-6 w-6 text-emerald-400" />
                                    File Mapping Workspace
                                </div>
                                <div className="mt-2 flex items-center gap-2 text-sm text-slate-400">
                                    {stage === 'folder' && activeFolder && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="text-emerald-400 hover:text-emerald-300 hover:bg-slate-800/50"
                                            onClick={handleBackToFolders}
                                        >
                                            <ArrowLeft className="mr-1 h-4 w-4" />
                                            Back to Folders
                                        </Button>
                                    )}
                                    {stage === 'mapping' && activeFile && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="text-emerald-400 hover:text-emerald-300 hover:bg-slate-800/50"
                                            onClick={handleBackToFolders}
                                        >
                                            <ArrowLeft className="mr-1 h-4 w-4" />
                                            Back to Files
                                        </Button>
                                    )}
                                    {activeFolder && stage !== 'overview' && (
                                        <span className="text-slate-400">Folder: {activeFolder.name}</span>
                                    )}
                                    {activeFile && stage === 'mapping' && (
                                        <span className="text-slate-500">• {activeFile.name}</span>
                                    )}
                                </div>
                            </div>

                        </div>
                    </div>
                    <div className="flex gap-4 justify-center">
                        <Button
                            size="lg"
                            className="bg-emerald-600 hover:bg-emerald-700 text-white"
                            onClick={() => setShowSourceModal(!showSourceModal)}
                        >
                            Connect Data Source
                            <ArrowRight className="w-5 h-5 ml-2" />
                        </Button>
                    </div>

                </header>

                <div className="flex gap-4 transition-all duration-[380ms] ease-in-out h-full">
                    <div
                        className={clsx(
                            'shrink-0 rounded-2xl border border-slate-800/70 bg-slate-900/70 p-4 shadow-2xl transition-all duration-[380ms] ease-in-out',
                            'max-h-[calc(100vh-50px)] min-h-[420px] overflow-y-auto w-full',
                            leftBasisClass
                        )}
                    >
                        {isFolderLoading && (
                            <div className="absolute inset-0 z-20 rounded-2xl bg-slate-950/70 backdrop-blur-sm flex items-center justify-center">
                                <div className="text-center">
                                    <div className="w-10 h-10 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mx-auto mb-3"></div>
                                    <p className="text-sm text-emerald-100">Loading folder files...</p>
                                </div>
                            </div>
                        )}

                        {stage === 'overview' ? (
                            <div className="flex flex-col gap-4 w-full">
                                {folders.length > 0 && (
                                    <div>
                                        <div className="mb-2 flex items-center justify-between">
                                            <p className="text-sm text-slate-300">Upload batches</p>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                                            {folders.map((folder) => (
                                                <FolderCard
                                                    key={folder.id}
                                                    folder={folder}
                                                    onSelect={() => handleFolderSelect(folder)}
                                                    onDelete={() => handleFolderDelete(folder)}
                                                    isDeleting={deletingFolderId === folder.id}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 auto-rows-max w-full">
                                    {ungroupedFiles.map((file) => (
                                        <div key={file.id} className="relative w-full">
                                            {loadingFileId === file.id && (
                                                <div className="absolute inset-0 z-10 bg-slate-900/80 backdrop-blur-sm rounded-xl flex items-center justify-center">
                                                    <div className="w-8 h-8 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin"></div>
                                                </div>
                                            )}
                                            <FileCard
                                                file={file}
                                                onSelect={() => handleCardSelect(file)}
                                                onDelete={handleFileDelete}
                                            />
                                        </div>
                                    ))}
                                    {ungroupedFiles.length === 0 && folders.length === 0 && (
                                        <div className="col-span-full flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800/70 bg-slate-950/40 p-8 text-center">
                                            <FileSpreadsheet className="mb-2 h-8 w-8 text-slate-600" />
                                            <p className="text-sm text-slate-400">No files uploaded yet</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : stage === 'folder' ? (
                            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 auto-rows-max w-full">
                                {currentFolderFiles.map((file) => (
                                    <FileCard key={file.id} file={file} onSelect={() => handleCardSelect(file)} onDelete={handleFileDelete} />
                                ))}
                                {currentFolderFiles.length === 0 && (
                                    <div className="col-span-full flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800/70 bg-slate-950/40 p-8 text-center">
                                        <FileSpreadsheet className="mb-2 h-8 w-8 text-slate-600" />
                                        <p className="text-sm text-slate-400">No files in this folder</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex flex-col divide-y divide-slate-800/80 overflow-hidden rounded-xl border border-slate-800/60 bg-slate-950/40">
                                {(activeFolder
                                    ? files.filter((f) => f.folderId === activeFolder.id)
                                    : activeFile
                                        ? [activeFile]
                                        : files
                                ).map((file) => (
                                    <FileListItem
                                        key={file.id}
                                        file={file}
                                        isActive={activeFile?.id === file.id}
                                        onSelect={() => handleListSelect(file)}
                                    />
                                ))}
                            </div>
                        )}
                    </div>

                    <div
                        className={clsx(
                            'flex-1 rounded-2xl border border-slate-800/70 bg-slate-900/80 p-4 shadow-2xl transition-all duration-[380ms] ease-in-out',
                            'max-h-[calc(100vh-200px)] min-h-[660px] h-full overflow-y-auto',
                            rightBasisClass
                        )}
                    >
                        {stage === 'overview' ? (
                            <div className=" relative flex h-full flex-col items-center justify-center text-center text-slate-400">

                                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-800/70 text-emerald-300">
                                    <FileSpreadsheet className="h-6 w-6" />
                                </div>
                                <p className="absolute top-[550%] left-1/2 -translate-x-1/2 -translate-y-1/2 rotate-90 text-xl uppercase text-emerald-300 whitespace-nowrap">Select a file to begin column mapping</p>

                            </div>
                        ) : stage === 'folder' ? (
                            <div className=" relative flex h-full flex-col items-center justify-center text-center text-slate-400">

                                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-800/70 text-emerald-300">
                                    <FileSpreadsheet className="h-6 w-6" />
                                </div>
                                <p className="absolute top-[550%] left-1/2 -translate-x-1/2 -translate-y-1/2 rotate-90 text-xl uppercase text-emerald-300 whitespace-nowrap">Select a file to begin column mapping</p>

                            </div>
                        ) : activeFile ? (
                            <div className="flex h-full flex-col gap-4">
                                <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/60">
                                    <div>
                                        <div className="flex items-center gap-2 text-lg font-semibold text-white">
                                            {activeFile.name}
                                            <span className="rounded-full bg-slate-800 px-2 py-[2px] text-xs text-emerald-200">
                                                {activeFile.type}
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-400">
                                            {activeFile.rows.toLocaleString()} rows • {activeFile.columns} columns
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Button
                                            variant="outline"
                                            className="border-slate-700 bg-slate-900 text-slate-100 hover:border-emerald-500 hover:text-emerald-100"
                                            onClick={() => handleReset(activeFile.id)}
                                        >
                                            <RotateCcw className="mr-2 h-4 w-4" />
                                            Reset
                                        </Button>
                                        <Button
                                            variant="outline"
                                            className="border-slate-700 bg-slate-900 text-slate-100 hover:border-red-500 hover:text-red-100"
                                            onClick={handleBackToFiles}
                                        >
                                            <X className="mr-2 h-4 w-4" />
                                            Unselect
                                        </Button>
                                    </div>
                                </div>

                                <div className="flex-1 overflow-y-auto grid gap-3 rounded-xl border border-slate-800/60 bg-slate-950/60 p-2">
                                    <div className="grid gap-2">
                                        {currentMappings.map((column) => (
                                            <ColumnMappingRow
                                                key={column.id}
                                                column={column}
                                                connectionOptions={connectionOptions}
                                                connectionDisabled={!activeFile?.folderId}
                                                onChange={(updates) =>
                                                    handleMappingChange(activeFile.id, column.id, updates)
                                                }
                                            />
                                        ))}
                                        {currentMappings.length === 0 && (
                                            <div className="rounded-lg border border-dashed border-slate-800/70 bg-slate-900/50 p-4 text-sm text-slate-400">
                                                No columns detected for this file.
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="flex gap-2 pt-3 border-t border-slate-800/60">
                                    <Button
                                        variant="outline"
                                        className="border-slate-700 bg-slate-900 text-slate-100 hover:border-emerald-500 hover:text-emerald-100"
                                        onClick={() => handleSave(activeFile.id)}
                                    >
                                        <Save className="mr-2 h-4 w-4" />
                                        Save
                                    </Button>
                                    <Button
                                        className="flex-1 bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
                                        onClick={() => handleSubmit(activeFile.id)}
                                        disabled={isSubmitting}
                                    >
                                        {isSubmitting ? (
                                            <>
                                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                                                Processing...
                                            </>
                                        ) : (
                                            <>
                                                <Send className="mr-2 h-4 w-4" />
                                                Submit Form
                                            </>
                                        )}
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <div className="flex h-full flex-col items-center justify-center text-center text-slate-400">
                                <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-800/70 text-emerald-300">
                                    <FileSpreadsheet className="h-6 w-6" />
                                </div>
                                <p className="text-sm">Select a file from the list to map columns</p>
                                <p className="text-xs text-slate-500 mt-1">Configure data types, aliases, and descriptions</p>
                            </div>
                        )}
                    </div>
                </div>
            </div >
        </div >
    );
}
