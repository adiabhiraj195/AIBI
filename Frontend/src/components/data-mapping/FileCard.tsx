import React, { useState } from 'react';
import clsx from 'clsx';
import { ChevronRight, Trash2 } from 'lucide-react';
import type { FileData } from '../../types/data-mapping';
import { deleteUploadedFile } from '../../services/api';

export function FileCard({ file, onSelect, onDelete }: { file: FileData; onSelect: () => void; onDelete?: (fileId: number) => void }) {
    const [isDeleting, setIsDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState<string | null>(null);

    const statusStyles: Record<FileData['mappingStatus'], string> = {
        'Not Started': 'bg-slate-800 text-slate-200 border-slate-700',
        'In Progress': 'bg-amber-900/40 text-amber-200 border-amber-500/40',
        Mapped: 'bg-emerald-900/30 text-emerald-100 border-emerald-500/40'
    };

    const handleDelete = async (e: React.MouseEvent) => {
        e.stopPropagation();

        if (!window.confirm(`Are you sure you want to delete "${file.name}"?`)) {
            return;
        }

        setIsDeleting(true);
        setDeleteError(null);

        try {
            await deleteUploadedFile(file.id);
            console.log(`[FileCard] Successfully deleted file: ${file.name}`);
            onDelete?.(file.id);
        } catch (error: any) {
            const errorMessage = error?.message || 'Failed to delete file';
            setDeleteError(errorMessage);
            console.error(`[FileCard] Failed to delete file:`, error);
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <div>
            {deleteError && (
                <div className="mb-2 rounded-lg bg-red-900/30 border border-red-500/40 p-2 text-xs text-red-200">
                    {deleteError}
                </div>
            )}
            <button
                className="group max-w-100 w-fit flex h-fit flex-col rounded-xl border border-slate-800/70 bg-slate-950/70 p-4 text-left shadow-lg transition-all duration-[380ms] ease-in-out hover:-translate-y-1 hover:border-emerald-500/50 hover:shadow-emerald-500/10"
                onClick={onSelect}
            >
                <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 text-lg font-semibold text-white">
                            <span className="truncate" title={file.name}>{file.name}</span>
                            <span className="rounded-full bg-slate-800 px-2 py-[2px] text-xs text-emerald-200 whitespace-nowrap">{file.type}</span>
                        </div>
                        <p className="text-sm text-slate-400">
                            {file.rows.toLocaleString()} rows • {file.columns} columns
                        </p>
                    </div>
                    <div className="flex items-start gap-2">
                        <span
                            className={clsx(
                                'rounded-full border px-3 py-1 text-xs font-medium transition-colors duration-200',
                                statusStyles[file.mappingStatus]
                            )}
                        >
                            {file.mappingStatus}
                        </span>
                        <button
                            onClick={handleDelete}
                            disabled={isDeleting}
                            className="flex-shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-red-900/30 hover:text-red-300 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Delete file"
                            aria-label="Delete file"
                        >
                            {isDeleting ? (
                                <div className="w-4 h-4 border-2 border-red-500/30 border-t-red-500 rounded-full animate-spin"></div>
                            ) : (
                                <Trash2 className="w-4 h-4" />
                            )}
                        </button>
                    </div>
                </div>

                <div className="mt-4 rounded-lg border border-slate-800/60 bg-slate-900/70 p-3">
                    <div className="mb-2 flex items-center justify-between text-xs text-slate-400">
                        <span>Preview</span>
                        <span className="flex items-center gap-1 text-emerald-200">
                            <ChevronRight className="h-3 w-3" />
                            Click to map
                        </span>
                    </div>
                    <div className="overflow-hidden rounded-md border border-slate-800/60">
                        <table className="w-full border-collapse text-xs text-slate-200">
                            <thead className="bg-slate-900/80 text-slate-400">
                                <tr>
                                    {file.preview.columns.slice(0, 4).map((col) => (
                                        <th key={col} className="px-3 py-2 text-left font-medium">
                                            {col}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {file.preview.rows.slice(0, 3).map((row, idx) => (
                                    <tr key={idx} className="border-t border-slate-800/60">
                                        {file.preview.columns.slice(0, 4).map((col) => (
                                            <td key={col} className="px-3 py-2 text-slate-300">
                                                {row[col]}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </button>
        </div>
    );
}
