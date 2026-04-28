import { Card } from './ui/card';
import { Activity, Database, Zap, Clock, Server } from 'lucide-react';

interface SystemMetricsProps {
  systemStatus?: {
    apiHealth: boolean;
    dbConnected: boolean;
    llmProvider: string;
  };
}

export function SystemMetrics({ systemStatus }: SystemMetricsProps) {
  // Note: These metrics should come from the backend API in production
  const metrics = [
    {
      label: 'Database',
      value: systemStatus?.dbConnected ? 'Connected' : 'Offline',
      icon: Database,
      color: systemStatus?.dbConnected ? 'text-green-600' : 'text-red-600',
      bgColor: systemStatus?.dbConnected ? 'bg-green-50' : 'bg-red-50'
    },
    {
      label: 'LLM Provider',
      value: systemStatus?.llmProvider || 'Not Available',
      icon: Zap,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50'
    }
  ];

  return (
    <div className="p-6 space-y-4">
      <h3 className="text-white mb-4">System Status</h3>
      
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <div 
            key={metric.label}
            className="flex items-center gap-3 p-3 rounded-lg bg-gray-900/30"
          >
            <div className={`w-10 h-10 ${metric.bgColor.replace('bg-blue-50', 'bg-emerald-500/20').replace('bg-green-50', 'bg-emerald-500/20').replace('bg-red-50', 'bg-red-500/20').replace('bg-amber-50', 'bg-amber-500/20')} rounded-lg flex items-center justify-center`}>
              <Icon className={`w-5 h-5 ${metric.color.replace('text-blue-600', 'text-emerald-400').replace('text-green-600', 'text-emerald-400').replace('text-red-600', 'text-red-400').replace('text-amber-600', 'text-amber-400')}`} />
            </div>
            <div className="flex-1">
              <p className="text-xs text-gray-500">{metric.label}</p>
              <p className="text-gray-200">{metric.value}</p>
            </div>
          </div>
        );
      })}

      <div className="pt-4 mt-4 border-t border-gray-800/50">
        <h4 className="text-sm text-gray-300 mb-3">System Status</h4>
        <div className="text-xs text-gray-500">
          <p>Backend configuration and metrics will be displayed here when connected to the API.</p>
        </div>
      </div>
    </div>
  );
}