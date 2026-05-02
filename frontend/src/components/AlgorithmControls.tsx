"use client";
import { Play, Pause, SkipForward, SkipBack, RotateCcw } from "lucide-react";

interface ControlsProps {
  onPlay: () => void;
  onPause: () => void;
  onReset: () => void;
  onNext: () => void;
  onPrev: () => void;
  isPlaying: boolean;
  currentStep: number;
  totalSteps: number;
  onSpeedChange: (newSpeed: number) => void;
  speed: number;
}

export default function AlgorithmControls({
  onPlay, onPause, onReset, onNext, onPrev,
  isPlaying, currentStep, totalSteps,
  onSpeedChange, speed,
}: ControlsProps) {
  const progress = totalSteps > 0 ? ((currentStep + 1) / totalSteps) * 100 : 0;

  return (
    <div className="flex items-center gap-6 p-3 bg-slate-800 rounded-xl border border-slate-700 shadow-2xl w-full">
      
      {/* Tốc độ */}
      <div className="flex items-center gap-3 pl-2">
        <input 
          type="range" min="0.25" max="3" step="0.25" value={speed} 
          onChange={(e) => {
            const val = parseFloat(e.target.value);
            onSpeedChange(val);
          }}
          className="w-24 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer accent-pink-500"
        />
        <span className="text-slate-400 text-xs font-mono w-8">{speed}x</span>
      </div>

      {/* Điều khiển Play/Pause/Steps */}
      <div className="flex items-center gap-2 border-l border-slate-700 pl-6">
        <button
          onClick={onPrev}
          disabled={currentStep <= 0}
          className="p-2 text-slate-400 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <SkipBack size={18} />
        </button>

        <button 
          onClick={isPlaying ? onPause : onPlay}
          className={`p-3 rounded-full transition-all transform active:scale-90 shadow-lg ${
            isPlaying ? 'bg-pink-600 hover:bg-pink-500' : 'bg-green-600 hover:bg-green-500'
          }`}
        >
          {isPlaying ? <Pause size={20} fill="white" /> : <Play size={20} fill="white" className="ml-0.5" />}
        </button>

        <button onClick={onReset} className="p-2 text-slate-400 hover:text-white transition-colors">
          <RotateCcw size={18} />
        </button>

        <button
          onClick={onNext}
          disabled={currentStep >= totalSteps - 1}
          className="p-2 text-slate-400 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <SkipForward size={18} />
        </button>
      </div>

      {/* Thanh tiến trình mô phỏng */}
      <div className="flex-1 flex items-center gap-4 pl-6 border-l border-slate-700">
        <div className="flex-1 h-1 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-pink-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="text-slate-400 text-[10px] font-mono whitespace-nowrap">
          Bước {currentStep + 1}/{totalSteps}
        </div>
      </div>
    </div>
  );
}