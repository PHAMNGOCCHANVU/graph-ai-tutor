"use client";
import { useParams } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { PencilLine } from "lucide-react";
import AlgorithmControls from "@/components/AlgorithmControls";
import { DEFAULT_GRAPHS } from "@/constants/defaultGraphs";
import GraphCanvas from "@/components/GraphCanvas";
import RagChatBox from "@/components/RagChatBox";
import { useAlgorithmStore } from "@/store/algorithmStore";
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

  // Khởi tạo session khi component mount
  useEffect(() => {
    if (slug) {
      // Load default graph data for editing & display
      const key = slug.toUpperCase();
      const data = DEFAULT_GRAPHS[key] || DEFAULT_GRAPHS["DFS"];
      setCurrentData(data);

      // Khởi tạo session với backend (graph_id = 1 tạm thời, start_node = "A")
      initSessionAction(slug, 1, "A");
    }

    // Cleanup khi unmount
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

  // Build SnapshotState từ backend response
  const snapshotState: SnapshotState | null = currentSnapshot
    ? {
        current_node: currentSnapshot.data.current_node,
        visited: currentSnapshot.data.visited,
        distances: currentSnapshot.data.distances,
        // Parse queue từ format "dist:node" thành array node IDs
        queue: currentSnapshot.data.queue.map((item: string) => {
          const parts = item.split(":");
          return parts.length > 1 ? parts[1] : item;
        }),
        action_description: currentSnapshot.description,
      }
    : null;

  // Dùng DEFAULT_GRAPHS để hiển thị đồ thị (backend không trả về graph data trong step)
  const displayData = currentData;

  const handleClearGraph = () => {
    setCurrentData({ nodes: [], edges: [] });
    setIsEditMode(true);
  };

  const handleReset = () => {
    if (slug) {
      const key = slug.toUpperCase();
      const data = DEFAULT_GRAPHS[key] || DEFAULT_GRAPHS["DFS"];
      setCurrentData(data);
      setIsEditMode(false);
      initSessionAction(slug, 1, "A");
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6 flex flex-col gap-4">
      {/* Header */}
      <header className="flex justify-between items-center border-b border-slate-700 pb-4">
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
        <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-2 rounded-lg text-xs">
          {error}
        </div>
      )}

      {/* Main area */}
      <div className="flex-1 flex gap-4 min-h-[500px]">
        {/* LEFT: Graph workspace */}
        <div className="flex-[2] bg-slate-800 rounded-xl border border-slate-700 relative flex items-center justify-center overflow-hidden">
          <div className="text-slate-500 font-mono text-xs absolute top-4 left-4 z-10">
            {isEditMode ? 'EDIT_MODE' : `STEP_${currentStepIndex}`}
          </div>

          {isLoading && !currentSnapshot ? (
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
          <button
            className="absolute bottom-4 left-4 z-50 flex items-center gap-2 bg-slate-900/90 hover:bg-pink-600 border border-slate-700 px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-2xl"
            onClick={handleClearGraph}
          >
            <PencilLine size={16} />
            {isEditMode ? 'ĐANG VẼ' : 'VẼ ĐỒ THỊ'}
          </button>
        </div>

        {/* RIGHT: AI Tutor Chat */}
        <RagChatBox sessionId={sessionId} stepIndex={currentStepIndex} />
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