import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Database, Table, Columns, Link as LinkIcon } from 'lucide-react';
import { getDatabaseSchema, type DatabaseSchema } from '../services/database';

export function DatabaseExplorer() {
  const [schema, setSchema] = useState<DatabaseSchema | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSchema();
  }, []);

  const loadSchema = async () => {
    try {
      const data = await getDatabaseSchema();
      setSchema(data);
    } catch (error) {
      console.error('Failed to load schema:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-slate-600">Loading database schema...</p>
          </div>
        </div>
      </Card>
    );
  }

  if (!schema) {
    return (
      <Card className="p-6">
        <div className="text-center text-slate-500">
          <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Failed to load database schema</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <Tabs defaultValue="tables">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-slate-900 flex items-center gap-2">
              <Database className="w-5 h-5" />
              Database Schema
            </h3>
            <p className="text-sm text-slate-500 mt-1">
              PostgreSQL @ 34.232.69.47:5432/Prescience_Dev
            </p>
          </div>
          <TabsList>
            <TabsTrigger value="tables">Tables</TabsTrigger>
            <TabsTrigger value="relationships">Relationships</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="tables" className="mt-0">
          <ScrollArea className="h-[500px]">
            <div className="space-y-4">
              {schema.tables.map((table) => (
                <div 
                  key={table.name}
                  className="border border-slate-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Table className="w-4 h-4 text-blue-600" />
                      <h4 className="text-slate-900">{table.name}</h4>
                    </div>
                    {table.rowCount && (
                      <Badge variant="secondary">
                        {table.rowCount.toLocaleString()} rows
                      </Badge>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    {table.columns.map((column) => (
                      <div 
                        key={column.name}
                        className="flex items-center justify-between text-sm p-2 rounded bg-slate-50"
                      >
                        <div className="flex items-center gap-2">
                          <Columns className="w-3 h-3 text-slate-400" />
                          <span className="text-slate-700">{column.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <code className="text-xs text-slate-600 bg-white px-2 py-0.5 rounded">
                            {column.type}
                          </code>
                          {!column.nullable && (
                            <Badge variant="outline" className="text-xs">
                              NOT NULL
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="relationships" className="mt-0">
          <ScrollArea className="h-[500px]">
            <div className="space-y-3">
              {schema.relationships.map((rel, idx) => (
                <div 
                  key={idx}
                  className="border border-slate-200 rounded-lg p-4"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <LinkIcon className="w-4 h-4 text-blue-600" />
                    <Badge variant="secondary">{rel.type}</Badge>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex items-center gap-2 text-slate-700">
                      <span className="font-medium">{rel.fromTable}</span>
                      <span className="text-slate-400">.</span>
                      <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">
                        {rel.fromColumn}
                      </code>
                    </div>
                    <div className="text-slate-400 ml-4">→</div>
                    <div className="flex items-center gap-2 text-slate-700">
                      <span className="font-medium">{rel.toTable}</span>
                      <span className="text-slate-400">.</span>
                      <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">
                        {rel.toColumn}
                      </code>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </Card>
  );
}
