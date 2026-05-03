import axios from 'axios';
import type { InitSessionResponse, StepResponse, RagExplanationResponse } from '@/types/snapshot';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

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
 * Trả về EventSource để frontend tự xử lý.
 */
export function getRagExplanationStreamUrl(
  sessionId: string,
  stepIndex: number,
  question?: string
): string {
  const params = new URLSearchParams();
  params.set('step_index', String(stepIndex));
  if (question) params.set('question', question);

  return `${API_BASE}/rag/explain/${sessionId}/stream?${params.toString()}`;
}