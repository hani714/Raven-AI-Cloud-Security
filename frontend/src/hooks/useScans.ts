import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { scanApi } from "@/services/api/scanApi";
import { toast } from "@/hooks/use-toast";
import type { ScanMode, ScanResult } from "@/interfaces/scan";

export const useScans = () => {
  const queryClient = useQueryClient();

  const { data: scans, isLoading, error } = useQuery({
    queryKey: ["scans"],
    queryFn: () => scanApi.getScans(),
  });

  const startScanMutation = useMutation({
    mutationFn: ({
      environmentId,
      scanName,
      mode,
      modelId,
    }: {
      environmentId: string;
      scanName: string;
      mode: ScanMode;
      modelId?: string;
    }) => scanApi.startScan(environmentId, scanName, mode, modelId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scans"] });
      toast({
        title: "Success",
        description: "Scan started successfully",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to start scan",
        variant: "destructive",
      });
    },
  });

  return {
    scans,
    isLoading,
    error,
    startScan: startScanMutation.mutate,
    isStarting: startScanMutation.isPending,
  };
};

export const useScanResult = (scanId: string) => {
  const { data: result, isLoading, error } = useQuery<ScanResult>({
    queryKey: ["scan-result", scanId],
    queryFn: () => scanApi.getScanResult(scanId),
    enabled: !!scanId,
  });

  return {
    result,
    isLoading,
    error,
  };
};

export const useScanAnalysis = (scanId: string) => {
  const { data: result, isLoading, error } = useQuery({
    queryKey: ["scan-analysis", scanId],
    queryFn: () => scanApi.getScanAnalysis(scanId),
    enabled: !!scanId,
    retry: false,
    refetchOnWindowFocus: false,
  });

  return {
    result,
    isLoading,
    error,
  };
};
