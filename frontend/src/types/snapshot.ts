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
  visited?: string[];
  queue?: string[];
  distances?: Record<string, number>;
  notes?: string;
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
