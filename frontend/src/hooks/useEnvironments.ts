import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { environmentApi } from "@/services/api/environmentApi";
import  type { CreateCredentialRequest } from "@/interfaces/environment";
import { toast } from "@/hooks/use-toast";

export const useEnvironments = () => {
  const queryClient = useQueryClient();
  const [testingId, setTestingId] = useState<string | null>(null);

  const { data: credentials, isLoading, error } = useQuery({
    queryKey: ["credentials"],
    queryFn: () => environmentApi.getCredentials(),
  });

  const createCredentialMutation = useMutation({
    mutationFn: (data: CreateCredentialRequest) => environmentApi.createCredential(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["credentials"] });
      toast({
        title: "Success",
        description: "AWS credentials added successfully",
      });
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || error?.message || "Failed to add credentials";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  const deleteCredentialMutation = useMutation({
    mutationFn: (id: string) => environmentApi.deleteCredential(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["credentials"] });
      toast({
        title: "Success",
        description: "Credentials deleted successfully",
      });
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || error?.message || "Failed to delete credentials";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  const importCredentialsMutation = useMutation({
    mutationFn: (file: File) => environmentApi.importCredentials(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["credentials"] });
      toast({
        title: "Success",
        description: "Credentials imported successfully",
      });
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || error?.message || "Failed to import credentials";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  const testCredentialMutation = useMutation({
    mutationFn: (id: string) => environmentApi.testCredential(id),
    onMutate: (id: string) => {
      setTestingId(id);
    },
    onSuccess: (isValid) => {
      toast({
        title: isValid ? "Valid Credentials" : "Invalid Credentials",
        description: isValid
          ? "Connection to AWS successful"
          : "Failed to connect to AWS",
        variant: isValid ? "default" : "destructive",
      });
    },
    onSettled: () => {
      setTestingId(null);
    },
  });

  return {
    credentials,
    isLoading,
    error,
    createCredential: createCredentialMutation.mutate,
    deleteCredential: deleteCredentialMutation.mutate,
    importCredentials: importCredentialsMutation.mutate,
    testCredential: testCredentialMutation.mutate,
    isCreating: createCredentialMutation.isPending,
    isDeleting: deleteCredentialMutation.isPending,
    isImporting: importCredentialsMutation.isPending,
    isTesting: testCredentialMutation.isPending,
    testingId,
  };
};
