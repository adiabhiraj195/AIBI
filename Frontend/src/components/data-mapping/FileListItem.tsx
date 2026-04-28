import React from 'react';
import clsx from 'clsx';
import { CheckCircle2 } from 'lucide-react';
import type { FileData } from '../../types/data-mapping';

export function FileListItem({
    file,
    isActive,
    onSelect
}: {
    file: FileData;
    isActive: boolean;
    onSelect: () => void;
}) {
    const statusIcon = file.mappingStatus === 'Mapped' ? (
        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
    ) : null;

    return (
        <button
            onClick={onSelect}
            className={clsx(
                'flex items-center justify-between gap-2 px-4 py-3 transition-all duration-[300ms] ease-in-out',
                isActive ? 'bg-emerald-900/20 text-white' : 'hover:bg-slate-900/60 text-slate-200'
            )}
        >
            <div className="flex flex-col text-left">
                <span className="text-sm font-semibold">{file.name}</span>
                <span className="text-xs text-slate-400">
                    {file.rows.toLocaleString()} rows • {file.columns} columns
                </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
                <span className="rounded-full bg-slate-800 px-2 py-[2px] text-emerald-200">{file.type}</span>
                {statusIcon}
            </div>
        </button>
    );
}
