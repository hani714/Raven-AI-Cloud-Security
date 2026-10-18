import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { byokApi } from "@/services/api/byokApi";
import type { CreateByokKeyRequest } from "@/interfaces/byok";
import { toast } from "@/hooks/use-toast";

export const useByok = () => {
  const queryClient = useQueryClient();

  const { data: keys, isLoading, error } = useQuery({
    queryKey: ["byok-keys"],
    queryFn: () => byokApi.getKeys(),
  });

  const {
    data: providers = [],
    isLoading: isProvidersLoading,
    error: providersError,
  } = useQuery({
    queryKey: ["byok-providers"],
    queryFn: () => byokApi.getProviders(),
  });

  const createKeyMutation = useMutation({
    mutationFn: (data: CreateByokKeyRequest) => byokApi.createKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["byok-keys"] });
      toast({ title: "Key saved", description: "Your API key has been securely stored." });
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || err?.message || "Failed to save key";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const deleteKeyMutation = useMutation({
    mutationFn: (id: string) => byokApi.deleteKey(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["byok-keys"] });
      toast({ title: "Key deleted", description: "The API key has been removed." });
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || err?.message || "Failed to delete key";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  return {
    keys,
    isLoading,
    error,
    providers,
    isProvidersLoading,
    providersError,
    createKey: createKeyMutation.mutate,
    deleteKey: deleteKeyMutation.mutate,
    isCreating: createKeyMutation.isPending,
    isDeleting: deleteKeyMutation.isPending,
  };
};

export const useByokModels = (providerSlug: string) => {
  return useQuery({
    queryKey: ["byok-models", providerSlug],
    queryFn: () => byokApi.getProviderModels(providerSlug),
    enabled: Boolean(providerSlug),
  });
};
