export type ScanDepth = "quick" | "deep";
export type AnalysisLevel = "triage" | "deep" | "exploit";

export interface SubscriptionPlanApiResponse {
  id: string;
  name: string;
  price: string;
  max_environments: number;
  max_scans_per_month: number;
  scan_depth: ScanDepth;
  analysis_level: AnalysisLevel;
  history_days: number;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  interval: "month";
  features: string[];
  maxEnvironments: number;
  maxScansPerMonth: number;
  scanDepth: ScanDepth;
  analysisLevel: AnalysisLevel;
  historyDays: number;
  isPopular?: boolean;
}

export interface UserSubscription {
  id: string;
  name: string;
  status: "active" | "canceled" | "expired" | "pending" | "unknown";
  startDate?: string | null;
  endDate?: string | null;
  autoRenew?: boolean | null;
  maxEnvironments: number;
  maxScansPerMonth: number;
  scanDepth: ScanDepth;
  analysisLevel: AnalysisLevel;
}

export interface CheckoutSession {
  checkoutUrl: string;
}
