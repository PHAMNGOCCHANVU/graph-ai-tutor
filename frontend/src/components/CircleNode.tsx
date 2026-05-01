// src/components/CircleNode.tsx
import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

export default function CircleNode({ data, selected }: NodeProps) {
  return (
    <div className={`
      w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300
      bg-white border-[4px] relative
      ${selected ? 'border-pink-500 scale-110 shadow-[0_0_15px_rgba(219,39,119,0.5)]' : 'border-[#334155]'}
      shadow-[0_4px_10px_rgba(0,0,0,0.3)]
    `}>
      {/* Nhãn của Node */}
      <span className="text-[#1e293b] font-black text-2xl select-none">
        {data.label}
      </span>

      {/* 
         MẸO: Để tránh ngược mũi tên và cho phép vẽ đường song song:
         - Source (Điểm kéo đi): Đặt lệch một chút (ví dụ 40%)
         - Target (Điểm nhận): Đặt lệch một chút (ví dụ 60%)
         - Khi selected = false, chúng ta để opacity-0 nhưng vẫn hoạt động để trông đẹp hơn.
      */}
      
      <div className={`transition-opacity duration-200 ${selected ? 'opacity-100' : 'opacity-0'}`}>
        
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