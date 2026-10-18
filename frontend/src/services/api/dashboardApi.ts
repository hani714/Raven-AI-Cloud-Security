import { apiClient } from './client';
import type { DashboardData, ScanActivity, VulnerabilityTrend, LastPentestSessionData } from '@/interfaces/dashboard';

const EMPTY_ACTIVITY: ScanActivity = {
  current_environments: 0,
  current_scans_per_month: 0,
  max_environments: 0,
  max_scans_per_month: 0,
  analysis_level: 'basic',
};

const toVulnerabilityTrend = (item: Record<string, unknown>): VulnerabilityTrend => ({
  date: String(item.created_at ?? ''),
  critical: Number(item.critical ?? 0),
  high: Number(item.high ?? 0),
  medium: Number(item.medium ?? 0),
  low: Number(item.low ?? 0),
});

export const dashboardApi = {
  async getDashboardData(): Promise<DashboardData> {
    const [lastPentestRes, vulnSummaryRes, activityRes] = await Promise.all([
      apiClient.get<LastPentestSessionData>('/dashboard/last-pentest'),
      apiClient.get<Record<string, unknown>[]>('/dashboard/vuln-summary'),
      apiClient.get<ScanActivity>('/dashboard/activity'),
    ]);

    return {
      lastSession: lastPentestRes.data ?? null,
      vulnerabilityTrends: (vulnSummaryRes.data ?? []).map(toVulnerabilityTrend),
      scanActivity: activityRes.data ?? EMPTY_ACTIVITY,
    };
  },
};
