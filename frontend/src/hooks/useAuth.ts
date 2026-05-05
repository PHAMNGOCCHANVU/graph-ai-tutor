"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUserStore } from "@/store/userStore";

/**
 * Hook to protect pages that require authentication
 * Redirects to /login if user is not authenticated
 *
 * Usage:
 * ```
 * export default function ProtectedPage() {
 *   useRequireAuth();
 *   return <div>Protected content</div>;
 * }
 * ```
 */
export function useRequireAuth() {
  const router = useRouter();
  const isAuthenticated = useUserStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  return isAuthenticated;
}

/**
 * Hook to check if user is authenticated
 * Returns boolean without redirecting
 */
export function useIsAuthenticated() {
  const isAuthenticated = useUserStore((state) => state.isAuthenticated);
  return isAuthenticated;
}

/**
 * Hook to get current user
 * Returns user object or null
 */
export function useCurrentUser() {
  const user = useUserStore((state) => state.user);
  return user;
}
