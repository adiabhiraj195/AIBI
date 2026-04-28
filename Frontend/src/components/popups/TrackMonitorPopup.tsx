import React, { useEffect } from 'react';
import { X, Activity, CheckCircle, TrendingUp, Wind, Zap } from 'lucide-react';

interface TrackMonitorPopupProps {
  onClose: () => void;
  messageContent: string;
  visualizations?: any[];
}

export function TrackMonitorPopup({ onClose, messageContent, visualizations }: TrackMonitorPopupProps) {
  // Detect monitoring type from content
  const getMonitoringType = () => {
    const content = messageContent.toLowerCase();
    if (content.includes('wind') || content.includes('turbine')) {
      return { type: 'Wind Energy', icon: Wind, color: 'blue' };
    }
    if (content.includes('solar') || content.includes('photovoltaic')) {
      return { type: 'Solar Energy', icon: Zap, color: 'yellow' };
    }
    if (content.includes('energy') || content.includes('power')) {
      return { type: 'Energy Production', icon: TrendingUp, color: 'emerald' };
    }
    return { type: 'Data Monitoring', icon: Activity, color: 'blue' };
  };

  const monitoring = getMonitoringType();
  const Icon = monitoring.icon;

  useEffect(() => {
    // Prevent body scroll when popup is open
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-${monitoring.color}-500/20`}>
              <Icon className={`w-6 h-6 text-${monitoring.color}-400`} />
            </div>
            <h3 className="text-xl font-semibold text-white">Tracking Started</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-6 h-6 text-emerald-400 flex-shrink-0 mt-1" />
            <div>
              <p className="text-white font-medium mb-1">
                {monitoring.type} Monitoring Active
              </p>
              <p className="text-gray-400 text-sm leading-relaxed">
                Successfully started tracking {monitoring.type.toLowerCase()} data. 
                You'll receive real-time updates and alerts for any significant changes.
              </p>
            </div>
          </div>

          {visualizations && visualizations.length > 0 && (
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <p className="text-sm text-gray-300 mb-2">Monitoring includes:</p>
              <ul className="space-y-1">
                {visualizations.map((viz, idx) => (
                  <li key={idx} className="text-sm text-gray-400 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
                    {viz.title || `Visualization ${idx + 1}`}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Activity className="w-4 h-4 animate-pulse" />
            <span>Live monitoring in progress...</span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700">
          <button
            onClick={onClose}
            className="w-full px-4 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
