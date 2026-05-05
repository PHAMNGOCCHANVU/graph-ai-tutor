import axios from 'axios';
import type { InitSessionResponse, StepResponse, RagExplanationResponse } from '@/types/snapshot';
import { useUserStore } from '@/store/userStore';
import { refreshToken } from './auth';
import { refreshTokenWithRetry } from '@/utils/tokenRefresh';
import { getErrorMessage, logError } from '@/utils/errorHandler';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: Thêm Authorization header
apiClient.interceptors.request.use(
  (config) => {
    const state = useUserStore.getState();
    if (state.accessToken) {
      config.headers.Authorization = `Bearer ${state.accessToken}`;
    }
    return config;
  },
  (error) => {
    logError('API Request', error);
    return Promise.reject(error);
  }
);

// Response interceptor: Handle token refresh khi 401 + comprehensive error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 with token refresh retry logic
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const state = useUserStore.getState();

      if (state.refreshToken) {
        try {
          logError('API', 'Token expired, attempting refresh...', { status: 401 });

          // Thử làm mới token với retry logic
          const newTokenResponse = await refreshTokenWithRetry(state.refreshToken);

          if (newTokenResponse) {
            // Refresh thành công
            state.setAccessToken(newTokenResponse.access_token);
            logError('API', 'Token refreshed successfully');

            // Retry request gốc với token mới
            originalRequest.headers.Authorization = `Bearer ${newTokenResponse.access_token}`;
            return apiClient(originalRequest);
          } else {
            // Refresh thất bại - logout
            logError('API', 'Token refresh failed, logging out...');
            state.logout();
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
            return Promise.reject(new Error('Token refresh failed'));
          }
        } catch (refreshError) {
          logError('API', refreshError, { message: 'Token refresh error' });
          // Nếu refresh thất bại, logout
          state.logout();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available - redirect to login
        logError('API', 'No refresh token available, redirecting to login');
        useUserStore.getState().logout();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    }

    // Handle other errors with better logging
    const status = error.response?.status;
    const message = getErrorMessage(error);

    logError('API Error', {
      status,
      message,
      endpoint: originalRequest?.url,
      method: originalRequest?.method,
    });

    // Attach user-friendly message to error for component display
    error.userMessage = message;

    return Promise.reject(error);
  }
);

/**
 * Tạo đồ thị mới từ dữ liệu frontend (dùng cho chức năng vẽ đồ thị).
 * POST /api/v1/graphs
 */
export async function createGraph(
  name: string,
  nodes: any[],
  edges: any[]
): Promise<{ graph_id: number }> {
  try {
    const response = await apiClient.post<{ graph_id: number }>('/graphs', {
      name,
      nodes,
      edges,
    });
    
    if (!response.data?.graph_id) {
      throw new Error('Invalid response: missing graph_id');
    }
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      console.error('Failed to create graph:', message);
      throw new Error(`Graph creation failed: ${message}`);
    }
    throw error;
  }
}

/**
 * Khởi tạo phiên chạy thuật toán.
 * POST /api/v1/init
 */
export async function initSession(
  algorithm: string,
  graphId: number,
  startNode: string
): Promise<InitSessionResponse> {
  try {
    const response = await apiClient.post<InitSessionResponse>('/init', {
      graph_id: graphId,
      start_node: startNode,
      algorithm,
    });
    
    if (!response.data?.session_id) {
      throw new Error('Invalid response: missing session_id');
    }
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      console.error('Failed to initialize session:', message);
      throw new Error(`Session initialization failed: ${message}`);
    }
    throw error;
  }
}

/**
 * Lấy snapshot của một bước cụ thể.
 * GET /api/v1/step/{session_id}?step_index=...
 */
export async function getStep(
  sessionId: string,
  stepIndex: number
): Promise<StepResponse> {
  const { data } = await apiClient.get<StepResponse>(`/step/${sessionId}`, {
    params: { step_index: stepIndex },
  });
  return data;
}

/**
 * Lấy giải thích RAG cho một bước (non-streaming).
 * GET /api/v1/rag/explain/{session_id}?step_index=...
 */
export async function getRagExplanation(
  sessionId: string,
  stepIndex: number,
  question?: string
): Promise<RagExplanationResponse> {
  const params: Record<string, string | number> = { step_index: stepIndex };
  if (question) params.question = question;

  const { data } = await apiClient.get<RagExplanationResponse>(
    `/rag/explain/${sessionId}`,
    { params }
  );
  return data;
}

/**
 * Lấy giải thích RAG dạng SSE stream.
 * Trả về URL với token included (cho EventSource).
 * Note: EventSource không hỗ trợ custom headers, nên token được pass qua URL
 */
export function getRagExplanationStreamUrl(
  sessionId: string,
  stepIndex: number,
  question?: string
): string {
  const params = new URLSearchParams();
  params.set('step_index', String(stepIndex));
  if (question) params.set('question', question);

  const state = useUserStore.getState();
  if (state.accessToken) {
    params.set('token', state.accessToken);
  }

  return `${API_BASE}/rag/explain/${sessionId}/stream?${params.toString()}`;
}