"use client";

import Link from "next/link";
import { Lock } from "lucide-react";

interface UnauthorizedPageProps {
  message?: string;
  showLoginButton?: boolean;
}

export default function UnauthorizedPage({
  message = "Bạn cần đăng nhập để truy cập trang này",
  showLoginButton = true,
}: UnauthorizedPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="text-center">
        <Lock className="w-16 h-16 mx-auto mb-6 text-pink-500" />
        <h1 className="text-4xl font-bold text-white mb-4">Quyền truy cập bị từ chối</h1>
        <p className="text-slate-400 text-lg mb-8">{message}</p>

        {showLoginButton && (
          <div className="flex gap-4 justify-center">
            <Link
              href="/login"
              className="px-6 py-3 bg-pink-600 hover:bg-pink-700 text-white rounded-lg font-semibold transition"
            >
              Đăng nhập
            </Link>
            <Link
              href="/"
              className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition"
            >
              Quay lại trang chủ
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
