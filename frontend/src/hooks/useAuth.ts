import { useState, useEffect } from "react";

interface User {
  id: string;
  email: string;
}

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
}

export const useAuth = (): AuthState => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
  });

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const userStr = localStorage.getItem("user");

        if (token && userStr) {
          const user = JSON.parse(userStr) as User;
          setAuthState({
            isAuthenticated: true,
            isLoading: false,
            user,
          });
        } else {
          setAuthState({
            isAuthenticated: false,
            isLoading: false,
            user: null,
          });
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        setAuthState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
        });
      }
    };

    checkAuth();
  }, []);

  return authState;
};
