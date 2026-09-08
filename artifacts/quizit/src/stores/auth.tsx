import { createContext, useCallback, useContext, useMemo, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getGetCurrentUserQueryKey,
  useGetCurrentUser,
  useLogin,
  useLogout as useLogoutMutation,
  useRegister,
  useUpdateCurrentUser,
  type User,
  type UserCreate,
  type UserLogin,
  type UserUpdate,
} from "@workspace/api-client-react";

interface AuthContextValue {
  user: User | null;
  isReady: boolean;
  isAuthenticated: boolean;
  login: (payload: UserLogin) => Promise<User>;
  signup: (payload: UserCreate) => Promise<User>;
  updateProfile: (payload: UserUpdate) => Promise<User>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const meQuery = useGetCurrentUser({
    query: { queryKey: getGetCurrentUserQueryKey(), retry: false, refetchOnWindowFocus: false, staleTime: 60_000 },
  });
  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const updateMutation = useUpdateCurrentUser();
  const logoutMutation = useLogoutMutation();

  const setUser = useCallback(
    (user: User) => {
      queryClient.setQueryData(getGetCurrentUserQueryKey(), user);
    },
    [queryClient],
  );

  const login = useCallback(
    async (payload: UserLogin) => {
      const response = await loginMutation.mutateAsync({ data: payload });
      setUser(response.user);
      return response.user;
    },
    [loginMutation, setUser],
  );

  const signup = useCallback(
    async (payload: UserCreate) => {
      const response = await registerMutation.mutateAsync({ data: payload });
      setUser(response.user);
      return response.user;
    },
    [registerMutation, setUser],
  );

  const updateProfile = useCallback(
    async (payload: UserUpdate) => {
      const user = await updateMutation.mutateAsync({ data: payload });
      setUser(user);
      return user;
    },
    [updateMutation, setUser],
  );

  const logout = useCallback(async () => {
    try {
      await logoutMutation.mutateAsync();
    } finally {
      queryClient.clear();
    }
  }, [logoutMutation, queryClient]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: meQuery.data ?? null,
      isReady: meQuery.isFetched,
      isAuthenticated: Boolean(meQuery.data),
      login,
      signup,
      updateProfile,
      logout,
    }),
    [meQuery.data, meQuery.isFetched, login, signup, updateProfile, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
