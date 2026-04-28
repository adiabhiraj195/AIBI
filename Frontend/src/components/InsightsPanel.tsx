import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Lightbulb, MessageSquare, Award } from 'lucide-react';

interface InsightsPanelProps {
  summary?: string;
  insights?: string[];
  followups?: string[];
  qualityScore?: number;
  onFollowupClick: (query: string) => void;
}

export function InsightsPanel({ 
  summary, 
  insights, 
  followups,
  qualityScore,
  onFollowupClick 
}: InsightsPanelProps) {
  if (!summary) {
    return (
      <Card className="p-6">
        <div className="h-96 flex items-center justify-center text-slate-400">
          <div className="text-center">
            <Lightbulb className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Insights will appear here</p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 space-y-6">
      {/* Quality Score */}
      {qualityScore && (
        <div className="flex items-center justify-between pb-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-blue-600" />
            <span className="text-slate-700">Quality Score</span>
          </div>
          <Badge variant={qualityScore >= 8 ? "default" : "secondary"}>
            {qualityScore.toFixed(1)} / 10
          </Badge>
        </div>
      )}

      {/* Executive Summary */}
      <div>
        <h3 className="text-slate-900 mb-3">Executive Summary</h3>
        <p className="text-slate-600 leading-relaxed">
          {summary}
        </p>
      </div>

      {/* Key Insights */}
      {insights && insights.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="w-5 h-5 text-amber-600" />
            <h3 className="text-slate-900">Key Insights</h3>
          </div>
          <ul className="space-y-2">
            {insights.map((insight, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0"></div>
                <span className="text-slate-600">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}



      {/* Follow-up Questions */}
      {followups && followups.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            <h3 className="text-slate-900">Suggested Follow-ups</h3>
          </div>
          <div className="space-y-2">
            {followups.map((followup, idx) => (
              <button
                key={idx}
                onClick={() => onFollowupClick(followup)}
                className="w-full text-left p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm text-slate-600 hover:text-blue-700"
              >
                {followup}
              </button>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
