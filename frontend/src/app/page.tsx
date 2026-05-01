// src/app/page.tsx
import AlgorithmCard from "../components/AlgorithmCard";
//<AlgorithmCard id="dfs" title="DFS" bgColor="bg-green-500" imageUrl="/window.svg" />

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-900 p-10">
      {/* Header mô phỏng VisuAlgo */}
      <header className="text-center mb-16">
        <h1 className="text-5xl font-extrabold tracking-[0.2em] text-white">
          VISUAL<span className="text-pink-500 font-light">ALGORITHM</span>
        </h1>
        <p className="text-slate-400 italic mt-4 text-lg">
          Trực quan hóa thuật toán lý thuyết đồ thị
        </p>
      </header>

      <div className="flex justify-center mb-12">
  <div className="relative w-full max-w-md">
    <input 
      type="text" 
      placeholder="Tìm kiếm thuật toán..." 
      className="w-full px-5 py-3 rounded-full border border-slate-700 bg-slate-800 text-white focus:outline-none focus:ring-2 focus:ring-pink-400 shadow-inner placeholder:text-slate-500"
    />
    <div className="absolute right-4 top-3 text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
    </div>
  </div>
</div>

      {/* Grid chứa các thẻ thuật toán */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
        <AlgorithmCard
          id="dfs"
          title="DFS" 
          bgColor="bg-sorting" // Màu này bạn đã định nghĩa ở Bước 1
          imageUrl="/DFS.svg" 
        />
        <AlgorithmCard
          id="bfs" 
          title="BFS" 
          bgColor="bg-list" 
          imageUrl="/BFS.svg" 
        />
        <AlgorithmCard
          id="dijkstra" 
          title="Dijkstra" 
          bgColor="bg-graph" 
          imageUrl="/Dijkstra.svg" 
        />
        <AlgorithmCard 
          id="prim"
          title="Prim" 
          bgColor="bg-cyan-500" 
          imageUrl="/Prim.svg" 
        />
        <AlgorithmCard
          id="kruskal" 
          title="Kruskal" 
          bgColor="bg-tree" 
          imageUrl="/Kruskal.svg" 
        />
      </div>
    </main>
  );
}