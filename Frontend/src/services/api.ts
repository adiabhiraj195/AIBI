// API Service Layer for CFO Multi-Agent Chatbot
// This integrates with the Python FastAPI backend running LangGraph multi-agent system

import {
  QueryRequest,
  QueryResponse,
  AgentStage,
  AgentType,
  ChartType,
  QueryIntentType,
  SystemStatus,
  ErrorResponse,
  LoginRequest,
  LoginResponse,
  User
} from '../types';

const API_BASE_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_URL)
  ? (import.meta as any).env.VITE_API_URL
  : 'http://localhost:8000';

// CSV Backend (port 8001) for file uploads, documents, and feedback
const CSV_API_BASE_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_CSV_API_URL)
  ? (import.meta as any).env.VITE_CSV_API_URL
  : 'http://localhost:8001';

// File upload
export interface UploadResponseItem {
  id: number;
  filename: string;
  upload_date?: string;
  is_described?: boolean;
  preview?: any;
  row_count?: number;
  column_count?: number;
}

export interface DocumentDetail {
  id: number;
  filename: string;
  upload_date: string;
  is_described: boolean;
  preview: any[];
  row_count: number;
  column_count: number;
  full_data: any[];
}

export interface MetadataColumn {
  column_name: string;
  data_type: string;
  connection_key?: string;
  alias: string;
  description: string;
}

export interface SaveMetadataRequest {
  document_id: number;
  columns: MetadataColumn[];
}

export interface ProcessMetadataResponse {
  success: boolean;
  knowledge_base_id: number;
  message: string;
  summary?: string;
}

export interface UploadResponse {
  success: boolean;
  message?: string;
  data: UploadResponseItem[];
}

// Transform backend response format to frontend expected format
function transformBackendResponse(backendData: any): QueryResponse {
  console.log('[API] Transforming backend response:', backendData);

  // Extract content - your backend puts it directly in the response
  const content = backendData.content || 'Response generated successfully';
  console.log('[API] Extracted content:', content);

  // Map backend response to frontend QueryResponse format
  const transformedResponse: QueryResponse = {
    query_intent: {
      intent_type: backendData.intent || QueryIntentType.GENERAL,
      confidence: backendData.confidence || 0.8,
      entities: [],
      temporal_scope: undefined
    },
    agent_responses: [
      {
        agent_name: AgentType.INSIGHTS,
        content: content,
        visualizations: backendData.visualizations || [],
        confidence: backendData.confidence || 0.8,
        execution_time: backendData.total_execution_time || 0,
        follow_up_questions: backendData.follow_up_questions || [],
        // Don't include cfo_response to avoid any mock data
        cfo_response: undefined
      }
    ],
    conversation_context: {
      session_id: backendData.session_id || 'unknown',
      user_id: 'demo_user',
      previous_queries: [],
      previous_responses: [],
      current_topic: undefined
    },
    processing_stages: backendData.agent_stages?.map((stage: any) => ({
      agent_name: mapAgentName(stage.agent_name),
      status: mapAgentStatus(stage.status),
      duration: stage.execution_time,
      output: stage.message
    })) || [
        {
          agent_name: AgentType.ORCHESTRATOR,
          status: 'completed' as const,
          duration: backendData.total_execution_time || 0,
          output: 'Query processed successfully'
        }
      ],
    total_execution_time: backendData.total_execution_time || 0,
    timestamp: new Date().toISOString()
  };

  console.log('[API] Transformed response - agent_responses:', transformedResponse.agent_responses);
  console.log('[API] Transformed response - processing_stages:', transformedResponse.processing_stages);
  return transformedResponse;
}

// Helper function to map backend agent names to frontend AgentType
function mapAgentName(backendAgentName: string): AgentType {
  const mapping: Record<string, AgentType> = {
    'orchestrator': AgentType.ORCHESTRATOR,
    'insights': AgentType.INSIGHTS,
    'visualization': AgentType.VISUALIZATION,
    'forecasting': AgentType.FORECASTING,
    'follow_up': AgentType.FOLLOWUP,
    'followup': AgentType.FOLLOWUP
  };

  return mapping[backendAgentName.toLowerCase()] || AgentType.ORCHESTRATOR;
}

// Helper function to map backend agent status to frontend format
function mapAgentStatus(backendStatus: string): 'pending' | 'processing' | 'completed' | 'error' {
  const mapping: Record<string, 'pending' | 'processing' | 'completed' | 'error'> = {
    'ready': 'completed',
    'completed': 'completed',
    'processing': 'processing',
    'pending': 'pending',
    'error': 'error',
    'failed': 'error'
  };

  return mapping[backendStatus.toLowerCase()] || 'completed';
}

// Main API endpoint for query processing
export async function* processQuery(
  request: QueryRequest,
  onStageUpdate?: (stage: AgentStage) => void
): AsyncGenerator<QueryResponse, void, unknown> {
  try {
    console.log('[API] Sending query to backend:', request);

    // Try production endpoint first
    try {
      const response = await fetch(`${API_BASE_URL}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      console.log('[API] Connected to backend successfully');

      // Check if response is streaming
      const contentType = response.headers.get('content-type');

      if (contentType?.includes('application/json')) {
        // Non-streaming response (single JSON object)
        const data = await response.json();
        console.log('[API] Received response:', data);

        // Transform backend response to frontend format
        const transformedResponse = transformBackendResponse(data);
        console.log('[API] About to yield transformed response');

        // Update agent stages if callback provided
        if (transformedResponse.processing_stages && onStageUpdate) {
          console.log('[API] Updating agent stages:', transformedResponse.processing_stages);
          transformedResponse.processing_stages.forEach((stage: AgentStage) => onStageUpdate(stage));
        }

        yield transformedResponse;
        console.log('[API] Successfully yielded response');
        return; // Explicitly return to end the generator
      } else {
        // Streaming response (SSE or chunked)
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        let buffer = '';

        while (true) {
          const { done, value } = await reader!.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Split by newlines to handle multiple JSON objects
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep last incomplete line

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) continue;

            try {
              const data = JSON.parse(trimmed);
              console.log('[API] Received chunk:', data);

              // Transform backend response to frontend format
              const transformedResponse = transformBackendResponse(data);

              // Update agent stages if callback provided
              if (transformedResponse.processing_stages && onStageUpdate) {
                transformedResponse.processing_stages.forEach((stage: AgentStage) => onStageUpdate(stage));
              }

              yield transformedResponse;
            } catch (parseError) {
              console.warn('[API] Failed to parse chunk:', trimmed);
            }
          }
        }

        // Process any remaining data in buffer
        if (buffer.trim()) {
          try {
            const data = JSON.parse(buffer);

            // Transform backend response to frontend format
            const transformedResponse = transformBackendResponse(data);

            if (transformedResponse.processing_stages && onStageUpdate) {
              transformedResponse.processing_stages.forEach((stage: AgentStage) => onStageUpdate(stage));
            }
            yield transformedResponse;
          } catch (parseError) {
            console.warn('[API] Failed to parse final chunk:', buffer);
          }
        }
      }
    } catch (fetchError) {
      console.error('[API] Backend connection failed:', fetchError);
      throw new Error('Backend service unavailable. Please ensure the backend server is running.');
    }
  } catch (error) {
    console.error('[API] Query processing error:', error);
    throw error;
  }
}











// System health and status endpoints

export async function checkAPIHealth(): Promise<boolean> {
  try {
    console.log('[API] Checking backend health at:', `${API_BASE_URL}/health`);
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });
    const healthy = response.ok;
    console.log('[API] Backend health status:', healthy);
    return healthy;
  } catch (error) {
    console.warn('[API] Backend health check failed:', error);
    return false;
  }
}

export async function getDatabaseStatus(): Promise<{
  connected: boolean;
  host: string;
  database: string;
  embedding_count?: number;
  latency?: number;
}> {
  try {
    console.log('[API] Fetching database status');
    const response = await fetch(`${API_BASE_URL}/api/system/database`);

    if (!response.ok) {
      throw new Error('Database status endpoint failed');
    }

    const data = await response.json();
    console.log('[API] Database status:', data);
    return data;
  } catch (error) {
    console.error('[API] Failed to fetch database status:', error);
    throw error;
  }
}

export async function getSystemStatus(): Promise<SystemStatus> {
  try {
    console.log('[API] Fetching system status');
    const response = await fetch(`${API_BASE_URL}/api/system/status`);

    if (!response.ok) {
      throw new Error('System status endpoint failed');
    }

    const data = await response.json();
    console.log('[API] System status:', data);
    return data;
  } catch (error) {
    console.error('[API] Failed to fetch system status:', error);
    throw error;
  }
}

export async function getConversationHistory(sessionId: string, limit: number = 10): Promise<any> {
  try {
    console.log('[API] Fetching conversation history for session:', sessionId);

    const response = await fetch(`${API_BASE_URL}/api/conversation/${sessionId}?limit=${limit}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch conversation: ${response.status}`);
    }

    const data = await response.json();
    console.log('[API] Received conversation history:', data);
    return data;
  } catch (error) {
    console.error('[API] Failed to fetch conversation:', error);
    throw error;
  }
}

export async function clearConversation(sessionId: string): Promise<void> {
  try {
    console.log('[API] Clearing conversation:', sessionId);

    const response = await fetch(`${API_BASE_URL}/api/conversation/${sessionId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error(`Failed to clear conversation: ${response.status}`);
    }
  } catch (error) {
    console.error('[API] Failed to clear conversation:', error);
    throw error;
  }
}

export async function getUserSessions(userId: string): Promise<string[]> {
  try {
    console.log('[API] Fetching sessions for user:', userId);

    const response = await fetch(`${API_BASE_URL}/api/user/${userId}/sessions`);
    if (!response.ok) {
      throw new Error(`Failed to fetch sessions: ${response.status}`);
    }

    const data = await response.json();
    console.log('[API] Received sessions from backend:', data);
    return data.sessions || [];
  } catch (error) {
    console.error('[API] Failed to fetch sessions:', error);
    throw error;
  }
}

export async function getSessionSummary(sessionId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/conversation/${sessionId}/summary`);
    if (!response.ok) throw new Error('Failed to fetch session summary');
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch session summary:', error);
    throw error;
  }
}

// Feedback submission
export interface FeedbackRequest {
  query: string;
  response: string;
  feedback: 'thumbs_up' | 'thumbs_down';
  session_id?: string;
  user_id?: string;
}

export interface FeedbackResponse {
  success: boolean;
  message: string;
  feedback_id: number;
}

export async function submitFeedback(feedbackData: FeedbackRequest): Promise<FeedbackResponse> {
  try {
    console.log('[API] Submitting feedback:', feedbackData);

    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedbackData)
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.status}`);
    }

    const data = await response.json();
    console.log('[API] Feedback submitted successfully:', data);
    return data;
  } catch (error) {
    console.error('[API] Failed to submit feedback:', error);
    throw error;
  }
}

// Upload single file
export async function uploadSingleFile(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append('file', file);

  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/upload-single`, {
      method: 'POST',
      body: form,
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Upload failed with status ${response.status}`);
    }

    const data = await response.json();
    return data as UploadResponse;
  } catch (error) {
    console.error('[API] Failed to upload file:', error);
    throw error;
  }
}

// Upload multiple files
export async function uploadMultipleFiles(files: File[]): Promise<UploadResponse> {
  const form = new FormData();
  files.forEach((file) => form.append('files', file));

  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/upload-multiple`, {
      method: 'POST',
      body: form,
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Upload failed with status ${response.status}`);
    }

    const data = await response.json();
    return data as UploadResponse;
  } catch (error) {
    console.error('[API] Failed to upload files:', error);
    throw error;
  }
}

// Upload data files - automatically uses the correct endpoint
export async function uploadDataFiles(files: File[]): Promise<UploadResponse> {
  if (files.length === 0) {
    throw new Error('No files provided');
  }

  if (files.length === 1) {
    return uploadSingleFile(files[0]);
  } else {
    return uploadMultipleFiles(files);
  }
}

// Get all uploaded files
export async function getUploadedFiles(): Promise<UploadResponseItem[]> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/documents`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch files with status ${response.status}`);
    }

    const data = await response.json();
    // Return array directly as the response is an array
    return Array.isArray(data) ? data : (data.files || data.data || []);
  } catch (error) {
    console.error('[API] Failed to fetch uploaded files:', error);
    throw error;
  }
}

// Check if a document with the given filename already exists
export interface CheckDocumentByNameResponse {
  exists: boolean;
  document_id?: number;
  filename?: string;
}

export async function checkDocumentByName(filename: string): Promise<CheckDocumentByNameResponse> {
  try {
    const url = `${CSV_API_BASE_URL}/api/v1/documents/check-by-name?filename=${encodeURIComponent(filename)}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Failed to check document by name with status ${response.status}`);
    }

    const data = await response.json();
    // Expecting backend to return shape like { exists: boolean, document_id?, filename? }
    return data as CheckDocumentByNameResponse;
  } catch (error) {
    console.error('[API] Failed to check document by name:', error);
    throw error;
  }
}

// Get single document by ID
export async function getDocumentById(documentId: number): Promise<DocumentDetail> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/document?id=${documentId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch document with status ${response.status}`);
    }

    const data = await response.json();
    return data as DocumentDetail;
  } catch (error) {
    console.error('[API] Failed to fetch document:', error);
    throw error;
  }
}

// Delete an uploaded file
export async function deleteUploadedFile(fileId: number): Promise<void> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/document/${fileId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Failed to delete file with status ${response.status}`);
    }
  } catch (error) {
    console.error('[API] Failed to delete file:', error);
    throw error;
  }
}

// Save metadata (column mappings)
export async function saveMetadata(payload: SaveMetadataRequest): Promise<void> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/metadata/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Failed to save metadata with status ${response.status}`);
    }
  } catch (error) {
    console.error('[API] Failed to save metadata:', error);
    throw error;
  }
}

// Process metadata and generate knowledge base
export async function processMetadata(documentId: number): Promise<ProcessMetadataResponse> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/metadata/process/${documentId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Failed to process metadata with status ${response.status}`);
    }

    const data = await response.json();
    return data as ProcessMetadataResponse;
  } catch (error) {
    console.error('[API] Failed to process metadata:', error);
    throw error;
  }
}

// ==================== Authentication API ====================

const AUTH_TOKEN_KEY = 'auth_token';
const AUTH_USER_KEY = 'auth_user';

/**
 * Login user with email or username
 */
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Login failed with status ${response.status}`);
    }

    const data: LoginResponse = await response.json();

    // Store token and user in localStorage
    setAuthToken(data.access_token);
    setAuthUser(data.user);

    return data;
  } catch (error) {
    console.error('[API] Login failed:', error);
    throw error;
  }
}

/**
 * Logout user and clear stored credentials
 */
export function logout(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

/**
 * Get stored auth token
 */
export function getAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Set auth token in localStorage
 */
export function setAuthToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

/**
 * Get stored user data
 */
export function getAuthUser(): User | null {
  const userStr = localStorage.getItem(AUTH_USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

/**
 * Set user data in localStorage
 */
export function setAuthUser(user: User): void {
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAuthToken();
}

/**
 * Get authorization header for API requests
 */
export function getAuthHeader(): Record<string, string> {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Register new user
 */
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  confirm_password: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
  data?: {
    id: number;
    email: string;
    username: string;
    created_at: string;
  };
}

export async function register(credentials: RegisterRequest): Promise<RegisterResponse> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Registration failed with status ${response.status}`);
    }

    const data: RegisterResponse = await response.json();
    return data;
  } catch (error) {
    console.error('[API] Registration failed:', error);
    throw error;
  }
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
  try {
    const response = await fetch(`${CSV_API_BASE_URL}/api/v1/auth/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Failed to get user with status ${response.status}`);
    }

    const user: User = await response.json();
    setAuthUser(user);
    return user;
  } catch (error) {
    console.error('[API] Failed to get current user:', error);
    throw error;
  }
}

// ==================== DASHBOARD API ====================

import { DashboardItem } from '../types';

// Helper to parse JWT
function parseJwt(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

// Helper to get current user ID
function getCurrentUserId(): string {
  const user = getAuthUser();
  const token = getAuthToken();

  // Primary: Use stored user object
  if (user && user.id) {
    return String(user.id);
  }

  // Fallback: Try to extract from token if present (User request: allow if token is present)
  if (token) {
    const decoded = parseJwt(token);
    if (decoded && (decoded.user_id || decoded.id || decoded.sub)) {
      console.log('[API] Extracted User ID from token:', decoded.user_id || decoded.id || decoded.sub);
      return String(decoded.user_id || decoded.id || decoded.sub);
    }
  }

  throw new Error('User not authenticated');
}

export async function saveDashboardItem(title: string, visualization_data: any, description?: string, category: string = 'General'): Promise<DashboardItem> {
  try {
    const userId = getCurrentUserId();
    const response = await fetch(`${API_BASE_URL}/api/dashboard/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        title,
        visualization_data,
        description,
        category
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to save dashboard item: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to save dashboard item:', error);
    throw error;
  }
}

export async function getDashboardItems(user_id: string): Promise<DashboardItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/items?user_id=${user_id}`);
    if (!response.ok) throw new Error('Failed to fetch dashboard items');
    return await response.json();
  } catch (error) {
    console.error('[API] Failed to get dashboard items:', error);
    throw error;
  }
}

export async function deleteDashboardItem(item_id: number): Promise<void> {
  try {
    const userId = getCurrentUserId();
    const response = await fetch(`${API_BASE_URL}/api/dashboard/delete/${item_id}?user_id=${userId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete dashboard item');
  } catch (error) {
    console.error('[API] Failed to delete dashboard item:', error);
    throw error;
  }
}

/**
 * Change password
 */
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface ChangePasswordResponse {
  success: boolean;
  message: string;
  data?: null;
}

export async function changePassword(
  passwords: ChangePasswordRequest
): Promise<ChangePasswordResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(passwords),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Failed to change password with status ${response.status}`);
    }

    const data: ChangePasswordResponse = await response.json();
    return data;
  } catch (error) {
    console.error('[API] Failed to change password:', error);
    throw error;
  }
}

/**
 * Verify token validity
 */
export interface VerifyTokenResponse {
  success: boolean;
  message: string;
  data?: {
    user_id: number;
    email: string;
    username: string;
  };
}

export async function verifyToken(): Promise<VerifyTokenResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/verify-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Token verification failed with status ${response.status}`);
    }

    const data: VerifyTokenResponse = await response.json();
    return data;
  } catch (error) {
    console.error('[API] Token verification failed:', error);
    throw error;
  }
}
