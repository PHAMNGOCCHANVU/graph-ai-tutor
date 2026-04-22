"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { Play, Pause, RotateCcw, SkipBack, SkipForward } from "lucide-react"; // Import các icon

export default function AlgorithmDetailPage() {
  const params = useParams();
  const slug = params.slug;
  
  // Thêm 2 state đơn giản để điều khiển giao diện
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-10">
      <header className="flex justify-between items-center mb-10 border-b border-slate-700 pb-5">
        <div>
          <h1 className="text-3xl font-bold uppercase tracking-wider">
            Thuật toán: <span className="text-pink-500">{slug}</span>
          </h1>
          <p className="text-slate-400 mt-2">Trình mô phỏng trực quan hóa lý thuyết đồ thị</p>
        </div>
        <button 
          onClick={() => window.history.back()} 
          className="bg-slate-700 hover:bg-slate-600 px-5 py-2 rounded-md transition-colors"
        >
          Quay lại
        </button>
      </header>

      {/* Vùng Canvas mô phỏng */}
      <div className="w-full h-[500px] bg-slate-800 rounded-xl border border-slate-700 flex flex-col items-center justify-center shadow-2xl">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-20 h-20 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-gray-400 italic">
            Đang tải không gian mô phỏng cho {slug?.toString().toUpperCase()}...
          </p>
        </div>
      </div>
      
      {/* Bảng điều khiển - Đã được làm mới để giống thanh player */}
      <div className="mt-8 p-4 bg-slate-800 rounded-lg border border-slate-700 flex items-center justify-between shadow-lg">
          
          {/* Cụm 1: Điều chỉnh tốc độ */}
          <div className="flex items-center gap-3 w-1/4">
            <input 
              type="range" 
              min="0.25" 
              max="2" 
              step="0.25" 
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="w-24 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer accent-pink-500" 
            />
            <span className="text-slate-400 text-sm font-mono">{speed}x</span>
          </div>

          {/* Cụm 2: Các nút điều khiển chính */}
          <div className="flex items-center gap-6">
            <button className="text-slate-400 hover:text-white transition-colors">
              <SkipBack size={20} />
            </button>

            <button 
              onClick={() => setIsPlaying(!isPlaying)}
              className="w-12 h-12 bg-pink-600 rounded-full flex items-center justify-center hover:bg-pink-500 transition-all transform active:scale-90 shadow-lg shadow-pink-900/20"
            >
              {isPlaying ? <Pause size={24} fill="currentColor" /> : <Play size={24} className="ml-1" fill="currentColor" />}
            </button>

            <button onClick={() => setIsPlaying(false)} className="text-slate-400 hover:text-white transition-colors">
              <RotateCcw size={20} />
            </button>

            <button className="text-slate-400 hover:text-white transition-colors">
              <SkipForward size={20} />
            </button>
          </div>

          {/* Cụm 3: Nút phụ/Thông tin */}
          <div className="w-1/4 flex justify-end">
             <button className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded text-xs font-bold uppercase tracking-widest transition-all">
                Thay đổi dữ liệu
             </button>
          </div>
      </div>
    </div>
  );
}