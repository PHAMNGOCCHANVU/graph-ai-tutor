"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useUserStore } from "@/store/userStore";
import { logout } from "@/services/auth";
import { LogOut, User } from "lucide-react";

export default function AuthHeader() {
  const router = useRouter();
  const user = useUserStore((state) => state.user);
  const accessToken = useUserStore((state) => state.accessToken);
  const logoutAction = useUserStore((state) => state.logout);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const handleLogout = async () => {
    if (accessToken) {
      try {
        await logout(accessToken);
      } catch {
        // Ignore errors
      }
    }
    logoutAction();
    router.push("/");
  };

  if (user) {
    return (
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-slate-300">
          <User size={18} />
          <span className="text-sm">{user.username}</span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-1.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition text-sm"
        >
          <LogOut size={16} />
          Đăng xuất
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <Link
        href="/login"
        className="px-4 py-1.5 text-slate-300 hover:text-white transition text-sm"
      >
        Đăng nhập
      </Link>
      <Link
        href="/signup"
        className="px-4 py-1.5 bg-pink-600 hover:bg-pink-700 text-white rounded-lg transition text-sm font-medium"
      >
        Đăng ký
      </Link>
    </div>
  );
}
