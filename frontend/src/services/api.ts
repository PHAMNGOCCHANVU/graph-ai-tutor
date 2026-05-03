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
  const { data } = await apiClient.post<{ graph_id: number }>('/graphs', {
    name,
    nodes,
    edges,
  });
  return data;
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
  const { data } = await apiClient.post<InitSessionResponse>('/init', {
    graph_id: graphId,
    start_node: startNode,
    algorithm,
  });
  return data;
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