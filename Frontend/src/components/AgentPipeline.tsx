import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';
import { AgentStage } from '../types';

interface AgentPipelineProps {
  stages: AgentStage[];
  compact?: boolean;
}

export function AgentPipeline({ stages, compact = false }: AgentPipelineProps) {
  if (compact) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 mb-2">
          <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
          <span className="text-sm text-gray-400">Processing pipeline...</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {stages.map((stage) => (
            <div key={stage.agent_name} className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition-colors ${
              stage.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
              stage.status === 'processing' ? 'bg-emerald-500/10 text-emerald-400' :
              stage.status === 'error' ? 'bg-red-500/20 text-red-400' :
              'bg-gray-800/50 text-gray-500'
            }`}>
              {stage.status === 'completed' && <CheckCircle2 className="w-3 h-3" />}
              {stage.status === 'processing' && <Loader2 className="w-3 h-3 animate-spin" />}
              {stage.status === 'error' && <XCircle className="w-3 h-3" />}
              {stage.status === 'pending' && <Circle className="w-3 h-3" />}
              <span>{stage.agent_name}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-400 text-sm mr-2">Multi-Agent Pipeline:</span>
      {stages.map((stage, index) => (
        <div key={stage.agent_name} className="flex items-center">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
            stage.status === 'completed' ? 'bg-emerald-500/20' :
            stage.status === 'processing' ? 'bg-emerald-500/10' :
            stage.status === 'error' ? 'bg-red-500/20' :
            'bg-gray-800/50'
          }`}>
            {stage.status === 'completed' && (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            )}
            {stage.status === 'processing' && (
              <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
            )}
            {stage.status === 'error' && (
              <XCircle className="w-4 h-4 text-red-400" />
            )}
            {stage.status === 'pending' && (
              <Circle className="w-4 h-4 text-gray-500" />
            )}
            <span className={`text-sm ${
              stage.status === 'completed' ? 'text-emerald-400' :
              stage.status === 'processing' ? 'text-emerald-400' :
              stage.status === 'error' ? 'text-red-400' :
              'text-gray-500'
            }`}>
              {stage.agent_name}
            </span>
            {stage.duration && (
              <span className="text-xs text-gray-500">
                {stage.duration}ms
              </span>
            )}
          </div>
          {index < stages.length - 1 && (
            <div className={`w-6 h-0.5 mx-1 ${
              stage.status === 'completed' ? 'bg-emerald-500/50' : 'bg-gray-700'
            }`}></div>
          )}
        </div>
      ))}
    </div>
  );
}