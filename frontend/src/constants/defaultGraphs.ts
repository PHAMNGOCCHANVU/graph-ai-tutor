/**
 * Hàm tiện ích để tự động gán Handle nhằm tạo hiệu ứng đường song song.
 * Logic:
 * - Nếu source ID < target ID: Cạnh "đi" (Forward) -> Dùng các Handle phía trên/phải (s-top, t-top hoặc s-right, t-right).
 * - Nếu source ID > target ID: Cạnh "về" (Backward) -> Dùng các Handle phía dưới/trái (s-bottom, t-bottom hoặc s-left, t-left).
 */
const formatEdge = (id: string, source: string, target: string, label: string) => {
  const isForward = source < target;
  
  return {
    id,
    source,
    target,
    label,
    // Gán handle dựa trên chiều của ID để tránh chồng lấp
    sourceHandle: isForward ? 's-top' : 's-bottom',
    targetHandle: isForward ? 't-top' : 't-bottom',
    // Thêm định dạng label để đồng bộ với VisuAlgo
    data: { label }, 
  };
};

export const DEFAULT_GRAPHS: Record<string, any> = {
  DFS: {
    nodes: [
      { id: "A", position: { x: 100, y: 150 }, data: { label: "A" }, type: 'circle' },
      { id: "B", position: { x: 300, y: 50 }, data: { label: "B" }, type: 'circle' },
      { id: "C", position: { x: 300, y: 250 }, data: { label: "C" }, type: 'circle' },
      { id: "D", position: { x: 500, y: 150 }, data: { label: "D" }, type: 'circle' },
    ],
    edges: [
      // Với DFS, chúng ta dùng formatEdge để đảm bảo nếu sau này bạn thêm cạnh ngược, nó sẽ không đè nhau
      formatEdge("eA-B", "A", "B", "5"),
      formatEdge("eA-C", "A", "C", "2"),
      formatEdge("eB-D", "B", "D", "4"),
      formatEdge("eC-D", "C", "D", "7"),
    ],
  },
  
  BFS: {
    nodes: [
      { id: "0", position: { x: 300, y: 50 }, data: { label: "0" }, type: 'circle' },
      { id: "1", position: { x: 480, y: 150 }, data: { label: "1" }, type: 'circle' },
      { id: "2", position: { x: 480, y: 350 }, data: { label: "2" }, type: 'circle' },
      { id: "3", position: { x: 300, y: 250 }, data: { label: "3" }, type: 'circle' },
      { id: "4", position: { x: 120, y: 350 }, data: { label: "4" }, type: 'circle' },
      { id: "5", position: { x: 120, y: 150 }, data: { label: "5" }, type: 'circle' },
    ],
    edges: [
      formatEdge("e0-5", "0", "5", "4"), 
      formatEdge("e0-1", "0", "1", "2"), 
      formatEdge("e1-3", "1", "3", "9"), 
      formatEdge("e3-4", "3", "4", "1"), 
      formatEdge("e3-2", "3", "2", "5"), 
    ],
  },

  DIJKSTRA: {
    nodes: [
      { id: "1", position: { x: 50, y: 150 }, data: { label: "1" }, type: 'circle' },
      { id: "2", position: { x: 250, y: 50 }, data: { label: "2" }, type: 'circle' },
      { id: "3", position: { x: 250, y: 250 }, data: { label: "3" }, type: 'circle' },
      { id: "4", position: { x: 500, y: 150 }, data: { label: "4" }, type: 'circle' },
    ],
    edges: [
      formatEdge("e1-2", "1", "2", "10"),
      formatEdge("e1-3", "1", "3", "5"),
      formatEdge("e2-4", "2", "4", "1"),
      formatEdge("e3-4", "3", "4", "8"),
      formatEdge("e3-2", "3", "2", "3"),
    ],
  },

  PRIM: {
    nodes: [
      { id: "A", position: { x: 300, y: 50 }, data: { label: "A" }, type: 'circle' },
      { id: "B", position: { x: 100, y: 150 }, data: { label: "B" }, type: 'circle' },
      { id: "C", position: { x: 500, y: 150 }, data: { label: "C" }, type: 'circle' },
      { id: "D", position: { x: 150, y: 350 }, data: { label: "D" }, type: 'circle' },
      { id: "E", position: { x: 450, y: 350 }, data: { label: "E" }, type: 'circle' },
    ],
    edges: [
      formatEdge("eB-A", "B", "A", "2"),
      formatEdge("eA-C", "A", "C", "3"), 
      formatEdge("eC-B", "C", "B", "5"),
      formatEdge("eB-D", "B", "D", "1"), 
      formatEdge("eE-C", "E", "C", "4"),
      formatEdge("eD-E", "D", "E", "8"), 
    ],
  },

  KRUSKAL: {
    nodes: [
      { id: "0", position: { x: 50, y: 200 }, data: { label: "0" }, type: 'circle' },
      { id: "1", position: { x: 200, y: 50 }, data: { label: "1" }, type: 'circle' },
      { id: "2", position: { x: 200, y: 350 }, data: { label: "2" }, type: 'circle' },
      { id: "3", position: { x: 450, y: 50 }, data: { label: "3" }, type: 'circle' },
      { id: "4", position: { x: 450, y: 350 }, data: { label: "4" }, type: 'circle' },
      { id: "5", position: { x: 600, y: 200 }, data: { label: "5" }, type: 'circle' },
    ],
    edges: [
      formatEdge("e0-1", "0", "1", "4"),
      formatEdge("e0-2", "0", "2", "2"),
      formatEdge("e1-2", "1", "2", "5"),
      formatEdge("e1-3", "1", "3", "10"),
      formatEdge("e2-4", "2", "4", "3"),
      formatEdge("e3-4", "3", "4", "4"),
      formatEdge("e3-5", "3", "5", "11"),
      formatEdge("e4-5", "4", "5", "7"), 
    ],
  }
};