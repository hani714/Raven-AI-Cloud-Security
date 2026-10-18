import { apiClient } from './client';
import type { Scan, ScanMode } from "@/interfaces/scan";

class ScanApi {
  /**
   * Get all scans for the current authenticated user
   */
  async getScans(): Promise<Scan[]> {
    const response = await apiClient.get<Scan[]>('/scans/');
    return response.data;
  }

  /**
   * Start a new scan for a specific environment
   */
  async startScan(environmentId: string, scanName: string, mode: ScanMode, modelId?: string): Promise<Scan> {
    const payload: any = {
      environment_id: environmentId,
      scan_name: scanName,
      mode,
    };

    if (modelId) payload.model_id = modelId;

    const response = await apiClient.post<Scan>('/scans/', payload);
    return response.data;
  }

  /**
   * Get scan results by scan ID
   */
  async getScanResult(scanId: string): Promise<any> {
    const response = await apiClient.get(`/scans/${scanId}/results/`);
    return response.data;
  }

  /**
   * Get scan analysis by scan ID
   */
  async getScanAnalysis(scanId: string): Promise<any> {
    const response = await apiClient.get(`/genai/${scanId}/`);
    return response.data;
  }

  /**
   * Delete a scan by ID
   */
  async deleteScan(scanId: string): Promise<void> {
    await apiClient.delete(`/scans/${scanId}`);
  }

  /**
   * Get scan details by ID
   */
  async getScanById(scanId: string): Promise<Scan> {
    const response = await apiClient.get<Scan>(`/scans/${scanId}`);
    return response.data;
  }
}

export const scanApi = new ScanApi();
