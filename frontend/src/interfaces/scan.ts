export type ScanMode = "enumeration" | "analysis";

export interface Scan {
  id: string;
  scanName: string;
  environmentId: string;
  environmentName: string;
  mode: ScanMode;
  status: 'completed' | 'running' | 'failed';
  createdAt: string;
  completedAt?: string;
}

export interface ScanResult {
  id: string;
  scanId: string;
  data: any; // Raw JSON object from backend
}
