"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { api } from "./api";
import type { SignupResult } from "./types";

interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  // Returns a discriminated result so the caller can route based on whether
  // Supabase requires email confirmation. When requiresEmailConfirmation is
  // true NO tokens have been persisted — the user is NOT authenticated.
  signup: (email: string, password: string) => Promise<SignupResult>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    userId: null,
    isLoading: true,
  });

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userId = localStorage.getItem("user_id");
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setState({
      isAuthenticated: !!token,
      userId: userId,
      isLoading: false,
    });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.login(email, password);
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    localStorage.setItem("user_id", res.user_id);
    setState({ isAuthenticated: true, userId: res.user_id, isLoading: false });
  }, []);

  const signup = useCallback(
    async (email: string, password: string): Promise<SignupResult> => {
      const res = await api.signup(email, password);

      // Email-confirmation-required branch: backend returns empty token
      // strings. We MUST NOT persist them or set isAuthenticated, otherwise
      // the user will be redirected to a "logged in" dashboard that 401s on
      // every request.
      if (res.email_confirmation_required) {
        return { requiresEmailConfirmation: true, email };
      }

      localStorage.setItem("access_token", res.access_token);
      localStorage.setItem("refresh_token", res.refresh_token);
      localStorage.setItem("user_id", res.user_id);
      setState({
        isAuthenticated: true,
        userId: res.user_id,
        isLoading: false,
      });
      return { requiresEmailConfirmation: false, email };
    },
    []
  );

  const logout = useCallback(() => {
    api.logout().catch(() => {});
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_id");
    setState({ isAuthenticated: false, userId: null, isLoading: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
