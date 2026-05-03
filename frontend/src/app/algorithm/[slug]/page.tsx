"use client";
import { useParams } from "next/navigation";
import { useState, useRef, useEffect, useCallback } from "react";
import { PencilLine } from "lucide-react";
import AlgorithmControls from "@/components/AlgorithmControls";
import { DEFAULT_GRAPHS } from "@/constants/defaultGraphs";
import GraphCanvas from "@/components/GraphCanvas";
import RagChatBox from "@/components/RagChatBox";
import { useAlgorithmStore } from "@/store/algorithmStore";
import { createGraph } from "@/services/api";
import type { SnapshotState } from "@/types/snapshot";

interface GraphData {
  nodes: any[];
  edges: any[];
}

export default function AlgorithmDetailPage() {
  const params = useParams();
  const slug = params.slug as string;

  // Local state for graph editing
  const [currentData, setCurrentData] = useState<GraphData>({
    nodes: [],
    edges: [],
  });
  const [isEditMode, setIsEditMode] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  // Zustand store
  const {
    sessionId,
    totalSteps,
    currentStepIndex,
    steps,
    isPlaying,
    speed,
    isLoading,
    error,
    initSessionAction,
    nextStep,
    prevStep,
    togglePlay,
    setSpeed,
    reset,
  } = useAlgorithmStore();

  // Auto-play interval ref
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Hàm khởi tạo session với graph động
  const runAlgorithm = useCallback(async (data: GraphData) => {
    if (!slug) return;
    setIsRunning(true);
    try {
      // Bước 1: Tạo graph trên backend
      const { graph_id } = await createGraph(slug, data.nodes, data.edges);
      
      // Bước 2: Validate start_node tồn tại trong graph
      const nodeIds = data.nodes.map((n: any) => (typeof n === 'string' ? n : n.id));
      let startNode = "A";
      
      if (!nodeIds.includes("A")) {
        // Nếu "A" không tồn tại, sử dụng node đầu tiên
        startNode = nodeIds.length > 0 ? nodeIds[0] : "A";
        console.warn(`Node "A" không tồn tại. Sử dụng node "${startNode}" thay thế.`);
      }
      
      // Bước 3: Khởi tạo session với start_node hợp lệ
      await initSessionAction(slug, graph_id, startNode);
    } catch (err) {
      console.error("Failed to run algorithm:", err);
    } finally {
      setIsRunning(false);
    }
  }, [slug, initSessionAction]);

  // Khởi tạo session khi component mount
  useEffect(() => {
    if (slug) {
      const key = slug.toUpperCase();
      const data = DEFAULT_GRAPHS[key] || DEFAULT_GRAPHS["DFS"];
      setCurrentData(data);
      // Tự động chạy với graph mẫu
      runAlgorithm(data);
    }

    return () => {
      reset();
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  // Auto-play logic
  useEffect(() => {
    if (isPlaying) {
      const intervalMs = Math.max(200, Math.round(1000 / speed));
      intervalRef.current = setInterval(() => {
        nextStep();
      }, intervalMs);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, speed, nextStep]);

  // Lấy snapshot hiện tại từ cache
  const currentSnapshot = steps.find((s) => s.step_index === currentStepIndex);

  // Build SnapshotState từ backend response (bao gồm traversed_edges, final_path_edges)
  const snapshotState: SnapshotState | null = currentSnapshot
    ? {
        current_node: currentSnapshot.data.current_node,
        visited: currentSnapshot.data.visited,
        distances: currentSnapshot.data.distances,
        queue: currentSnapshot.data.queue.map((item: string) => {
          const parts = item.split(":");
          return parts.length > 1 ? parts[1] : item;
        }),
        traversed_edges: currentSnapshot.data.traversed_edges || [],
        final_path_edges: currentSnapshot.data.final_path_edges || [],
        action_description: currentSnapshot.description,
      }
    : null;

  const displayData = currentData;

  const handleClearGraph = () => {
    setCurrentData({ nodes: [], edges: [] });
    setIsEditMode(true);
  };

  const handleRunCustomGraph = () => {
    if (currentData.nodes.length > 0) {
      runAlgorithm(currentData);
      setIsEditMode(false);
    }
  };

  const handleReset = () => {
    if (slug) {
      const key = slug.toUpperCase();
      const data = DEFAULT_GRAPHS[key] || DEFAULT_GRAPHS["DFS"];
      setCurrentData(data);
      setIsEditMode(false);
      runAlgorithm(data);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6 flex flex-col gap-4">
      {/* Header */}
      <header className="flex justify-between items-center border-b border-slate-700 pb-4 shrink-0">
        <h1 className="text-2xl font-bold uppercase tracking-wider">
          Thuật toán: <span className="text-pink-500">{slug}</span>
        </h1>
        <div className="flex items-center gap-3">
          {sessionId && (
            <span className="text-[10px] text-slate-500 font-mono">
              ID: {sessionId.slice(0, 8)}...
            </span>
          )}
          <button
            onClick={() => window.history.back()}
            className="bg-slate-700 px-4 py-2 rounded-md text-sm hover:bg-slate-600 transition-colors"
          >
            Quay lại
          </button>
        </div>
      </header>

      {/* Error display */}
      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-2 rounded-lg text-xs shrink-0">
          {error}
        </div>
      )}

      {/* Main area */}
      <div className="flex-1 flex gap-4 min-h-0" style={{ height: 'calc(100vh - 220px)' }}>
        {/* LEFT: Graph workspace */}
        <div className="flex-[2] bg-slate-800 rounded-xl border border-slate-700 relative flex items-center justify-center overflow-hidden">
          <div className="text-slate-500 font-mono text-xs absolute top-4 left-4 z-10">
            {isEditMode ? 'EDIT_MODE' : `STEP_${currentStepIndex}`}
          </div>

          {(isLoading || isRunning) && !currentSnapshot ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-10 h-10 border-2 border-slate-600 border-t-pink-500 rounded-full animate-spin"></div>
              <p className="text-slate-400 italic font-light">Đang tải mô phỏng...</p>
            </div>
          ) : (
            <div className="w-full h-full">
              <GraphCanvas
                data={displayData}
                setData={setCurrentData}
                snapshotState={isEditMode ? null : snapshotState}
                readOnly={!isEditMode}
              />
            </div>
          )}

          {/* Edit mode toggle */}
          {!isEditMode ? (
            <button
              className="absolute bottom-4 left-4 z-50 flex items-center gap-2 bg-slate-900/90 hover:bg-pink-600 border border-slate-700 px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-2xl"
              onClick={handleClearGraph}
            >
              <PencilLine size={16} />
              VẼ ĐỒ THỊ
            </button>
          ) : (
            <button
              className="absolute bottom-4 left-4 z-50 flex items-center gap-2 bg-green-600 hover:bg-green-500 border border-green-700 px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-2xl"
              onClick={handleRunCustomGraph}
              disabled={isRunning || currentData.nodes.length === 0}
            >
              {isRunning ? 'ĐANG CHẠY...' : 'CHẠY THUẬT TOÁN'}
            </button>
          )}

          {/* RagChatBox floating buttons */}
          <RagChatBox
            sessionId={sessionId}
            stepIndex={currentStepIndex}
            description={currentSnapshot?.description}
          />
        </div>
      </div>

      {/* Controls */}
      <AlgorithmControls
        isPlaying={isPlaying}
        currentStep={currentStepIndex}
        totalSteps={totalSteps}
        speed={speed}
        onPlay={() => togglePlay()}
        onPause={() => togglePlay()}
        onReset={handleReset}
        onNext={() => nextStep()}
        onPrev={() => prevStep()}
        onSpeedChange={(s) => setSpeed(s)}
      />
    </div>
  );
}