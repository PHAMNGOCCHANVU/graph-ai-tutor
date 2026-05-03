// src/components/GraphCanvas.tsx
"use client";
import React, { useMemo, useCallback } from 'react';
import ReactFlow, { Background, MarkerType, BackgroundVariant, ConnectionMode, Controls, useNodesState, useEdgesState, addEdge, applyNodeChanges, applyEdgeChanges, } from 'reactflow';
import 'reactflow/dist/style.css';
import CircleNode from './CircleNode';
import MultiBezierEdge from './MultiBezierEdge';
import type { SnapshotState } from '@/types/snapshot';

const edgeTypes = {
  multi: MultiBezierEdge,
};

const nodeTypes = { circle: CircleNode };

interface GraphCanvasProps {
  data: {
    nodes: any[];
    edges: any[];
  };
  setData: React.Dispatch<React.SetStateAction<any>>;
  snapshotState?: SnapshotState | null;
  readOnly?: boolean;
}

export default function GraphCanvas({ data, setData, snapshotState, readOnly = false }: GraphCanvasProps) {
  // Cấu hình Marker định dạng VisuAlgo: Mũi tên to, sắc nét
  const arrowMarker = useMemo(() => ({
    type: MarkerType.ArrowClosed,
    color: '#64748b',
    width: 10,
    height: 10,
    refX: 15,
  }), []);

  const onNodesChange = useCallback((changes: any) => {
    if (readOnly) return;
    setData((prev: any) => ({
      ...prev,
      nodes: applyNodeChanges(changes, prev.nodes),
    }));
  }, [setData, readOnly]);

  const onEdgesChange = useCallback((changes: any) => {
    if (readOnly) return;
    setData((prev: any) => ({
      ...prev,
      edges: applyEdgeChanges(changes, prev.edges),
    }));
  }, [setData, readOnly]);

  const onPaneClick = useCallback((event: React.MouseEvent) => {
    if (readOnly) return;
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
  }, [data?.nodes?.length, setData, readOnly]);

  const onConnect = useCallback((params: any) => {
    if (readOnly) return;
    const sourceNode = data.nodes.find(n => n.id === params.source);
    const targetNode = data.nodes.find(n => n.id === params.target);
    
    let distance = 0;
    if (sourceNode && targetNode) {
      const dx = targetNode.position.x - sourceNode.position.x;
      const dy = targetNode.position.y - sourceNode.position.y;
      distance = Math.round(Math.sqrt(dx * dx + dy * dy) / 10); 
    }

    const newEdge = { 
      ...params, 
      type: 'multi', 
      data: { weight: distance },
      markerEnd: arrowMarker,
      style: { stroke: '#64748b', strokeWidth: 3 }
    };
    
    setData((prev: any) => ({
      ...prev,
      edges: addEdge(newEdge, prev.edges)
    }));
  }, [data.nodes, setData, arrowMarker, readOnly]);

  // Áp dụng trạng thái snapshot vào nodes
  const enhancedNodes = useMemo(() => {
    if (!data?.nodes) return [] as any[];
    
    return data.nodes.map((n: any) => {
      const nodeState: any = {
        ...n,
        type: 'circle',
        data: { ...n.data },
      };

      if (snapshotState) {
        // Active node (current_node)
        nodeState.data.active = snapshotState.current_node === n.id;
        
        // Visited nodes
        nodeState.data.visited = snapshotState.visited?.includes(n.id) ?? false;
        
        // Queued nodes
        nodeState.data.queued = snapshotState.queue?.includes(n.id) ?? false;
        
        // Distance label
        if (snapshotState.distances && snapshotState.distances[n.id] !== undefined) {
          nodeState.data.distance = snapshotState.distances[n.id];
        }
      }

      return nodeState;
    });
  }, [data?.nodes, snapshotState]);

  // Áp dụng trạng thái snapshot vào edges
  const enhancedEdges = useMemo(() => {
    if (!data?.edges) return [];

    return data.edges.map((e: any) => {
      const sourceNode = data.nodes.find((n: any) => n.id === e.source);
      const targetNode = data.nodes.find((n: any) => n.id === e.target);
      const weight = e.data?.weight ?? "";

      const hasReverseEdge = data.edges.some(
        (edge: any) => edge.source === e.target && edge.target === e.source
      );

      let offset = 0;
      if (hasReverseEdge) {
        offset = e.source.localeCompare(e.target) < 0 ? -12 : 12;
      }

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

      // Xác định màu edge dựa trên snapshot (chuẩn hóa)
      let edgeColor = '#64748b';
      let animated = false;

      if (snapshotState) {
        // Tạo edge ID theo format "source-target" để so sánh với backend
        const edgeId = `${e.source}-${e.target}`;
        const reverseEdgeId = `${e.target}-${e.source}`;

        // Ưu tiên 1: final_path_edges (kết quả cuối) — màu xanh lá
        if (snapshotState.final_path_edges?.includes(edgeId) || 
            snapshotState.final_path_edges?.includes(reverseEdgeId)) {
          edgeColor = '#22c55e';
          animated = false;
        }
        // Ưu tiên 2: traversed_edges (cạnh đã đi qua) — màu xanh dương
        else if (snapshotState.traversed_edges?.includes(edgeId) || 
                 snapshotState.traversed_edges?.includes(reverseEdgeId)) {
          edgeColor = '#3b82f6';
          animated = true;
        }
        // Ưu tiên 3: Edge từ current_node — màu hồng
        else if (snapshotState.current_node && 
            (e.source === snapshotState.current_node || e.target === snapshotState.current_node)) {
          edgeColor = '#db2777';
          animated = true;
        }
        // Ưu tiên 4: selected_edges — màu vàng
        else if (snapshotState.selected_edges?.includes(e.id)) {
          edgeColor = '#f59e0b';
          animated = true;
        }
      }

      return {
        ...e,
        type: 'straight',
        data: { ...e.data, offset },
        sourceHandle,
        targetHandle,
        label: weight.toString(),
        animated,
        style: { 
          stroke: edgeColor, 
          strokeWidth: animated ? 4 : 3,
          transition: 'stroke 0.3s',
        },
      };
    });
  }, [data?.edges, data?.nodes, arrowMarker, snapshotState]);

  const onNodeClick = useCallback((_: any, node: any) => {
    if (readOnly) return;
    const newLabel = prompt("Nhập tên đỉnh mới:", node.data.label);
    if (newLabel !== null) {
      setData((prev: any) => ({
        ...prev,
        nodes: prev.nodes.map((n: any) => 
          n.id === node.id ? { ...n, data: { ...n.data, label: newLabel } } : n
        ),
      }));
    }
  }, [setData, readOnly]);

  const onEdgeClick = useCallback((_: any, edge: any) => {
    if (readOnly) return;
    const newWeight = prompt("Nhập trọng số mới:", edge.data?.weight);
    if (newWeight !== null) {
      setData((prev: any) => ({
        ...prev,
        edges: prev.edges.map((e: any) => 
          e.id === edge.id ? { ...e, data: { ...e.data, weight: Number(newWeight) } } : e
        ),
      }));
    }
  }, [setData, readOnly]);

  return (
    <div className="w-full h-full bg-[#0f172a]">
      <ReactFlow
        nodes={enhancedNodes}
        edges={enhancedEdges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onPaneClick={onPaneClick}
        selectNodesOnDrag={true}
        connectOnClick={true}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
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