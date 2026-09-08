import { useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/stores/auth";

/** Client-side guard: sends unauthenticated visitors to /login. */
export function useRequireAuth() {
  const { isReady, isAuthenticated } = useAuth();
  const [, navigate] = useLocation();

  useEffect(() => {
    if (isReady && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isReady, isAuthenticated, navigate]);

  return { isReady, isAuthenticated };
}
