import { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { Send, Sparkles } from 'lucide-react';
import { QueryResult } from '../App';

interface QueryInterfaceProps {
  onSubmit: (query: string) => void;
  isProcessing: boolean;
  currentQuery: QueryResult | null;
}

const SAMPLE_QUERIES = [
  'What was the total revenue for E4 turbines in Q3 2024?',
  'Show me the trend of installations by project phase over the last year',
  'Compare profit margins between E3 and E4 models',
  'Which customers contributed the most to revenue this quarter?'
];

export function QueryInterface({ onSubmit, isProcessing, currentQuery }: QueryInterfaceProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = () => {
    if (query.trim() && !isProcessing) {
      onSubmit(query.trim());
      setQuery('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="flex-1">
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about Green.co's financial data, operations, or performance metrics..."
              className="min-h-[100px] resize-none"
              disabled={isProcessing}
            />
          </div>
          <Button 
            onClick={handleSubmit}
            disabled={!query.trim() || isProcessing}
            className="gap-2"
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Processing
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Analyze
              </>
            )}
          </Button>
        </div>

        {!currentQuery && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span className="text-slate-700 text-sm">Try asking:</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {SAMPLE_QUERIES.map((sampleQuery, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(sampleQuery)}
                  className="text-left p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm text-slate-600 hover:text-blue-700"
                  disabled={isProcessing}
                >
                  {sampleQuery}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
