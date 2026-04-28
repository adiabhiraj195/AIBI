import { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Send, Sparkles } from 'lucide-react';

interface ChatInputProps {
  onSubmit: (query: string) => void;
  isProcessing: boolean;
}



export function ChatInput({ onSubmit, isProcessing }: ChatInputProps) {
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
    <div className="space-y-3">
      {/* Suggestions */}


      {/* Input */}
      <div className="flex items-end gap-3">
        <div className="flex-1 relative">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about financial data, operations, or performance..."
            className="min-h-[60px] max-h-[200px] resize-none pr-12 bg-gray-900/30 border-gray-800/50 text-gray-200 placeholder:text-gray-500 focus:border-emerald-500/50"
            disabled={isProcessing}
          />
          <div className="absolute bottom-3 right-3 text-xs text-gray-500">
            {isProcessing ? 'Processing...' : 'Enter to send'}
          </div>
        </div>
        <Button
          onClick={handleSubmit}
          disabled={!query.trim() || isProcessing}
          className="h-[60px] px-6 bg-emerald-600 hover:bg-emerald-700"
          size="lg"
        >
          {isProcessing ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <Send className="w-5 h-5" />
          )}
        </Button>
      </div>
    </div>
  );
}
