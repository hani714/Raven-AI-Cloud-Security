export interface AWSCredential {
  id: string;
  name: string;
  accessKey: string;
  secretAccessKey: string;
  region?: string;
  userId: string;
  status: 'active' | 'inactive' | 'error';
  // Optional provider models exposed via environments for convenience
  models?: { id: string; value: string; label?: string }[];
}

export interface CreateCredentialRequest {
  name: string;
  accessKey: string;
  secretAccessKey: string;
  region?: string;
}

export interface ImportCredentialsRequest {
  file: File;
}
