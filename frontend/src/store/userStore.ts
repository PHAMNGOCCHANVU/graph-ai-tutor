import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  // Actions
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  setAccessToken: (accessToken: string) => void;
  logout: () => void;
  loadFromStorage: () => void;
}

export const useUserStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setAuth: (user: User, accessToken: string, refreshToken: string) => {
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        });
        // Also save to localStorage
        localStorage.setItem(
          "auth",
          JSON.stringify({
            user,
            accessToken,
            refreshToken,
          })
        );
      },

      setAccessToken: (accessToken: string) => {
        set({ accessToken });
        const auth = localStorage.getItem("auth");
        if (auth) {
          const parsed = JSON.parse(auth);
          localStorage.setItem(
            "auth",
            JSON.stringify({
              ...parsed,
              accessToken,
            })
          );
        }
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
        localStorage.removeItem("auth");
      },

      loadFromStorage: () => {
        const auth = localStorage.getItem("auth");
        if (auth) {
          try {
            const parsed = JSON.parse(auth);
            set({
              user: parsed.user,
              accessToken: parsed.accessToken,
              refreshToken: parsed.refreshToken,
              isAuthenticated: !!parsed.user,
            });
          } catch (error) {
            console.error("Failed to load auth from storage", error);
            localStorage.removeItem("auth");
          }
        }
      },
    }),
    {
      name: "user-store", // Name of item in localStorage
    }
  )
);
