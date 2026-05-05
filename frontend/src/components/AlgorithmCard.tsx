// src/components/AlgorithmCard.tsx
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Lock } from "lucide-react";
import { useUserStore } from "@/store/userStore";
import { useState, useEffect } from "react";

interface AlgorithmCardProps {
  id: string;
  title: string;
  bgColor: string;
  imageUrl: string;
}

export default function AlgorithmCard({ id, title, bgColor, imageUrl }: AlgorithmCardProps) {
  const router = useRouter();
  const isAuthenticated = useUserStore((state) => state.isAuthenticated);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleClick = (e: React.MouseEvent) => {
    if (!mounted || !isAuthenticated) {
      e.preventDefault();
      router.push("/login");
      return;
    }
  };

  const content = (
    <div 
      className="group flex flex-col border border-gray-200 rounded-md overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer bg-white"
      onClick={handleClick}
    >
      {/* Phần hình ảnh minh họa với màu nền đặc trưng */}
      <div className={`h-40 ${bgColor} flex items-center justify-center p-6 group-hover:opacity-90 transition-opacity relative`}>
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-full object-contain filter brightness-0 invert opacity-80" 
        />
        
        {/* Lock icon overlay khi chưa login */}
        {!isAuthenticated && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center rounded-sm">
            <Lock className="text-white" size={40} />
          </div>
        )}
      </div>
      
      {/* Phần thông tin phía dưới */}
      <div className="p-3 flex justify-between items-center border-t border-gray-100">
        <h3 className="font-bold text-gray-700 text-xs tracking-tight uppercase">
          {title}
        </h3>
        <button 
          className="bg-[#e91e63] hover:bg-[#ad1457] text-white px-2 py-1 rounded text-[10px] font-bold transition-colors"
          onClick={(e) => {
            e.preventDefault();
            if (!isAuthenticated) {
              router.push("/login");
            }
          }}
        >
          {isAuthenticated ? "MÔ PHỎNG" : "ĐĂNG NHẬP"}
        </button>
      </div>
    </div>
  );

  if (!isAuthenticated) {
    return content;
  }

  return (
    <Link href={`/algorithm/${id}`} className="block">
      {content}
    </Link>
  );
}