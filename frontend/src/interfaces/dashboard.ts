export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface LastPentestSessionData {
  scan_id: string;
  severity: SeverityLevel | string;
  triage?: {
    severity?: SeverityLevel | string;
    entry_points?: Array<{
      rank: number;
      resource: string;
      risk: string;
      exploitability: string;
    }>;
    quick_wins?: string[];
    requires_deep_analysis?: boolean;
  };
  risk_summary?: {
    overall_severity?: SeverityLevel | string;
    scores?: {
      iam?: number;
      s3?: number;
      lambda?: number;
    };
    findings?: Array<{
      type: string;
      severity: SeverityLevel | string;
      resource: string;
      detail: string;
      impact: string;
    }>;
    metadata?: {
      scan_id?: string;
      total_users?: number;
      total_roles?: number;
      total_groups?: number;
      total_s3_buckets?: number;
      total_lambda_functions?: number;
    };
  };
}

export interface ScanActivity {
  current_environments: number;
  current_scans_per_month: number;
  max_environments: number;
  max_scans_per_month: number;
  analysis_level: string;
}

export interface VulnerabilityTrend {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface DashboardData {
  lastSession: LastPentestSessionData | null;
  scanActivity: ScanActivity;
  vulnerabilityTrends: VulnerabilityTrend[];
}
