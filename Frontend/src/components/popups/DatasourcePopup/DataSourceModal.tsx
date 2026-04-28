import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, BarChart3, Upload, Cloud, Sheet, Zap, Package, Boxes, Wifi } from 'lucide-react';
import { Button } from '../../ui/button';
import { uploadSingleFile, uploadMultipleFiles, checkDocumentByName } from '../../../services/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../../ui/dialog';
import { ConnectionCard } from './ConnectionCard';

type UploadGroup = {
    id: number;
    name: string;
    fileIds: number[];
    createdAt: string;
};

const UPLOAD_GROUPS_KEY = 'uploadFileGroups';

const loadUploadGroups = (): UploadGroup[] => {
    if (typeof window === 'undefined') return [];
    try {
        const raw = localStorage.getItem(UPLOAD_GROUPS_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (err) {
        console.warn('[DataSourceModal] Failed to read upload groups from localStorage:', err);
        return [];
    }
};

const saveUploadGroup = (fileIds: number[]) => {
    if (typeof window === 'undefined') return;
    const groups = loadUploadGroups();
    const now = new Date();
    const newGroup: UploadGroup = {
        id: Date.now(),
        name: `Upload Batch ${now.toLocaleString()}`,
        fileIds,
        createdAt: now.toISOString()
    };
    const next = [...groups, newGroup];
    try {
        localStorage.setItem(UPLOAD_GROUPS_KEY, JSON.stringify(next));
    } catch (err) {
        console.warn('[DataSourceModal] Failed to save upload group to localStorage:', err);
    }
};

interface DataSourceModalProps {
    open: boolean;
    onClose: () => void;
    onUploadComplete?: () => void;
}

// Map icon names to lucide-react components
export const getIconComponent = (iconName: string) => {
    const iconMap: { [key: string]: React.ReactNode } = {
        'file': <Upload className="w-5 h-5" />,
        'database': <Database className="w-5 h-5" />,
        'cloud': <Cloud className="w-5 h-5" />,
        'sheets': <Sheet className="w-5 h-5" />,
        'api': <Zap className="w-5 h-5" />,
        'warehouse': <Package className="w-5 h-5" />,
        'integration': <Boxes className="w-5 h-5" />,
        'stream': <Wifi className="w-5 h-5" />,
    };
    return iconMap[iconName] || <Database className="w-5 h-5" />;
};

export function DataSourceModal({ open, onClose, onUploadComplete }: DataSourceModalProps) {
    const navigate = useNavigate();
    const [mode, setMode] = useState<'grid' | 'upload'>("grid");
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [previews, setPreviews] = useState<Record<string, { kind: 'csv' | 'json' | 'other'; rows?: string[][]; text?: string }>>({});
    const inputRef = useRef<HTMLInputElement>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [uploadedItems, setUploadedItems] = useState<Array<{
        id: number;
        filename: string;
        preview?: any;
        row_count?: number;
        column_count?: number;
    }>>([]);
    const [uploadSuccess, setUploadSuccess] = useState(false);
    const [showFilenameHelp, setShowFilenameHelp] = useState(false);
    const [showDuplicateWarning, setShowDuplicateWarning] = useState(false);
    const [duplicateFileName, setDuplicateFileName] = useState<string | null>(null);

    const isCSV = (file: File) => file.type.includes('csv') || file.name.toLowerCase().endsWith('.csv');
    const isJSON = (file: File) => file.type.includes('json') || file.name.toLowerCase().endsWith('.json');

    const isValidFilename = (file: File) => {
        // Enforce pattern: name_part-01132026.csv (exactly one dash, 8-digit date, .csv)
        const name = file.name;
        const csvPattern = /^[^-]+-[0-9]{8}\.csv$/;
        return csvPattern.test(name);
    };
    const addFiles = async (files: FileList | File[]) => {
        const arr = Array.from(files);
        if (arr.length === 0) return;

        for (const file of arr) {
            // Only allow CSV files with strict naming convention
            if (!isCSV(file)) {
                setUploadError('Only .csv files are supported for upload.');
                continue;
            }

            if (!isValidFilename(file)) {
                setUploadError('File name must follow pattern name_of_file-01132026.csv.');
                setShowFilenameHelp(true);
                continue;
            }

            // Check if already uploaded by calling backend
            try {
                const check = await checkDocumentByName(file.name);
                if (check?.exists) {
                    setUploadError(`File "${file.name}" has already been uploaded.`);
                    setDuplicateFileName(file.name);
                    setShowDuplicateWarning(true);
                    continue;
                }
            } catch (err: any) {
                // Log but allow user to proceed if check fails, or block? Here we block to be safe.
                console.warn('[DataSourceModal] Failed to check document by name:', err);
                setUploadError('Unable to verify if file was already uploaded. Please try again later.');
                continue;
            }

            setSelectedFiles((prev) => {
                const existing = new Set(prev.map((f) => f.name));
                if (existing.has(file.name)) return prev;
                return [...prev, file];
            });

            // Build preview
            try {
                if (isCSV(file)) {
                    const text = await file.text();
                    const lines = text.split(/\r?\n/).slice(0, 5).filter(Boolean);
                    const rows = lines.map((l) => l.split(','));
                    setPreviews((p) => ({ ...p, [file.name]: { kind: 'csv', rows } }));
                } else if (isJSON(file)) {
                    const text = await file.text();
                    let pretty = text;
                    try {
                        const parsed = JSON.parse(text);
                        pretty = JSON.stringify(parsed, null, 2).slice(0, 800);
                    } catch {
                        pretty = text.slice(0, 800);
                    }
                    setPreviews((p) => ({ ...p, [file.name]: { kind: 'json', text: pretty } }));
                } else {
                    setPreviews((p) => ({ ...p, [file.name]: { kind: 'other' } }));
                }
            } catch {
                setPreviews((p) => ({ ...p, [file.name]: { kind: 'other' } }));
            }
        }
    };

    const onFilesChosen = (files: FileList | null) => {
        if (!files || files.length === 0) return;
        setUploadError(null);
        void addFiles(files);
    };

    const removeFile = (name: string) => {
        setSelectedFiles((prev) => prev.filter((f) => f.name !== name));
        setPreviews((p) => {
            const { [name]: _, ...rest } = p;
            return rest;
        });
    };

    const MAX_SIZE_BYTES = 200 * 1024 * 1024; // 200MB
    const uploadFiles = async () => {
        setUploadError(null);
        if (selectedFiles.length === 0) {
            setUploadError('Please add at least one file.');
            return;
        }
        // Validate sizes
        const tooLarge = selectedFiles.find(f => f.size > MAX_SIZE_BYTES);
        if (tooLarge) {
            setUploadError(`File "${tooLarge.name}" exceeds the 200MB limit.`);
            return;
        }
        setIsUploading(true);
        try {
            // Use the appropriate endpoint based on file count
            const response = selectedFiles.length === 1
                ? await uploadSingleFile(selectedFiles[0])
                : await uploadMultipleFiles(selectedFiles);

            if (response?.success && Array.isArray(response.data)) {
                const uploaded = response.data.map((d: any) => ({
                    id: d.id,
                    filename: d.filename,
                    preview: d.preview,
                    row_count: d.row_count,
                    column_count: d.column_count,
                }));
                setUploadedItems(uploaded);

                // Persist multi-file upload grouping for folder display later
                if (uploaded.length > 1) {
                    const fileIds = uploaded.map((d) => d.id).filter((id) => typeof id === 'number');
                    if (fileIds.length > 0) {
                        saveUploadGroup(fileIds);
                    }
                }

                // Reset selection and show success state in-modal
                setSelectedFiles([]);
                setPreviews({});
                setUploadSuccess(true);

                // Trigger refetch in parent component
                if (onUploadComplete) {
                    onUploadComplete();
                }
            } else {
                throw new Error(response?.message || 'Unexpected server response.');
            }
        } catch (err: any) {
            setUploadError(err?.message || 'Something went wrong while uploading.');
        } finally {
            setIsUploading(false);
        }
    };

    const handleDrop: React.DragEventHandler<HTMLDivElement> = (e) => {
        e.preventDefault();
        e.stopPropagation();
        onFilesChosen(e.dataTransfer.files);
    };

    if (mode === 'upload') {
        return (
            <div className="flex flex-col gap-4 relative max-h-[80vh] overflow-y-auto pr-1">
                {/* Loading Overlay */}
                {isUploading && (
                    <div className="absolute inset-0 z-50 bg-slate-900/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                        <div className="text-center">
                            <div className="w-16 h-16 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4"></div>
                            <p className="text-white text-lg font-medium mb-2">Uploading files...</p>
                            <p className="text-slate-300 text-sm">Please wait while we process your {selectedFiles.length === 1 ? 'file' : 'files'}</p>
                        </div>
                    </div>
                )}

                {/* Filename Format Help Popup */}
                {showFilenameHelp && (
                    <div className="absolute inset-0 z-40 bg-slate-950/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                        <div className="max-w-md w-full mx-4 bg-slate-900 border border-emerald-500/40 rounded-2xl p-6 shadow-2xl space-y-4">
                            <h3 className="text-lg font-semibold text-white">File name format required</h3>
                            <p className="text-sm text-slate-200">
                                To upload a file, please use the following naming format:
                            </p>
                            <div className="rounded-md bg-slate-800/80 px-3 py-2 text-sm font-mono text-emerald-300">
                                name_of_file-01132026.csv
                            </div>
                            <ul className="list-disc list-inside text-xs text-slate-300 space-y-1">
                                <li>Use any descriptive name on the left (letters, numbers, underscores allowed).</li>
                                <li>Include exactly one dash <span className="font-mono">-</span> before the date.</li>
                                <li>Use an 8-digit date on the right in MMDDYYYY format (e.g. 01132026 for Jan 13, 2026).</li>
                                <li>End the filename with the <span className="font-mono">.csv</span> extension.</li>
                            </ul>
                            <div className="flex justify-end gap-2 pt-2">
                                <Button
                                    variant="outline"
                                    className="border-emerald-500/40 text-slate-100 hover:bg-emerald-600/10"
                                    onClick={() => setShowFilenameHelp(false)}
                                >
                                    Got it
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Duplicate File Warning Popup */}
                {showDuplicateWarning && (
                    <div className="absolute inset-0 z-40 bg-slate-950/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                        <div className="max-w-md w-full mx-4 bg-slate-900 border border-yellow-400/60 rounded-2xl p-6 shadow-2xl space-y-4">
                            <h3 className="text-lg font-semibold text-white">File already uploaded</h3>
                            <p className="text-sm text-slate-200">
                                The file
                                {" "}
                                <span className="font-mono text-yellow-300">{duplicateFileName}</span>
                                {" "}
                                has already been uploaded.
                            </p>
                            <p className="text-xs text-slate-300">
                                To avoid duplicate processing, please rename the file or use a different dataset. You can review all previously uploaded files from the Uploaded Data page.
                            </p>
                            <div className="flex justify-end gap-2 pt-2">
                                <Button
                                    variant="outline"
                                    className="border-slate-600 text-slate-100 hover:bg-slate-800/80"
                                    onClick={() => {
                                        setShowDuplicateWarning(false);
                                        setDuplicateFileName(null);
                                    }}
                                >
                                    Close
                                </Button>
                                <Button
                                    className="bg-emerald-600 hover:bg-emerald-700 text-white"
                                    onClick={() => {
                                        setShowDuplicateWarning(false);
                                        setDuplicateFileName(null);
                                        navigate('/uploaded-data');
                                        onClose();
                                    }}
                                >
                                    View Uploaded Files
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Success Banner */}
                {uploadSuccess && (
                    <div className="rounded-xl border border-emerald-500/30 bg-emerald-900/40 p-4 text-white">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                            <div>
                                <p className="text-sm font-semibold">Upload complete</p>
                                <p className="text-emerald-100 text-sm">
                                    {uploadedItems.length} {uploadedItems.length === 1 ? 'file' : 'files'} uploaded successfully.
                                </p>
                            </div>
                            <div className="flex gap-2">
                                <Button
                                    className="bg-white text-emerald-700 hover:bg-emerald-100"
                                    onClick={() => {
                                        navigate('/uploaded-data');
                                        onClose();
                                    }}
                                >
                                    View Uploaded Files
                                </Button>
                                <Button
                                    variant="outline"
                                    className="border-emerald-500/40 text-emerald-100 hover:bg-emerald-500/10"
                                    onClick={() => setUploadSuccess(false)}
                                >
                                    Upload More
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
                <DialogHeader>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
                                <Upload className="w-5 h-5 text-emerald-300" />
                            </div>
                            <div>
                                <p className="text-xs uppercase tracking-wider text-emerald-300/80">Upload</p>
                                <DialogTitle className="text-white">Upload your data files</DialogTitle>
                            </div>
                        </div>
                        <Button variant="ghost" className="text-slate-300 hover:text-white" onClick={() => setMode('grid')}>
                            ← Back
                        </Button>
                    </div>
                    <DialogDescription className="text-slate-300 mt-2">
                        Drag and drop files anywhere in the area below, or click to select files.
                    </DialogDescription>
                </DialogHeader>

                <div
                    onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                    onDrop={handleDrop}
                    className="w-full min-h-[60vh] rounded-2xl border-2 border-dashed border-emerald-500/30 bg-slate-900/40 p-4"
                >
                    {selectedFiles.length === 0 ? (
                        <div className="h-full min-h-[50vh] flex items-center justify-center text-center px-8 py-12">
                            <div>
                                <div className="mx-auto w-16 h-16 rounded-xl bg-emerald-600/15 border border-emerald-500/20 flex items-center justify-center mb-4">
                                    <Upload className="w-7 h-7 text-emerald-300" />
                                </div>
                                <p className="text-white mb-2">Drop files here</p>
                                <p className="text-slate-400 text-sm mb-6">CSV, XLS, XLSX, JSON up to 25MB</p>
                                <Button onClick={() => inputRef.current?.click()} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                                    Choose Files
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-3 h-full">
                            <div className="flex items-center justify-between">
                                <p className="text-slate-300 text-sm">Selected files ({selectedFiles.length})</p>
                                <Button variant="outline" className="border-emerald-500/30 text-slate-200" onClick={() => inputRef.current?.click()}>
                                    Add more files
                                </Button>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {selectedFiles.map((f) => {
                                    const preview = previews[f.name];
                                    return (
                                        <div key={f.name} className="relative rounded-xl border border-slate-800/60 bg-slate-900/60 p-4">
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="min-w-0">
                                                    <p className="text-white text-sm truncate" title={f.name}>{f.name}</p>
                                                    <p className="text-slate-500 text-xs">{(f.size / 1024).toFixed(1)} KB</p>
                                                </div>
                                                <button className="text-slate-400 hover:text-white text-xs" onClick={() => removeFile(f.name)}>Remove</button>
                                            </div>
                                            <div className="mt-3 overflow-auto max-h-48 rounded-md border border-slate-800/50">
                                                {preview?.kind === 'csv' && preview.rows && (
                                                    <table className="w-full text-left text-xs text-slate-300">
                                                        <tbody>
                                                            {preview.rows.map((row, i) => (
                                                                <tr key={i} className="border-b border-slate-800/40">
                                                                    {row.map((cell, j) => (
                                                                        <td key={j} className="px-2 py-1 whitespace-nowrap">{cell}</td>
                                                                    ))}
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                )}
                                                {preview?.kind === 'json' && (
                                                    <pre className="text-xs text-slate-300 p-2 whitespace-pre-wrap">{preview.text}</pre>
                                                )}
                                                {!preview || preview.kind === 'other' ? (
                                                    <div className="text-xs text-slate-400 p-2">No preview available</div>
                                                ) : null}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                            {/* {uploadedItems.length > 0 && (
                                <div className="mt-4">
                                    <p className="text-slate-300 text-sm mb-2">Uploaded</p>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {uploadedItems.map((item) => (
                                            <button
                                                key={item.id}
                                                className="text-left rounded-xl border border-slate-800/60 bg-slate-900/60 p-4 hover:border-emerald-500/40"
                                                onClick={() => navigate(`/data/${item.id}`)}
                                            >
                                                <p className="text-white text-sm truncate" title={item.filename}>{item.filename}</p>
                                                <p className="text-slate-500 text-xs mb-2">{item.row_count ?? 0} rows • {item.column_count ?? 0} columns</p>
                                                <div className="overflow-auto max-h-40 rounded-md border border-slate-800/50">
                                                    {Array.isArray(item.preview) ? (
                                                        <pre className="text-xs text-slate-300 p-2 whitespace-pre-wrap">{JSON.stringify(item.preview.slice(0, 5), null, 2)}</pre>
                                                    ) : (
                                                        <div className="text-xs text-slate-400 p-2">No preview available</div>
                                                    )}
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )} */}
                        </div>
                    )}
                    <input
                        ref={inputRef}
                        type="file"
                        className="hidden"
                        multiple
                        accept=".csv"
                        onChange={(e) => onFilesChosen(e.target.files)}
                    />
                </div>

                {/* {selectedFiles.length > 0 && (
                    <div className="mt-2 text-slate-300 text-sm">
                        {selectedFiles.map((f) => (
                            <div key={f.name} className="flex items-center justify-between py-1 border-b border-slate-800/50">
                                <span className="truncate max-w-[70%]">{f.name}</span>
                                <span className="text-slate-500 text-xs">{(f.size / 1024).toFixed(1)} KB</span>
                            </div>
                        ))}
                    </div>
                )} */}
                <DialogFooter>
                    <Button variant="ghost" className="text-slate-300 hover:text-white" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button className="bg-emerald-600 hover:bg-emerald-700 text-white" onClick={uploadFiles} disabled={isUploading || selectedFiles.length === 0}>
                        {isUploading ? 'Uploading...' : 'Upload Files'}
                    </Button>
                </DialogFooter>
            </div>
        );
    }

    // Default: grid view
    return (
        <div>
            <DialogHeader>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
                            <Database className="w-5 h-5 text-emerald-300" />
                        </div>
                        <div>
                            <p className="text-xs uppercase tracking-wider text-emerald-300/80">Data Source</p>
                            <DialogTitle className="text-white">Connect your financial systems</DialogTitle>
                        </div>
                    </div>
                    <Button
                        variant="outline"
                        className="border-emerald-500/30 text-slate-200 hover:bg-emerald-600/10"
                        onClick={() => {
                            navigate('/uploaded-data');
                            onClose();
                        }}
                    >
                        Review All Files
                    </Button>
                </div>
                <DialogDescription className="text-slate-300 mt-2">
                    Connect PostgreSQL, Snowflake, or upload CSVs to let the CFO Assistant run live analyses. Add credentials securely and we will never store sensitive data in plain text.
                </DialogDescription>
            </DialogHeader>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-h-[60vh] w-full overflow-y-auto">
                {DATA_CONNECTION_OPTIONS.map((option) => (
                    <ConnectionCard
                        key={option.id}
                        title={option.title}
                        description={option.description}
                        icon={getIconComponent(option.icon)}
                        badge={option.category}
                        supported={
                            option.supportedFormats ||
                            option.supportedDatabases ||
                            option.supportedProviders
                        }
                        ctaLabel={option.ctaLabel}
                        disabled={option.status === "coming_soon"}
                        accent={option.theme.accentColor as "blue" | "green" | "purple" | "yellow" | "pink"}
                        onAction={option.id === 'file_upload' ? () => setMode('upload') : undefined}
                    />
                ))}
            </div>
        </div>
    );
}



export const DATA_CONNECTION_OPTIONS = [
    {
        id: "file_upload",
        title: "Upload File",
        description: "Upload CSV, Excel, or JSON files from your computer",
        category: "MVP",
        icon: "file",
        supportedFormats: ["CSV", "XLS", "XLSX", "JSON"],
        connectionType: "file",
        authRequired: false,
        status: "available",
        ctaLabel: "Upload",
        theme: {
            accentColor: "blue",
            gradient: "Gradient / Accent / Blue"
        }
    },

    {
        id: "sql_database",
        title: "Connect Database",
        description: "Securely connect to your SQL database",
        category: "MVP",
        icon: "database",
        supportedDatabases: [
            "PostgreSQL",
            "MySQL",
            "SQL Server"
        ],
        connectionType: "database",
        authRequired: true,
        status: "available",
        ctaLabel: "Connect",
        theme: {
            accentColor: "green",
            gradient: "Gradient / Accent / Green"
        }
    },

    {
        id: "cloud_storage",
        title: "Cloud Storage",
        description: "Import data from S3 or compatible cloud storage",
        category: "MVP",
        icon: "cloud",
        supportedProviders: [
            "AWS S3",
            "S3-Compatible Storage"
        ],
        connectionType: "cloud",
        authRequired: true,
        status: "available",
        ctaLabel: "Connect",
        theme: {
            accentColor: "purple",
            gradient: "Gradient / Accent / Purple"
        }
    },

    {
        id: "google_sheets",
        title: "Google Sheets",
        description: "Sync data directly from Google Sheets",
        category: "MVP+",
        icon: "sheets",
        supportedProviders: ["Google"],
        connectionType: "oauth",
        authRequired: true,
        authMethod: "OAuth 2.0",
        status: "available",
        ctaLabel: "Sign in with Google",
        theme: {
            accentColor: "yellow",
            gradient: "Gradient / Accent / Yellow"
        }
    },

    {
        id: "api_import",
        title: "API Import",
        description: "Fetch structured data from a REST API",
        category: "MVP+",
        icon: "api",
        supportedAuth: [
            "API Key",
            "Bearer Token",
            "Basic Auth"
        ],
        connectionType: "api",
        authRequired: true,
        status: "available",
        ctaLabel: "Configure API",
        theme: {
            accentColor: "pink",
            gradient: "Gradient / Accent / Pink"
        }
    },

    {
        id: "data_warehouse",
        title: "Data Warehouse",
        description: "Connect to enterprise data warehouses",
        category: "Enterprise",
        icon: "warehouse",
        supportedProviders: [
            "Snowflake",
            "BigQuery",
            "Redshift"
        ],
        connectionType: "warehouse",
        authRequired: true,
        status: "coming_soon",
        ctaLabel: "Coming Soon",
        theme: {
            accentColor: "blue",
            gradient: "Gradient / Card / Default"
        }
    },

    {
        id: "saas_integrations",
        title: "Business Systems",
        description: "Integrate ERP, CRM, and finance tools",
        category: "Enterprise",
        icon: "integration",
        supportedProviders: [
            "SAP",
            "Oracle",
            "Salesforce",
            "NetSuite"
        ],
        connectionType: "saas",
        authRequired: true,
        status: "coming_soon",
        ctaLabel: "Coming Soon",
        theme: {
            accentColor: "purple",
            gradient: "Gradient / Card / Default"
        }
    },

    {
        id: "live_stream",
        title: "Live Data Stream",
        description: "Stream real-time data into dashboards",
        category: "Enterprise",
        icon: "stream",
        supportedProviders: [
            "Kafka",
            "Kinesis",
            "Webhooks"
        ],
        connectionType: "stream",
        authRequired: true,
        status: "coming_soon",
        ctaLabel: "Coming Soon",
        theme: {
            accentColor: "green",
            gradient: "Gradient / Card / Default"
        }
    }
];
