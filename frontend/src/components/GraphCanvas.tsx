// src/components/GraphCanvas.tsx
"use client";
import React, { useMemo } from 'react';
import ReactFlow, { Background, MarkerType, BackgroundVariant, ConnectionMode, Controls, useNodesState, useEdgesState, addEdge, applyNodeChanges, applyEdgeChanges, } from 'reactflow';
import 'reactflow/dist/style.css';
import CircleNode from './CircleNode';
import { useCallback } from 'react';
import MultiBezierEdge from './MultiBezierEdge';

const edgeTypes = {
  multi: MultiBezierEdge,
};



const nodeTypes = { circle: CircleNode };

interface GraphCanvasProps {
  data: {
    nodes: any[];
    edges: any[];
  };
  setData: React.Dispatch<React.SetStateAction<any>>; // Thêm dòng này để nhận hàm cập nhật
}

const edges = [
  { 
    id: 'e1-2', 
    source: 'A', 
    target: 'B', 
    type: 'straight', 
    label: '27', 
    data: { offset: -30 } // Đẩy lên trên
  },
  { 
    id: 'e2-1', 
    source: 'B', 
    target: 'A', 
    type: 'straight', 
    label: '24', 
    data: { offset: 30 }  // Đẩy xuống dưới
  }
];

export default function GraphCanvas({ data, setData }: GraphCanvasProps) {
  // Cấu hình Marker định dạng VisuAlgo: Mũi tên to, sắc nét
  const arrowMarker = useMemo(() => ({
    type: MarkerType.ArrowClosed,
    color: '#64748b', // Slate-500
    width: 10,
    height: 10,
    // refX điều chỉnh để mũi tên chạm vừa khít viền tròn của Node (w-16)
    refX: 15, 
  }), []);

  const onNodesChange = useCallback((changes: any) => {
    setData((prev: any) => ({
      ...prev,
      nodes: applyNodeChanges(changes, prev.nodes),
    }));
  }, [setData]);

  const onEdgesChange = useCallback((changes: any) => {
    setData((prev: any) => ({
      ...prev,
      edges: applyEdgeChanges(changes, prev.edges),
    }));
  }, [setData]);

  const handleStartDrawing = () => {
  setData({ nodes: [], edges: [] });
};

  const onPaneClick = useCallback((event: React.MouseEvent) => {
    // Để lấy tọa độ chuẩn trong React Flow khi click, bạn nên dùng dự phòng hoặc helper
    // Tạm thời dùng logic của bạn nhưng fix label
    const id = Date.now().toString();
    const newNode = {
      id,
      type: 'circle', 
      position: { x: event.clientX - 400, y: event.clientY - 200 }, 
      data: { label: String.fromCharCode(65 + (data?.nodes?.length || 0)) },
    };
    
    setData((prev: any) => ({
      ...prev,
      nodes: [...prev.nodes, newNode]
    }));
  }, [data?.nodes?.length, setData]);
 
  const onConnect = useCallback((params: any) => {
  const sourceNode = data.nodes.find(n => n.id === params.source);
  const targetNode = data.nodes.find(n => n.id === params.target);
  
  let distance = 0;
  if (sourceNode && targetNode) {
    const dx = targetNode.position.x - sourceNode.position.x;
    const dy = targetNode.position.y - sourceNode.position.y;
    // Tính khoảng cách Euclidean
    distance = Math.round(Math.sqrt(dx * dx + dy * dy) / 10); 
  }

  const newEdge = { 
    ...params, 
    type: 'multi', 
    data: { weight: distance }, // Lưu vào object data
    markerEnd: arrowMarker,
    style: { stroke: '#64748b', strokeWidth: 3 }
  };
  
  setData((prev: any) => ({
    ...prev,
    edges: addEdge(newEdge, prev.edges)
  }));
}, [data.nodes, setData, arrowMarker]); // Đã thêm data.nodes vào đây


  // 1. Chuẩn hóa Nodes
 const formattedNodes = useMemo(() => 
    data?.nodes.map((n: any) => ({ ...n, type: 'circle' })), [data?.nodes]);

  // 2. Logic gán Handle thông minh để tạo đường song song
 const formattedEdges = useMemo(() => 
  data?.edges.map((e: any) => {
    const sourceNode = data.nodes.find((n: any) => n.id === e.source);
    const targetNode = data.nodes.find((n: any) => n.id === e.target);
    // LẤY GIÁ TRỊ TỪ data.weight
    const weight = e.data?.weight ?? ""; 

   const hasReverseEdge = data.edges.some(
      (edge: any) => edge.source === e.target && edge.target === e.source
    );

    let offset = 0;
    if (hasReverseEdge) {
      // Quy ước: Cạnh đi từ đỉnh có ID nhỏ sang ID lớn uốn lên trên (offset âm)
      // Cạnh đi từ đỉnh có ID lớn về ID nhỏ uốn xuống dưới (offset dương)
      // Điều này đảm bảo nhãn của A->B và B->A không bao giờ đè lên nhau
      offset = e.source.localeCompare(e.target) < 0 ? -12 : 12;
    }

    // Logic tính Handle thông minh của bạn giữ nguyên...
    let sourceHandle = 's-right';
    let targetHandle = 't-left';
    if (sourceNode && targetNode) {
       const dx = targetNode.position.x - sourceNode.position.x;
       const dy = targetNode.position.y - sourceNode.position.y;
       if (Math.abs(dy) > Math.abs(dx)) {
         sourceHandle = dy > 0 ? 's-bottom' : 's-top';
         targetHandle = dy > 0 ? 't-top' : 't-bottom';
       } else {
         sourceHandle = dx > 0 ? 's-right' : 's-left';
         targetHandle = dx > 0 ? 't-left' : 't-right';
       }
    }

    return {
      ...e,
      type: 'straight',
      data: { ...e.data, offset },
      sourceHandle,
      targetHandle,
      label: weight.toString(), 
      style: { 
        stroke: e.animated ? '#db2777' : '#64748b', 
        strokeWidth: 3,
        transition: 'stroke 0.3s'
      },
    };
  }), [data?.edges, data?.nodes, arrowMarker]);

  // Trong GraphCanvas.tsx

const onNodeClick = useCallback((_: any, node: any) => {
  const newLabel = prompt("Nhập tên đỉnh mới:", node.data.label);
  if (newLabel !== null) {
    setData((prev: any) => ({
      ...prev,
      nodes: prev.nodes.map((n: any) => 
        n.id === node.id ? { ...n, data: { ...n.data, label: newLabel } } : n
      ),
    }));
  }
}, [setData]);

const onEdgeClick = useCallback((_: any, edge: any) => {
  const newWeight = prompt("Nhập trọng số mới:", edge.data?.weight);
  if (newWeight !== null) {
    setData((prev: any) => ({
      ...prev,
      edges: prev.edges.map((e: any) => 
        e.id === edge.id ? { ...e, data: { ...e.data, weight: Number(newWeight) } } : e
      ),
    }));
  }
}, [setData]);


  return (
    <div className="w-full h-full bg-[#0f172a]"> {/* Màu nền tối sâu hơn (Slate-900) */}
      <ReactFlow
        nodes={formattedNodes}
        edges={formattedEdges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onPaneClick={onPaneClick} 
        selectNodesOnDrag={true} 
        connectOnClick={true}// Cho phép click để thêm node
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        
        
        // ConnectionMode.Loose cho phép nối source-to-source hoặc target-to-target nếu cần
        connectionMode={ConnectionMode.Loose}
        defaultEdgeOptions={{
          type: 'straight',
          labelStyle: { 
            fill: '#f1f5f9', 
            fontWeight: 400, 
            fontSize: 12,
            fontFamily: 'Inter, sans-serif'
          },
          labelBgStyle: { 
            fill: '#0f172a', 
            fillOpacity: 0,
            
          },
          labelBgPadding: [4, 4],
          markerEnd: arrowMarker,
        }}
        fitView
        minZoom={0.5}
        maxZoom={2}
        >
        <Controls position="bottom-right" />
        <Background color="#333" variant={BackgroundVariant.Dots} />
      
        <Background 
          variant={BackgroundVariant.Dots} 
          color="#334155" 
          gap={30} 
          size={1.5} 
        />
      </ReactFlow>
    </div>
  );
}