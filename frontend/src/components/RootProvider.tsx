"use client";

import { useEffect, useRef } from "react";
import { useUserStore } from "@/store/userStore";
import { setupAutoRefresh } from "@/utils/tokenRefresh";
import { SessionTimeout } from "@/utils/sessionTimeout";

export default function RootProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const autoRefreshCleanup = useRef<(() => void) | null>(null);
  const sessionTimeout = useRef<SessionTimeout | null>(null);
  const isAuthenticated = useUserStore((state) => state.isAuthenticated);
  const logout = useUserStore((state) => state.logout);

  useEffect(() => {
    // Load auth from localStorage on app start
    const loadFromStorage = useUserStore.getState().loadFromStorage;
    loadFromStorage();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      // Setup auto-refresh for access token (checks every 1 minute)
      if (!autoRefreshCleanup.current) {
        autoRefreshCleanup.current = setupAutoRefresh();
      }

      // Setup session timeout (30 minutes inactivity)
      if (!sessionTimeout.current) {
        sessionTimeout.current = new SessionTimeout(
          30 * 60 * 1000, // 30 minutes
          () => {
            // Auto-logout after 30 minutes of inactivity
            console.warn("Session timeout - logging out due to inactivity");
            logout();
          }
        );
        sessionTimeout.current.start();
      }
    } else {
      // Cleanup auto-refresh when logged out
      if (autoRefreshCleanup.current) {
        autoRefreshCleanup.current();
        autoRefreshCleanup.current = null;
      }

      // Stop session timeout when logged out
      if (sessionTimeout.current) {
        sessionTimeout.current.stop();
        sessionTimeout.current = null;
      }
    }

    return () => {
      // Cleanup on unmount
      if (autoRefreshCleanup.current) {
        autoRefreshCleanup.current();
      }
      if (sessionTimeout.current) {
        sessionTimeout.current.stop();
      }
    };
  }, [isAuthenticated, logout]);

  return <>{children}</>;
}
