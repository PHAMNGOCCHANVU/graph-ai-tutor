"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useUserStore } from "@/store/userStore";
import { register } from "@/services/auth";

export default function SignupPage() {
  const router = useRouter();
  const setAuth = useUserStore((state) => state.setAuth);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Validation
      if (!username || !email || !password || !passwordConfirm) {
        throw new Error("Vui lòng điền đầy đủ thông tin");
      }

      if (password.length < 8) {
        throw new Error("Mật khẩu phải có ít nhất 8 ký tự");
      }

      if (password !== passwordConfirm) {
        throw new Error("Mật khẩu xác nhận không trùng khớp");
      }

      if (username.length < 3) {
        throw new Error("Tên người dùng phải có ít nhất 3 ký tự");
      }

      const response = await register({ username, email, password });
      setAuth(response.user, response.access_token, response.refresh_token);

      // Redirect to home page
      router.push("/");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Đăng ký thất bại";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold tracking-[0.2em] text-white mb-2">
            VISUAL<span className="text-pink-500 font-light">ALGORITHM</span>
          </h1>
          <p className="text-slate-400">Tạo tài khoản để bắt đầu</p>
        </div>

        {/* Form */}
        <div className="bg-slate-800 rounded-lg shadow-2xl p-8 border border-slate-700">
          <h2 className="text-2xl font-bold text-white mb-6">Đăng ký</h2>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-900/30 border border-red-500/50 rounded-lg">
              <p className="text-red-300 text-sm">⚠️ {error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Tên người dùng
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="user123"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 transition"
                disabled={loading}
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 transition"
                disabled={loading}
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Mật khẩu
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 transition"
                disabled={loading}
              />
              <p className="text-slate-500 text-xs mt-1">Tối thiểu 8 ký tự</p>
            </div>

            {/* Password Confirm */}
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-2">
                Xác nhận mật khẩu
              </label>
              <input
                type="password"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 transition"
                disabled={loading}
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700 text-white font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {loading ? "Đang đăng ký..." : "Đăng ký"}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center border-t border-slate-700 pt-6">
            <p className="text-slate-400">
              Đã có tài khoản?{" "}
              <Link href="/login" className="text-pink-500 hover:text-pink-400 font-semibold">
                Đăng nhập
              </Link>
            </p>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-slate-500 text-xs">
          <p>Tên người dùng phải có ít nhất 3 ký tự</p>
        </div>
      </div>
    </div>
  );
}
