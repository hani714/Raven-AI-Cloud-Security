import axios from "axios";

import type {
  SubscriptionPlan,
  SubscriptionPlanApiResponse,
  UserSubscription,
} from "../../interfaces/subscription";
import { apiClient } from "./client";

type SubscriptionChangeStatus = "NO_OP" | "PENDING_PAYMENT" | "APPLIED";

type SubscriptionChangeResponse = {
  request_id: string;
  status: SubscriptionChangeStatus;
  user_id: string;
  target_plan_id: string;
  target_plan_name: string;
  current_plan_id?: string | null;
  current_plan_name?: string | null;
  subscription_id?: string | null;
  requires_payment: boolean;
  checkout_url?: string | null;
  effective_at?: string | null;
  message: string;
};

type SubscribeResult =
  | { action: "checkout"; checkoutUrl: string; message: string }
  | { action: "applied" | "no-op"; message: string };

type JwtSubscriptionClaim = {
  id: string;
  name: string;
  scan_depth: UserSubscription["scanDepth"];
  analysis_level: UserSubscription["analysisLevel"];
  max_environments: number;
  max_scans_per_month: number;
};

const decodeJwtPayload = (token: string): Record<string, unknown> | null => {
  try {
    const parts = token.split(".");
    if (parts.length < 2 || !parts[1]) return null;

    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload.padEnd(Math.ceil(payload.length / 4) * 4, "=");
    return JSON.parse(atob(padded)) as Record<string, unknown>;
  } catch {
    return null;
  }
};

const toPlanView = (plan: SubscriptionPlanApiResponse): SubscriptionPlan => {
  const price = Number(plan.price);

  return {
    id: plan.id,
    name: plan.name,
    description: `${plan.scan_depth} scans with ${plan.analysis_level} analysis`,
    price: Number.isFinite(price) ? price : 0,
    interval: "month",
    features: [
      `${plan.max_environments} environments`,
      `${plan.max_scans_per_month} scans per month`,
      `${plan.scan_depth} scan depth`,
      `${plan.analysis_level} analysis level`,
      `${plan.history_days} days result history`,
    ],
    maxEnvironments: plan.max_environments,
    maxScansPerMonth: plan.max_scans_per_month,
    scanDepth: plan.scan_depth,
    analysisLevel: plan.analysis_level,
    historyDays: plan.history_days,
    isPopular: plan.name === "Professional",
  };
};

const extractMessage = (error: unknown, fallback: string): string => {
  if (!axios.isAxiosError(error)) return fallback;

  const detail = error.response?.data as { detail?: string } | undefined;
  return detail?.detail || error.message || fallback;
};

class SubscriptionApi {
  async getPlans(): Promise<SubscriptionPlan[]> {
    const response = await apiClient.get<SubscriptionPlanApiResponse[]>("/subscription/");
    return response.data.map(toPlanView);
  }

  async getUserSubscription(): Promise<UserSubscription | null> {
    const token = localStorage.getItem("access_token");
    if (!token) return null;

    const payload = decodeJwtPayload(token);
    const claim = payload?.subscription as JwtSubscriptionClaim | undefined;

    if (!claim?.id || !claim.name) {
      return null;
    }

    return {
      id: claim.id,
      name: claim.name,
      status: "active",
      startDate: null,
      endDate: null,
      autoRenew: null,
      maxEnvironments: claim.max_environments,
      maxScansPerMonth: claim.max_scans_per_month,
      scanDepth: claim.scan_depth,
      analysisLevel: claim.analysis_level,
    };
  }

  async subscribe(planId: string): Promise<SubscribeResult> {
    const user = localStorage.getItem("user");
    const userId = user ? (JSON.parse(user) as { id?: string }).id : undefined;

    if (!userId) {
      throw new Error("Unable to resolve current user. Please log in again.");
    }

    try {
      const response = await apiClient.post<SubscriptionChangeResponse>("/subscription/new", {
        user_id: userId,
        plan_id: planId,
      });

      if (response.data.status === "PENDING_PAYMENT") {
        const checkoutUrl = response.data.checkout_url;
        if (!checkoutUrl) {
          throw new Error("Checkout URL missing from subscription response");
        }

        return {
          action: "checkout",
          checkoutUrl,
          message: response.data.message,
        };
      }

      if (response.data.status === "NO_OP") {
        return {
          action: "no-op",
          message: response.data.message,
        };
      }

      return {
        action: "applied",
        message: response.data.message,
      };
    } catch (error) {
      throw new Error(extractMessage(error, "Failed to change subscription"));
    }
  }

  async revokeSubscription(): Promise<{ message: string }> {
    const user = localStorage.getItem("user");
    const userId = user ? (JSON.parse(user) as { id?: string }).id : undefined;

    if (!userId) {
      throw new Error("Unable to resolve current user. Please log in again.");
    }

    try {
      const response = await apiClient.post<{ message?: string }>("/subscription/revoke", {
        user_id: userId,
      });

      return {
        message: response.data?.message || "Subscription cancellation scheduled.",
      };
    } catch (error) {
      throw new Error(extractMessage(error, "Failed to revoke subscription"));
    }
  }
}

export const subscriptionApi = new SubscriptionApi();
