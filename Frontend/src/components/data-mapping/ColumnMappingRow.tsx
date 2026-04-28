import React, { ChangeEvent, useEffect, useRef } from 'react';
import type { ColumnMapping, SqlType } from '../../types/data-mapping';

const sqlTypes: SqlType[] = [
    'INTEGER',
    'BIGINT',
    'FLOAT',
    'DECIMAL',
    'VARCHAR',
    'TEXT',
    'BOOLEAN',
    'DATE',
    'TIMESTAMP',
    'JSON'
];

export function ColumnMappingRow({
    column,
    connectionOptions = [],
    connectionDisabled = false,
    onChange
}: {
    column: ColumnMapping;
    connectionOptions?: string[];
    connectionDisabled?: boolean;
    onChange: (updates: Partial<ColumnMapping>) => void;
}) {
    const descriptionRef = useRef<HTMLTextAreaElement | null>(null);

    useEffect(() => {
        if (descriptionRef.current) {
            descriptionRef.current.style.height = 'auto';
            descriptionRef.current.style.height = `${descriptionRef.current.scrollHeight}px`;
        }
    }, [column.description]);

    const handleDescriptionResize = (event: ChangeEvent<HTMLTextAreaElement>) => {
        const element = event.currentTarget;
        element.style.height = 'auto';
        element.style.height = `${element.scrollHeight}px`;
        onChange({ description: element.value });
    };

    return (
        <div className="grid grid-cols-12 items-start gap-3 rounded-lg border border-slate-800/70 bg-slate-900/80 p-3 h-fit">
            <div className="col-span-12 sm:col-span-3">
                <p className="text-xs uppercase text-slate-400">Column</p>
                <p className="font-semibold text-white">{column.name}</p>
            </div>
            <div className="col-span-12 sm:col-span-3">
                <label className="text-xs uppercase text-slate-400">Data Type</label>
                <select
                    value={column.selectedType}
                    onChange={(event) => onChange({ selectedType: event.target.value as SqlType })}
                    className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-white outline-none transition focus:border-emerald-500"
                >
                    {sqlTypes.map((type) => (
                        <option key={type} value={type}>
                            {type}
                        </option>
                    ))}
                </select>
            </div>
            <div className="col-span-12 sm:col-span-3">
                <label className="text-xs uppercase text-slate-400">Connection_key</label>
                <select
                    value={column.connectionKey}
                    onChange={(event) => onChange({ connectionKey: event.target.value })}
                    disabled={connectionDisabled || connectionOptions.length === 0}
                    className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-white outline-none transition focus:border-emerald-500 disabled:cursor-not-allowed disabled:border-slate-800/60 disabled:text-slate-500"
                >
                    <option value="">None</option>
                    {connectionOptions.map((option) => (
                        <option key={option} value={option}>
                            {option}
                        </option>
                    ))}
                </select>
                {(connectionDisabled || connectionOptions.length === 0) && (
                    <p className="mt-1 text-xs text-slate-500">
                        {connectionDisabled
                            ? 'Connection key available only within an upload batch.'
                            : 'No other file columns available'}
                    </p>
                )}
            </div>
            <div className="col-span-12 sm:col-span-3">
                <label className="text-xs uppercase text-slate-400">Alias</label>
                <input
                    value={column.alias}
                    onChange={(event) => onChange({ alias: event.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-white outline-none transition focus:border-emerald-500"
                    placeholder="Friendly name"
                />
            </div>
            <div className="col-span-12 ">
                <label className="text-xs uppercase text-slate-400">Description</label>
                <textarea
                    ref={descriptionRef}
                    value={column.description}
                    onChange={handleDescriptionResize}
                    className="mt-1 w-full resize-none rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-white outline-none transition focus:border-emerald-500"
                    placeholder="Context for this column"
                    rows={2}
                />
            </div>
        </div>
    );
}
