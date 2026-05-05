"use client";

import { useUserStore } from "@/store/userStore";
import { logError } from "@/utils/errorHandler";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const MAX_REFRESH_ATTEMPTS = 3;
const REFRESH_RETRY_DELAY_MS = 1000;

interface RefreshTokenResponse {
  access_token: string;
  expires_in: number;
}

/**
 * Refresh token with retry logic
 * Handles network errors and server failures gracefully
 */
export async function refreshTokenWithRetry(
  refreshToken: string,
  attempt: number = 1
): Promise<RefreshTokenResponse | null> {
  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // 401/403 means refresh token is invalid/expired
      if (response.status === 401 || response.status === 403) {
        logError("Token Refresh", `Refresh token expired (${response.status})`);
        return null;
      }

      // Server error - retry
      if (response.status >= 500 && attempt < MAX_REFRESH_ATTEMPTS) {
        logError(
          "Token Refresh",
          `Server error (${response.status}), retrying... attempt ${attempt}/${MAX_REFRESH_ATTEMPTS}`
        );
        await delay(REFRESH_RETRY_DELAY_MS * attempt);
        return refreshTokenWithRetry(refreshToken, attempt + 1);
      }

      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Refresh failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    logError("Token Refresh", error);

    // Network error - retry with backoff
    if (attempt < MAX_REFRESH_ATTEMPTS) {
      logError(
        "Token Refresh",
        `Network error, retrying... attempt ${attempt}/${MAX_REFRESH_ATTEMPTS}`
      );
      await delay(REFRESH_RETRY_DELAY_MS * attempt);
      return refreshTokenWithRetry(refreshToken, attempt + 1);
    }

    return null;
  }
}

/**
 * Helper to delay execution
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Validate if token is about to expire
 * Returns true if token expires within specified minutes
 */
export function isTokenExpiringSoon(
  expiresAt: number,
  withinMinutes: number = 5
): boolean {
  const now = Date.now();
  const expirationTime = expiresAt * 1000; // Convert to milliseconds
  const timeUntilExpiry = expirationTime - now;
  const withinMs = withinMinutes * 60 * 1000;

  return timeUntilExpiry <= withinMs;
}

/**
 * Decode JWT payload (without verification)
 * Returns payload object or null if invalid
 */
export function decodeJWT(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const decoded = JSON.parse(
      Buffer.from(parts[1], "base64").toString("utf-8")
    );
    return decoded;
  } catch {
    return null;
  }
}

/**
 * Get expiration time from JWT token
 * Returns timestamp in seconds or null if invalid
 */
export function getTokenExpiration(token: string): number | null {
  const payload = decodeJWT(token);
  return payload?.exp as number | null || null;
}

/**
 * Setup auto-refresh for access token
 * Refreshes token before it expires
 */
export function setupAutoRefresh(): () => void {
  const intervalId = setInterval(async () => {
    const state = useUserStore.getState();

    if (!state.accessToken || !state.refreshToken) {
      clearInterval(intervalId);
      return;
    }

    const expiresAt = getTokenExpiration(state.accessToken);
    if (!expiresAt) {
      clearInterval(intervalId);
      return;
    }

    // Refresh if token expires within 5 minutes
    if (isTokenExpiringSoon(expiresAt, 5)) {
      logError("Auto Refresh", "Token expiring soon, attempting refresh...");

      const newTokenResponse = await refreshTokenWithRetry(
        state.refreshToken
      );

      if (newTokenResponse) {
        state.setAccessToken(newTokenResponse.access_token);
        logError("Auto Refresh", "Token refreshed successfully");
      } else {
        logError("Auto Refresh", "Failed to refresh token, logging out...");
        state.logout();
      }
    }
  }, 60 * 1000); // Check every 1 minute

  // Return cleanup function
  return () => clearInterval(intervalId);
}
