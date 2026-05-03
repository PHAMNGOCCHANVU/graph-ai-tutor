import { create } from 'zustand';
import type { InitSessionResponse, StepResponse } from '@/types/snapshot';
import { initSession, getStep } from '@/services/api';

interface StepData {
  step_index: number;
  description: string;
  data: {
    phase_id: string;
    current_node: string | null;
    target_node: string | null;
    visited: string[];
    distances: Record<string, number>;
    queue: string[];
    traversed_edges?: string[];
    final_path_edges?: string[];
  };
}

interface AlgorithmState {
  // Session info
  sessionId: string | null;
  algorithm: string | null;
  totalSteps: number;
  currentStepIndex: number;

  // Data cache: lưu raw StepResponse từ backend
  steps: StepData[];

  // UI state
  isPlaying: boolean;
  isLoadingStep: boolean; // Đang fetch step (chờ trước khi next)
  speed: number;
  isLoading: boolean;
  error: string | null;

  // Actions
  initSessionAction: (algorithm: string, graphId: number, startNode: string) => Promise<void>;
  fetchStep: (stepIndex: number) => Promise<void>;
  goToStep: (index: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  togglePlay: () => void;
  setSpeed: (speed: number) => void;
  reset: () => void;
}

export const useAlgorithmStore = create<AlgorithmState>((set, get) => ({
  // Initial state
  sessionId: null,
  algorithm: null,
  totalSteps: 0,
  currentStepIndex: 0,
  steps: [],
  isPlaying: false,
  isLoadingStep: false,
  speed: 1,
  isLoading: false,
  error: null,

  initSessionAction: async (algorithm: string, graphId: number, startNode: string) => {
    set({ isLoading: true, error: null });
    try {
      const result: InitSessionResponse = await initSession(algorithm, graphId, startNode);
      set({
        sessionId: result.session_id,
        algorithm: result.algorithm,
        totalSteps: result.total_steps,
        currentStepIndex: 0,
        steps: [],
        isPlaying: false,
        isLoading: false,
        error: null,
      });

      // Fetch step 0 immediately after init
      await get().fetchStep(0);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Không thể khởi tạo phiên thuật toán';
      set({ isLoading: false, error: message });
    }
  },

  fetchStep: async (stepIndex: number) => {
    const { sessionId, steps } = get();
    if (!sessionId) return;

    // Nếu step đã có trong cache, không fetch lại
    if (steps.some((s) => s.step_index === stepIndex)) return;

    set({ isLoading: true, isLoadingStep: true, error: null });
    try {
      const response: StepResponse = await getStep(sessionId, stepIndex);
      const stepData: StepData = {
        step_index: response.step_index,
        description: response.description,
        data: response.data,
      };
      set((state) => ({
        steps: [...state.steps, stepData],
        isLoading: false,
        isLoadingStep: false,
      }));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Không thể lấy dữ liệu bước';
      set({ isLoading: false, isLoadingStep: false, error: message });
    }
  },

  goToStep: (index: number) => {
    const { totalSteps, fetchStep } = get();
    if (index < 0 || index >= totalSteps) return;

    set({ currentStepIndex: index });

    // Fetch step nếu chưa có trong cache (lazy loading)
    fetchStep(index);
  },

  nextStep: () => {
    const { currentStepIndex, totalSteps, goToStep, isLoadingStep } = get();
    // Không next nếu đang fetch step
    if (isLoadingStep) return;
    if (currentStepIndex < totalSteps - 1) {
      goToStep(currentStepIndex + 1);
    } else {
      // Đã đến bước cuối, dừng auto-play
      set({ isPlaying: false });
    }
  },

  prevStep: () => {
    const { currentStepIndex, goToStep, isLoadingStep } = get();
    if (isLoadingStep) return;
    if (currentStepIndex > 0) {
      goToStep(currentStepIndex - 1);
    }
  },

  togglePlay: () => {
    const { isPlaying, currentStepIndex, totalSteps } = get();
    if (currentStepIndex >= totalSteps - 1) {
      // Nếu đang ở cuối, reset về đầu khi play
      set({ currentStepIndex: 0, isPlaying: true });
    } else {
      set({ isPlaying: !isPlaying });
    }
  },

  setSpeed: (speed: number) => {
    set({ speed });
  },

  reset: () => {
    set({
      sessionId: null,
      algorithm: null,
      totalSteps: 0,
      currentStepIndex: 0,
      steps: [],
      isPlaying: false,
      isLoadingStep: false,
      speed: 1,
      isLoading: false,
      error: null,
    });
  },
}));