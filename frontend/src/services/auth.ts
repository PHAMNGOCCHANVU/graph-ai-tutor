import { User } from "@/store/userStore";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TokenRefreshPayload {
  refresh_token: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Đăng ký tài khoản mới
 */
export async function register(payload: RegisterPayload): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMsg = "Đăng ký thất bại";
    try {
      const error = await response.json();
      errorMsg = error.detail || errorMsg;
    } catch {
      errorMsg = `Lỗi ${response.status}`;
    }
    throw new Error(errorMsg);
  }

  return await response.json();
}

/**
 * Đăng nhập với email và mật khẩu
 */
export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMsg = "Đăng nhập thất bại";
    try {
      const error = await response.json();
      errorMsg = error.detail || errorMsg;
    } catch {
      errorMsg = `Lỗi ${response.status}`;
    }
    throw new Error(errorMsg);
  }

  return await response.json();
}

/**
 * Làm mới access token bằng refresh token
 */
export async function refreshToken(
  refreshToken: string
): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    throw new Error("Không thể làm mới token");
  }

  return await response.json();
}

/**
 * Lấy thông tin người dùng hiện tại (protected endpoint)
 */
export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Không thể lấy thông tin người dùng");
  }

  return await response.json();
}

/**
 * Đăng xuất (client-side: xóa tokens)
 */
export async function logout(token: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    // Ignore response - just for server-side logging
  } catch {
    // Ignore errors on logout
  }
}
