"use client";
import { useParams } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { Send, PencilLine, Sparkles } from "lucide-react"; 
import AlgorithmControls from "@/components/AlgorithmControls";
import { DEFAULT_GRAPHS } from "@/constants/defaultGraphs"; // Sửa lại import
import GraphCanvas from "@/components/GraphCanvas"; // Thêm dòng này

interface GraphData {
  nodes: any[];
  edges: any[];
}
// Sử dụng <GraphData> để chỉ định kiểu cho state


export default function AlgorithmDetailPage() {
  const params = useParams();
  const slug = params.slug;
  const [isPlaying, setIsPlaying] = useState(false);
  const [graphData, setGraphData] = useState(null);
  const [currentData, setCurrentData] = useState<GraphData>({ 
  nodes: [], 
  edges: [] 
});

const handleClearGraph = () => {
    setCurrentData({ nodes: [], edges: [] });
  };


  // 2. THÊM EFFECT ĐỂ CẬP NHẬT DỮ LIỆU THEO SLUG TẠI ĐÂY
  useEffect(() => {
    if (slug) {
      const key = slug.toString().toUpperCase();
      const data = DEFAULT_GRAPHS[slug.toString().toUpperCase()] || DEFAULT_GRAPHS["DFS"];
      setCurrentData(data); // Mặc định là DFS nếu không tìm thấy
      setGraphData(data);
      console.log("Đang tải dữ liệu cho thuật toán:", slug);
    }
  }, [slug]);

   

  // Quản lý danh sách tin nhắn trong chat
  const [messages, setMessages] = useState([
    { role: "system", content: `Chào bạn! Tôi là AI Tutor. Nhấn nút "Vẽ đồ thị" để tùy chỉnh hoặc nhấn "Play" để xem thuật toán ${slug} hoạt động.` }
  ]);
  
  const chatEndRef = useRef<HTMLDivElement>(null);
  

  // Tự động cuộn xuống khi có tin nhắn mới
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Hàm xử lý khi nhấn "Giải thích bước hiện tại"
  const handleExplainStep = () => {
    const stepInfo = "Hiện tại thuật toán đang kiểm tra các đỉnh kề của nút gốc. Đây là bước quan trọng để xác định lộ trình tiếp theo trong đồ thị.";
    
    setMessages(prev => [
      ...prev, 
      { role: "user", content: "Giải thích bước này cho tôi." },
      { role: "ai", content: stepInfo }
    ]);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6 flex flex-col gap-4">
      {/* Header */}
      <header className="flex justify-between items-center border-b border-slate-700 pb-4">
        <h1 className="text-2xl font-bold uppercase tracking-wider">
          Thuật toán: <span className="text-pink-500">{slug}</span>
        </h1>
        <button onClick={() => window.history.back()} className="bg-slate-700 px-4 py-2 rounded-md text-sm hover:bg-slate-600 transition-colors">
          Quay lại
        </button>
      </header>

      {/* KHU VỰC CHÍNH */}
      <div className="flex-1 flex gap-4 min-h-[500px]">
        
        {/* BÊN TRÁI: KHÔNG GIAN ĐỒ THỊ */}
        <div className="flex-[2] bg-slate-800 rounded-xl border border-slate-700 relative flex items-center justify-center overflow-hidden">
          <div className="text-slate-500 font-mono text-xs absolute top-4 left-4">GRAPH_WORKSPACE</div>
          {/* HIỂN THỊ GRAPH CANVAS THẬT */}
          {/* Truyền currentData thay vì graphData */}
          {currentData.nodes.length >= 0 ? (
            <div className="w-full h-full">
               <GraphCanvas data={currentData} setData={setCurrentData} />
            </div>
          ) : (
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-2 border-slate-600 border-t-pink-500 rounded-full animate-spin"></div>
          <p className="text-slate-400 italic font-light">Đang tải mô phỏng...</p>
        </div>
      )}

          <button className="absolute bottom-4 left-4 z-50 flex items-center gap-2 bg-slate-900/90 hover:bg-pink-600 border border-slate-700 px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-2xl group"
           onClick={handleClearGraph} // Gắn hàm xóa vào đây
            >
          
            <PencilLine size={16} />
            VẼ ĐỒ THỊ
          </button>
        </div>

        {/* BÊN PHẢI: KHUNG CHAT AI TUTOR */}
        <div className="flex-1 bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden shadow-2xl">
          <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-pink-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-bold tracking-tight uppercase">AI Tutor</span>
            </div>
          </div>

          {/* Vùng hiển thị nội dung chat */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-slate-700">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] p-3 rounded-2xl text-xs leading-relaxed shadow-sm ${
                  msg.role === "user" 
                    ? "bg-pink-600 text-white rounded-tr-none" 
                    : "bg-slate-700/50 border border-slate-600 text-slate-200 rounded-tl-none"
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Footer Chat: Nút hỗ trợ nhanh & Ô nhập liệu */}
          <div className="p-4 bg-slate-900/50 border-t border-slate-700 space-y-3">
            
            {/* Nút Giải thích nhanh */}
            <button 
              onClick={handleExplainStep}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-[10px] font-bold text-pink-400 flex items-center justify-center gap-2 transition-all active:scale-95"
            >
              <Sparkles size={14} />
              GIẢI THÍCH BƯỚC HIỆN TẠI
            </button>

            <div className="relative">
              <input 
                type="text" 
                placeholder="Nhập câu hỏi..." 
                className="w-full bg-slate-800 border border-slate-600 rounded-full px-4 py-2 text-xs outline-none focus:border-pink-500 transition-colors pr-10"
              />
              <button className="absolute right-3 top-2 text-slate-500 hover:text-pink-400 transition-colors">
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* THANH ĐIỀU KHIỂN */}
      <AlgorithmControls 
        isPlaying={isPlaying}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onReset={() => {
            setIsPlaying(false);
            setMessages([{ role: "system", content: "Đã đặt lại mô phỏng. Sẵn sàng bắt đầu lại!" }]);
        }}
        onSpeedChange={(s) => console.log(s)}
      />
    </div>
  );
}