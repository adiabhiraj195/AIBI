import React, { useState } from 'react';
import { Message, AgentType } from '../types';
import { Avatar } from './ui/avatar';
import { Badge } from './ui/badge';
import { AgentPipeline } from './AgentPipeline';
import { VisualizationPanel } from './VisualizationPanel';
import { ActionButtons } from './ActionButtons';
import { Toast } from './popups/Toast';
import { submitFeedback } from '../services/api';
import { Bot, User, MessageSquare, AlertTriangle, Award, Lightbulb, Star, ThumbsUp, ThumbsDown, Copy } from 'lucide-react';

// Helper function to format LLM response with better structure
function formatLLMResponse(content: string): React.ReactElement {
  if (!content || content === 'Processing...') {
    return <p>{content}</p>;
  }

  // Check if this looks like a structured LLM response
  if (content.includes('Executive Summary:') || content.includes('Key Insights:')) {
    const sections = content.split(/(?=Executive Summary:|Key Insights:|Business Actions:|Risk\/Notes:)/);
    
    return (
      <div className="space-y-4">
        {sections.map((section, index) => {
          if (!section.trim()) return null;
          
          const lines = section.trim().split('\n');
          const title = lines[0];
          const content = lines.slice(1).join('\n').trim();
          
          if (title.includes('Executive Summary:')) {
            return (
              <div key={index}>
                <h4 className="text-emerald-400 font-medium mb-2 flex items-center gap-2">
                  <Award className="w-4 h-4" />
                  Executive Summary
                </h4>
                <p className="text-gray-300 leading-relaxed">{content.replace(/^-\s*/, '')}</p>
              </div>
            );
          } else if (title.includes('Key Insights:')) {
            return (
              <div key={index}>
                <h4 className="text-blue-400 font-medium mb-2 flex items-center gap-2">
                  <Lightbulb className="w-4 h-4" />
                  Key Insights
                </h4>
                <div className="text-gray-300 leading-relaxed whitespace-pre-line">{content}</div>
              </div>
            );
          } else if (title.includes('Business Actions:')) {
            return (
              <div key={index}>
                <h4 className="text-green-400 font-medium mb-2 flex items-center gap-2">
                  <Award className="w-4 h-4" />
                  Business Actions
                </h4>
                <div className="text-gray-300 leading-relaxed whitespace-pre-line">{content}</div>
              </div>
            );
          } else if (title.includes('Risk/Notes:')) {
            return (
              <div key={index}>
                <h4 className="text-amber-400 font-medium mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Risk/Notes
                </h4>
                <div className="text-gray-300 leading-relaxed whitespace-pre-line">{content}</div>
              </div>
            );
          }
          
          return null;
        })}
      </div>
    );
  }

  // For non-structured responses, just display as is
  return <p className="whitespace-pre-line">{content}</p>;
}

interface ChatMessageProps {
  message: Message;
  onFollowupClick: (followup: string) => void;
  userQuery?: string; // The original user query that led to this response
}

export function ChatMessage({ message, onFollowupClick, userQuery }: ChatMessageProps) {
  const [showFavoriteToast, setShowFavoriteToast] = useState(false);
  const [showCopyToast, setShowCopyToast] = useState(false);
  const [showFeedbackToast, setShowFeedbackToast] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<'up' | 'down' | null>(null);
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);

  const handleFavorite = () => {
    setShowFavoriteToast(true);
    setTimeout(() => setShowFavoriteToast(false), 2000);
  };

  const submitFeedbackHandler = async (feedbackType: 'thumbs_up' | 'thumbs_down') => {
    if (isSubmittingFeedback || feedbackGiven !== null) return;
    
    setIsSubmittingFeedback(true);
    
    try {
      const result = await submitFeedback({
        query: userQuery || 'No query available',
        response: message.content,
        feedback: feedbackType,
        session_id: message.queryResponse?.conversation_context?.session_id,
      });

      if (result.success) {
        console.log('[Feedback] Submitted successfully:', result);
        setFeedbackGiven(feedbackType === 'thumbs_up' ? 'up' : 'down');
        setShowFeedbackToast(true);
        setTimeout(() => setShowFeedbackToast(false), 2000);
      }
    } catch (error) {
      console.error('[Feedback] Error submitting feedback:', error);
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  const handleThumbsUp = () => {
    submitFeedbackHandler('thumbs_up');
  };

  const handleThumbsDown = () => {
    submitFeedbackHandler('thumbs_down');
  };

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setShowCopyToast(true);
      setTimeout(() => setShowCopyToast(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  if (message.type === 'user') {
    return (
      <div className="flex items-start gap-3 justify-end">
        <div className="max-w-2xl">
          <div className="bg-emerald-600 text-white rounded-2xl rounded-tr-sm px-4 py-3">
            <p>{message.content}</p>
          </div>
          <div className="text-xs text-gray-500 mt-1 text-right px-1">
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        </div>
        <Avatar className="w-9 h-9 bg-emerald-600 flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </Avatar>
      </div>
    );
  }

  // Extract data from query response
  const queryResponse = message.queryResponse;
  const insightsAgent = queryResponse?.agent_responses?.find(r => r.agent_name === AgentType.INSIGHTS);
  const visualizationAgent = queryResponse?.agent_responses?.find(r => r.agent_name === AgentType.VISUALIZATION);
  
  const cfoResponse = insightsAgent?.cfo_response;
  // Check both INSIGHTS and VISUALIZATION agents for visualizations (backend puts them in INSIGHTS)
  const visualizations = insightsAgent?.visualizations || visualizationAgent?.visualizations || [];
  const followUpQuestions = insightsAgent?.follow_up_questions || [];
  
  // Debug logging
  console.log('[ChatMessage] Query response:', queryResponse);
  console.log('[ChatMessage] Insights agent:', insightsAgent);
  console.log('[ChatMessage] Visualizations found:', visualizations);

  return (
    <div className="flex items-start gap-3">
      <Avatar className="w-9 h-9 bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
        <Bot className="w-5 h-5 text-white" />
      </Avatar>
      <div className="flex-1 max-w-3xl">
        {/* Save as Favorite Button */}
        <button
          onClick={handleFavorite}
          className="mb-2 flex items-center gap-2 px-3 py-1.5 bg-gray-800/50 hover:bg-amber-500/20 border border-gray-700 hover:border-amber-500/50 rounded-lg text-gray-400 hover:text-amber-400 transition-all text-sm group"
        >
          <Star className="w-4 h-4 group-hover:fill-amber-400" />
          Save as Favorite
        </button>

        <div className="bg-[#0f1629] rounded-2xl rounded-tl-sm border border-gray-800/50 overflow-hidden">
          {/* Processing State with Agent Pipeline */}
          {message.isProcessing && queryResponse?.processing_stages && (
            <div className="p-4 border-b border-gray-800/50 bg-gray-900/30">
              <AgentPipeline stages={queryResponse.processing_stages} compact />
            </div>
          )}

          {/* Main Content */}
          <div className="p-4">
            {/* CFO Response Summary - Show full content */}
            <div className="text-gray-300 mb-4 leading-relaxed">
              {formatLLMResponse(message.content)}
            </div>



            {/* Visualizations from Visualization Agent */}
            {visualizations && visualizations.length > 0 && (
              <div className="mb-4">
                <VisualizationPanel visualizations={visualizations} />
              </div>
            )}

            {/* Action Buttons - Show after visualizations */}
            {visualizations && visualizations.length > 0 && (
              <ActionButtons 
                messageContent={message.content}
                visualizations={visualizations}
              />
            )}



            {/* Risk Flags from CFO Response */}
            {cfoResponse?.risk_flags && cfoResponse.risk_flags.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  <span className="text-sm text-gray-300">Risk Indicators</span>
                </div>
                <ul className="space-y-2">
                  {cfoResponse.risk_flags.map((risk, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-sm">
                      <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0"></div>
                      <span className="text-gray-400">{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Follow-up Questions - Exactly 4 questions from Follow-Up Agent */}
            {followUpQuestions && followUpQuestions.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <MessageSquare className="w-4 h-4 text-emerald-400" />
                  <span className="text-sm text-gray-300">Suggested Follow-up Questions</span>
                  <Badge variant="outline" className="text-xs border-emerald-500/30 text-emerald-400">
                    {followUpQuestions.length}
                  </Badge>
                </div>
                <div className="space-y-2">
                  {followUpQuestions.map((followup, idx) => (
                    <button
                      key={idx}
                      onClick={() => onFollowupClick(followup)}
                      className="w-full text-left p-3 rounded-lg border border-gray-800/50 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-colors text-sm text-gray-400 hover:text-emerald-400"
                    >
                      <span className="text-emerald-500/70 mr-2">Q{idx + 1}:</span>
                      {followup}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Timestamp and Action Buttons */}
        <div className="flex items-center gap-3 mt-2 px-1">
          <div className="text-xs text-gray-600">
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
          
          {/* Feedback and Copy Buttons */}
          <div className="flex items-center gap-2 ml-auto">
            <button
              onClick={handleThumbsUp}
              disabled={isSubmittingFeedback || feedbackGiven !== null}
              className={`p-1.5 rounded-lg transition-all ${
                feedbackGiven === 'up'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'text-gray-500 hover:text-emerald-400 hover:bg-gray-800/50'
              } ${(isSubmittingFeedback || feedbackGiven !== null) ? 'opacity-50 cursor-not-allowed' : ''}`}
              title="Good response"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            
            <button
              onClick={handleThumbsDown}
              disabled={isSubmittingFeedback || feedbackGiven !== null}
              className={`p-1.5 rounded-lg transition-all ${
                feedbackGiven === 'down'
                  ? 'bg-red-500/20 text-red-400'
                  : 'text-gray-500 hover:text-red-400 hover:bg-gray-800/50'
              } ${(isSubmittingFeedback || feedbackGiven !== null) ? 'opacity-50 cursor-not-allowed' : ''}`}
              title="Bad response"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
            
            <button
              onClick={handleCopyToClipboard}
              className="p-1.5 rounded-lg text-gray-500 hover:text-blue-400 hover:bg-gray-800/50 transition-all"
              title="Copy to clipboard"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Toast Notifications */}
      {showFavoriteToast && <Toast message="Added to favorites!" />}
      {showCopyToast && <Toast message="Copied to clipboard!" />}
      {showFeedbackToast && <Toast message="Feedback submitted!" />}
    </div>
  );
}