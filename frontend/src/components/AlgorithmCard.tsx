// src/components/AlgorithmCard.tsx
import Link from "next/link"; // 1. Import Link để chuyển trang

interface AlgorithmCardProps {
  id: string;
  title: string;
  bgColor: string;
  imageUrl: string;
}

// 2. Thêm 'id' vào trong dấu ngoặc nhọn bên dưới
export default function AlgorithmCard({ id, title, bgColor, imageUrl }: AlgorithmCardProps) {
  return (
    // 3. Bao bọc toàn bộ div bằng thẻ Link trỏ tới đường dẫn động
    <Link href={`/algorithm/${id}`} className="block">
      <div className="group flex flex-col border border-gray-200 rounded-md overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer bg-white">
        {/* Phần hình ảnh minh họa với màu nền đặc trưng */}
        <div className={`h-40 ${bgColor} flex items-center justify-center p-6 group-hover:opacity-90 transition-opacity`}>
          <img 
            src={imageUrl} 
            alt={title} 
            className="w-full h-full object-contain filter brightness-0 invert opacity-80" 
          />
        </div>
        
        {/* Phần thông tin phía dưới */}
        <div className="p-3 flex justify-between items-center border-t border-gray-100">
          <h3 className="font-bold text-gray-700 text-xs tracking-tight uppercase">
            {title}
          </h3>
          <button className="bg-[#e91e63] hover:bg-[#ad1457] text-white px-2 py-1 rounded text-[10px] font-bold transition-colors">
            MÔ PHỎNG
          </button>
        </div>
      </div>
    </Link>
  );
}