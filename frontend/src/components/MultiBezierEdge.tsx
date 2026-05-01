// src/components/MultiBezierEdge.tsx
import { BaseEdge, EdgeProps, EdgeLabelRenderer } from '@xyflow/react';

export default function MultiBezierEdge({
  sourceX, sourceY, targetX, targetY,
  data, style, markerEnd, label,
}: EdgeProps) {
  const offset = (data?.offset as number) || 0;

  const dx = targetX - sourceX;
  const dy = targetY - sourceY;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const nx = -dy / len; 
  const ny = dx / len;  

  // Dịch chuyển đường thẳng
  const sx = sourceX + nx * offset;
  const sy = sourceY + ny * offset;
  const tx = targetX + nx * offset;
  const ty = targetY + ny * offset;

  // TÍNH VỊ TRÍ NHÃN: Đẩy nhãn ra xa đường thẳng một chút để không đè lên dây
  // offset > 0 thì đẩy nhãn theo hướng vector pháp tuyến, ngược lại thì đẩy ngược lại
  const labelDistance = 15; 
  const labelX = (sx + tx) / 2 + nx * (offset > 0 ? labelDistance : -labelDistance);
  const labelY = (sy + ty) / 2 + ny * (offset > 0 ? labelDistance : -labelDistance);

  const path = `M ${sx},${sy} L ${tx},${ty}`;

  return (
    <>
      <BaseEdge path={path} markerEnd={markerEnd} style={style} />
      {label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              fontSize: '14px',
              fontWeight: 'bold',
              color: 'white',
              pointerEvents: 'none',
              // Bỏ background để giống hình mẫu VisuAlgo của bạn
              textShadow: '1px 1px 2px black', 
            }}
          >
            {label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}