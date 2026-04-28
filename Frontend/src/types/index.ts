// Backend Data Models - Matching the Multi-Agent Architecture

export enum AgentType {
  ORCHESTRATOR = 'Orchestrator',
  VISUALIZATION = 'Visualization',
  INSIGHTS = 'Insights',
  FORECASTING = 'Forecasting',
  FOLLOWUP = 'Follow-Up'
}

export enum QueryIntentType {
  VISUALIZATION = 'visualization',
  INSIGHTS = 'insights',
  FORECASTING = 'forecasting',
  GENERAL = 'general'
}

export enum ChartType {
  BAR = 'bar',
  STACKED_BAR = 'stacked_bar',
  LINE = 'line',
  HEATMAP = 'heatmap',
  CHOROPLETH = 'choropleth',
  SCATTER = 'scatter',
  BUBBLE = 'bubble',
  PIE = 'pie',
  DONUT = 'donut',
  WATERFALL = 'waterfall',
  TREEMAP = 'treemap',
  BOX = 'box',
  FUNNEL = 'funnel',
  SANKEY = 'sankey'
}

export interface QueryIntent {
  intent_type: QueryIntentType;
  confidence: number;
  entities: string[];
  temporal_scope?: string;
}

export interface ConversationContext {
  session_id: string;
  user_id: string;
  previous_queries: string[];
  previous_responses: AgentResponse[];
  current_topic?: string;
}

export interface KeyMetric {
  name: string;
  value: number | string;
  unit: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  significance: 'high' | 'medium' | 'low';
}

export interface CFOResponse {
  summary: string; // 4-5 lines
  key_metrics: KeyMetric[];
  recommendations: string[];
  risk_flags: string[];
}

export interface PlotlyChart {
  type: ChartType;
  data: any; // Plotly data format
  layout: any; // Plotly layout format
  config?: any; // Plotly config format
}

export interface AgentStage {
  agent_name: AgentType;
  status: 'pending' | 'processing' | 'completed' | 'error';
  duration?: number;
  output?: string;
}

export interface AgentResponse {
  agent_name: AgentType;
  content: string;
  visualizations: PlotlyChart[];
  confidence: number;
  execution_time: number;
  follow_up_questions: string[];
  cfo_response?: CFOResponse;
  forecast_data?: ForecastData;
}

export interface ForecastData {
  model_type: 'prophet' | 'xgboost';
  predictions: any[];
  confidence_intervals?: {
    lower: number[];
    upper: number[];
  };
  scenario_params?: Record<string, any>;
}

export interface QueryRequest {
  query: string;
  session_id: string;
  user_id?: string;
  context?: Partial<ConversationContext>;
}

export interface QueryResponse {
  query_intent: QueryIntent;
  agent_responses: AgentResponse[];
  conversation_context: ConversationContext;
  processing_stages: AgentStage[];
  total_execution_time: number;
  timestamp: string;
}

export interface ErrorResponse {
  error_type: string;
  message: string;
  suggested_actions: string[];
  fallback_response?: AgentResponse;
}

export interface SessionSummary {
  session_id: string;
  total_queries: number;
  topics_covered: string[];
  start_time: string;
  last_activity: string;
}

// Frontend-specific types
export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  queryResponse?: QueryResponse;
  isProcessing?: boolean;
  userQuery?: string; // The original user query that led to this assistant response
}

export interface ChatSession {
  id: string;
  messages: Message[];
  timestamp: Date;
  title: string;
  summary?: SessionSummary;
  userId?: string;
  lastActivity?: Date;
}

export interface SystemStatus {
  apiHealth: boolean;
  dbConnected: boolean;
  ragSystemActive: boolean;
  modelsLoaded: boolean;
  activeAgents: AgentType[];
}

// Authentication Types
export interface User {
  id: string;
  email?: string;
  username: string;
  name?: string;
  role?: string;
}

export interface LoginRequest {
  email: string; // email or username
  password?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
  expires_in?: number;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface DashboardItem {
  id: number;
  user_id?: string;
  title: string;
  description?: string;
  visualization_data: any;
  layout?: any;
  created_at: string;
  category?: string;
}
