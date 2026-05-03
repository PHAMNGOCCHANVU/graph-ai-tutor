export interface GraphNode {
  id: string;
  label?: string;
  [key: string]: unknown;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight?: number;
  [key: string]: unknown;
}

export interface SnapshotState {
  current_node?: string | null;
  current_edge?: string | null;
  visited?: string[];
  queue?: string[];
  distances?: Record<string, number>;
  traversed_edges?: string[];    // Các cạnh đã đi qua (tô màu xanh dương)
  final_path_edges?: string[];   // Kết quả cuối (MST / đường đi ngắn nhất) — tô màu xanh lá
  mst_edges?: string[];
  selected_edges?: string[];
  notes?: string;
  action_description?: string;
  [key: string]: unknown;
}

export interface AlgorithmSnapshot {
  step_id: number;
  algorithm: string;
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
    [key: string]: unknown;
  };
  state: SnapshotState;
  meta?: Record<string, unknown>;
}

/**
 * Response thực tế từ backend GET /api/v1/step/{session_id}
 * Backend trả về step_data_json dạng flat, không có graph
 */
export interface StepResponse {
  session_id: string;
  step_index: number;
  description: string;
  data: {
    phase_id: string;
    current_node: string | null;
    target_node: string | null;
    visited: string[];
    distances: Record<string, number>;
    queue: string[];
  };
}

export interface InitSessionResponse {
  session_id: string;
  total_steps: number;
  algorithm: string;
}

export interface RagExplanationResponse {
  explanation: string;
  session_id: string;
  step_index: number;
}