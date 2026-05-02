// src/components/CircleNode.tsx
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export default function CircleNode({ data, selected }: NodeProps) {
  // Xác định trạng thái node từ data
  const isActive = data.active === true;
  const isVisited = data.visited === true;
  const isQueued = data.queued === true;
  const distance = data.distance;

  // Xác định class CSS dựa trên trạng thái
  let borderColor = 'border-[#334155]';
  let bgColor = 'bg-white';
  let shadowStyle = 'shadow-[0_4px_10px_rgba(0,0,0,0.3)]';
  let scaleClass = '';

  if (isActive) {
    borderColor = 'border-pink-500';
    bgColor = 'bg-pink-50';
    shadowStyle = 'shadow-[0_0_20px_rgba(219,39,119,0.6)]';
    scaleClass = 'scale-110';
  } else if (isVisited) {
    borderColor = 'border-blue-500';
    bgColor = 'bg-blue-50';
    shadowStyle = 'shadow-[0_0_12px_rgba(59,130,246,0.4)]';
  } else if (isQueued) {
    borderColor = 'border-amber-400';
    bgColor = 'bg-amber-50';
    shadowStyle = 'shadow-[0_0_12px_rgba(251,191,36,0.4)]';
  }

  return (
    <div className={`
      w-16 h-16 rounded-full flex items-center justify-center transition-all duration-500
      ${bgColor} border-[4px] relative
      ${selected ? 'border-pink-500 scale-110 shadow-[0_0_15px_rgba(219,39,119,0.5)]' : borderColor}
      ${scaleClass} ${shadowStyle}
    `}>
      {/* Nhãn của Node */}
      <div className="flex flex-col items-center">
        <span className="text-[#1e293b] font-black text-2xl select-none leading-none">
          {data.label}
        </span>
        {distance !== undefined && distance !== null && (
          <span className="text-[10px] font-mono text-slate-500 mt-0.5">
            {distance}
          </span>
        )}
      </div>

      {/* Handles */}
      <div className={`transition-opacity duration-200 ${selected || isActive ? 'opacity-100' : 'opacity-0'}`}>
        {/* TOP */}
        <Handle 
          type="source" position={Position.Top} id="s-top" 
          style={{ left: '40%' }} 
          className="!w-2 !h-2 !bg-pink-500 !border-white" 
        />
        <Handle 
          type="target" position={Position.Top} id="t-top" 
          style={{ left: '60%' }} 
          className="!w-2 !h-2 !bg-blue-500 !border-white" 
        />

        {/* BOTTOM */}
        <Handle 
          type="source" position={Position.Bottom} id="s-bottom" 
          style={{ left: '60%' }} 
          className="!w-2 !h-2 !bg-pink-500 !border-white" 
        />
        <Handle 
          type="target" position={Position.Bottom} id="t-bottom" 
          style={{ left: '40%' }} 
          className="!w-2 !h-2 !bg-blue-500 !border-white" 
        />

        {/* LEFT */}
        <Handle 
          type="source" position={Position.Left} id="s-left" 
          style={{ top: '60%' }} 
          className="!w-2 !h-2 !bg-pink-500 !border-white" 
        />
        <Handle 
          type="target" position={Position.Left} id="t-left" 
          style={{ top: '40%' }} 
          className="!w-2 !h-2 !bg-blue-500 !border-white" 
        />

        {/* RIGHT */}
        <Handle 
          type="source" position={Position.Right} id="s-right" 
          style={{ top: '40%' }} 
          className="!w-2 !h-2 !bg-pink-500 !border-white" 
        />
        <Handle 
          type="target" position={Position.Right} id="t-right" 
          style={{ top: '60%' }} 
          className="!w-2 !h-2 !bg-blue-500 !border-white" 
        />
      </div>
    </div>
  );
}