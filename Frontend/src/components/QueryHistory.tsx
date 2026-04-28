import { ScrollArea } from './ui/scroll-area';
import { ChatSession } from '../App';
import { Clock, MessageSquare } from 'lucide-react';

interface QueryHistoryProps {
  sessions: ChatSession[];
  onSessionSelect?: (sessionId: string) => void;
  currentSessionId?: string;
}

export function QueryHistory({ sessions, onSessionSelect, currentSessionId }: QueryHistoryProps) {
  // Helper to check if session is from today
  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Separate sessions into today and previous
  const todaySessions = sessions.filter(s => isToday(s.lastActivity || s.timestamp));
  const previousSessions = sessions.filter(s => !isToday(s.lastActivity || s.timestamp));

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 px-4 py-4">
        {sessions.length === 0 ? (
          <div className="text-center py-8">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-700" />
            <p className="text-gray-500 text-sm">No chat history yet</p>
            <p className="text-gray-600 text-xs mt-2">Start a conversation to begin</p>
          </div>
        ) : (
          <div className="space-y-1">
            {todaySessions.length > 0 && (
              <>
                <div className="text-xs text-gray-500 mb-2 px-1">Today</div>
                {todaySessions.map((session) => {
                  const isActive = session.id === currentSessionId;
                  return (
                    <button
                      key={session.id}
                      className={`w-full text-left p-3 rounded-lg transition-all ${
                        isActive 
                          ? 'bg-emerald-500/10 border border-emerald-500/30' 
                          : 'hover:bg-gray-800/30 border border-transparent hover:border-gray-700/50'
                      }`}
                      onClick={() => onSessionSelect?.(session.id)}
                    >
                      <div className="flex items-start gap-2 mb-1">
                        <MessageSquare className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                          isActive ? 'text-emerald-400' : 'text-gray-500'
                        }`} />
                        <p className={`text-sm line-clamp-1 ${
                          isActive ? 'text-emerald-300' : 'text-gray-300'
                        }`}>
                          {session.title}
                        </p>
                      </div>
                      <div className={`flex items-center gap-2 text-xs ml-6 ${
                        isActive ? 'text-emerald-400/70' : 'text-gray-500'
                      }`}>
                        <Clock className="w-3 h-3" />
                        <span>{session.messages.length} messages</span>
                      </div>
                    </button>
                  );
                })}
              </>
            )}
            
            {previousSessions.length > 0 && (
              <>
                <div className="text-xs text-gray-500 mb-2 px-1 mt-4">Previous</div>
                {previousSessions.map((session) => {
                  const isActive = session.id === currentSessionId;
                  return (
                    <button
                      key={session.id}
                      className={`w-full text-left p-3 rounded-lg transition-all ${
                        isActive 
                          ? 'bg-emerald-500/10 border border-emerald-500/30' 
                          : 'hover:bg-gray-800/30 border border-transparent hover:border-gray-700/50'
                      }`}
                      onClick={() => onSessionSelect?.(session.id)}
                    >
                      <div className="flex items-start gap-2 mb-1">
                        <MessageSquare className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                          isActive ? 'text-emerald-400' : 'text-gray-500'
                        }`} />
                        <p className={`text-sm line-clamp-1 ${
                          isActive ? 'text-emerald-300' : 'text-gray-300'
                        }`}>
                          {session.title}
                        </p>
                      </div>
                      <div className={`flex items-center gap-2 text-xs ml-6 ${
                        isActive ? 'text-emerald-400/70' : 'text-gray-500'
                      }`}>
                        <Clock className="w-3 h-3" />
                        <span>
                          {(session.lastActivity || session.timestamp).toLocaleDateString([], { 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
