export type ByokProvider = string;

export interface ByokKey {
  id: string;
  provider: ByokProvider;
  model: string;
  modelId: string;
  label?: string | null;
  keyPreview: string;
  createdAt: string;
}

export interface CreateByokKeyRequest {
  provider: ByokProvider;
  model: string;
  apiKey: string;
  label?: string;
}

export interface ByokProviderOption {
  value: ByokProvider;
  label: string;
  defaultModel: string;
}

export interface ByokProviderModelOption {
  value: string;
  label: string;
  isDefault?: boolean;
}
