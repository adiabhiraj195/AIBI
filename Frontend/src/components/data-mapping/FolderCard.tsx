import React from 'react';
import { Folder, FileText, CheckCircle2, Trash2, Loader2 } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import type { FolderData } from '../../types/data-mapping';

interface FolderCardProps {
    folder: FolderData;
    onSelect: () => void;
    onDelete?: () => void;
    isDeleting?: boolean;
}

export function FolderCard({ folder, onSelect, onDelete, isDeleting }: FolderCardProps) {
    const progressColor =
        folder.mappingProgress === 100
            ? 'text-emerald-400'
            : folder.mappingProgress > 0
                ? 'text-amber-400'
                : 'text-slate-400';

    return (
        <Card
            className="group h-fit cursor-pointer overflow-hidden border-slate-800/80 bg-slate-950/60 transition-all hover:border-emerald-600/50 hover:shadow-lg hover:shadow-emerald-900/20"
            onClick={onSelect}
        >
            <CardContent className="p-4">
                <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-800/70 transition-colors group-hover:bg-emerald-600/20">
                        <Folder className="h-6 w-6 text-emerald-400 transition-transform group-hover:scale-110" />
                    </div>
                    <div className="flex items-center gap-2">
                        <div className={`flex items-center gap-1 text-xs font-medium ${progressColor}`}>
                            {folder.mappingProgress === 100 && <CheckCircle2 className="h-3.5 w-3.5" />}
                            {folder.mappingProgress}%
                        </div>
                        {onDelete && (
                            <button
                                aria-label="Delete folder"
                                disabled={isDeleting}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDelete();
                                }}
                                className="flex items-center gap-1 rounded-md border border-slate-800 bg-slate-900 px-2 py-1 text-xs text-slate-300 transition-colors hover:border-red-500 hover:text-red-100 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {isDeleting ? (
                                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                ) : (
                                    <Trash2 className="h-3.5 w-3.5" />
                                )}
                                <span>Delete</span>
                            </button>
                        )}
                    </div>
                </div>

                <h3 className="mb-1 truncate text-base font-semibold text-white group-hover:text-emerald-100">
                    {folder.name}
                </h3>

                <p className="mb-3 text-xs text-slate-400">{folder.uploadDate}</p>

                <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                        <FileText className="h-3.5 w-3.5" />
                        {folder.fileCount} {folder.fileCount === 1 ? 'file' : 'files'}
                    </span>
                    <span>•</span>
                    <span>{folder.totalRows.toLocaleString()} rows</span>
                </div>

                <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                    <div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-600 to-emerald-400 transition-all duration-500"
                        style={{ width: `${folder.mappingProgress}%` }}
                    />
                </div>
            </CardContent>
        </Card>
    );
}
