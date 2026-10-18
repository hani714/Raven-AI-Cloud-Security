import type { LoginCredentials, RegisterCredentials } from '@/interfaces/auth';
import type { AxiosResponse } from "axios";
import { apiClient } from "./api/client";
import type { AuthResponse, User } from "@/interfaces/auth";

export const authService = {
  /**
   * Login user and store auth token
   */
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await apiClient.post(
      "/auth/login",
      credentials
    );

    // Store token and user in localStorage
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }

    return response.data;
  },

  /**
   * Register new user
   */
  register: async (credentials: RegisterCredentials): Promise<User> => {
    const response: AxiosResponse<User> = await apiClient.post(
      "/auth/register",
      credentials
    );

    return response.data;
  },

  /**
   * Logout user and clears local auth data
   */
  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/auth/logout");
    } finally {
      // Always clear local state regardless of backend response
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
    }
  },

  /**
   * Get stored auth token
   */
  getToken: (): string | null => {
    return localStorage.getItem("access_token");
  },

  /**
   * Get stored user data
   */
  getUser: (): User | null => {
    const userStr = localStorage.getItem("user");
    if (!userStr) return null;

    try {
      return JSON.parse(userStr) as User;
    } catch {
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!authService.getToken();
  },

  /**
   * Send OTP to user email
   */
  sendOtp: async ({ email }: { email: string }): Promise<{ message: string }> => {
    const response: AxiosResponse<{ message: string }> = await apiClient.post(
      "/auth/otp/send",
      { email }
    );
    return response.data;
  },

  /**
   * Verify OTP for user
   */
  verifyOtp: async ({ email, code }: { email: string; code: string }): Promise<{ message: string }> => {
    const response: AxiosResponse<{ message: string }> = await apiClient.post(
      "/auth/otp/verify",
      { email, code }
    );
    return response.data;
  },

  /**
   * Verify OTP for password reset — returns a short-lived reset token
   */
  verifyResetOtp: async ({ email, code }: { email: string; code: string }): Promise<{ message: string; access_token: string }> => {
    const response: AxiosResponse<{ message: string; access_token: string }> = await apiClient.post(
      "/auth/verify-reset",
      { email, code }
    );
    return response.data;
  },

  /**
   * Reset password using the short-lived reset token
   */
  resetPassword: async ({ newPassword, resetToken }: { newPassword: string; resetToken: string }): Promise<{ message: string }> => {
    const response: AxiosResponse<{ message: string }> = await apiClient.post(
      "/auth/reset-password",
      { newPassword },
      { headers: { Authorization: `Bearer ${resetToken}` } }
    );
    return response.data;
  },
};
