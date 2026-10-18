import { apiClient } from "./client";
import type {
  ByokKey,
  ByokProviderModelOption,
  ByokProviderOption,
  CreateByokKeyRequest,
} from "@/interfaces/byok";

class ByokApi {
  async getKeys(): Promise<ByokKey[]> {
    const response = await apiClient.get<ByokKey[]>("/byok/keys");
    return response.data;
  }

  async getProviders(): Promise<ByokProviderOption[]> {
    const response = await apiClient.get<ByokProviderOption[]>("/byok/providers");
    return response.data;
  }

  async getProviderModels(providerSlug: string): Promise<ByokProviderModelOption[]> {
    const response = await apiClient.get<ByokProviderModelOption[]>(`/byok/providers/${providerSlug}/models`);
    return response.data;
  }

  async createKey(data: CreateByokKeyRequest): Promise<ByokKey> {
    const response = await apiClient.post<ByokKey>("/byok/keys", data);
    return response.data;
  }

  async deleteKey(id: string): Promise<void> {
    await apiClient.delete(`/byok/keys/${id}`);
  }
}

export const byokApi = new ByokApi();
