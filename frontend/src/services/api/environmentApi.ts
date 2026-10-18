import { apiClient } from './client';
import type { AWSCredential, CreateCredentialRequest } from "@/interfaces/environment";

class EnvironmentApi {
  
  // GET all credentials for current user
  async getCredentials(): Promise<AWSCredential[]> {
    const response = await apiClient.get<AWSCredential[]>('/environments/');
    return response.data;
  }

  // POST: create new credential
  async createCredential(data: CreateCredentialRequest): Promise<AWSCredential> {
    const response = await apiClient.post<AWSCredential>("/environments/", data);
    return response.data;
  }
  
  // DELETE: delete credential by ID
  async deleteCredential(id: string): Promise<void> {
    await apiClient.delete(`/environments/${id}`);
  }

  async importCredentials(_file: File): Promise<AWSCredential[]> {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    // In real implementation, parse CSV/JSON file
    // For now, return mock data
    return [];
  }

  // POST: test credential by ID
  async testCredential(id: string): Promise<boolean> {
    const response = await apiClient.post<{ is_valid: boolean; message: string }>(`/environments/${id}/test-connection`);
    return response.data.is_valid;
  }
}

export const environmentApi = new EnvironmentApi();
