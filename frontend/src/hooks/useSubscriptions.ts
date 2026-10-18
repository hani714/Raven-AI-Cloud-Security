import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { subscriptionApi } from "@/services/api/subscriptionApi";
import { useToast } from "@/hooks/use-toast";

const getErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
};

const normalizeCheckoutUrl = (checkoutUrl: string): string => {
  try {
    const parsed = new URL(checkoutUrl);
    const transactionId = parsed.searchParams.get("_ptxn");

    if (transactionId) {
      const localCheckoutUrl = new URL("/checkout", window.location.origin);
      localCheckoutUrl.searchParams.set("_ptxn", transactionId);
      return localCheckoutUrl.toString();
    }

    return checkoutUrl;
  } catch {
    return checkoutUrl;
  }
};

export const useSubscriptions = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: plans, isLoading: isLoadingPlans } = useQuery({
    queryKey: ["subscription-plans"],
    queryFn: () => subscriptionApi.getPlans(),
  });

  const { data: currentSubscription, isLoading: isLoadingSubscription } = useQuery({
    queryKey: ["user-subscription"],
    queryFn: () => subscriptionApi.getUserSubscription(),
  });

  const subscribeMutation = useMutation({
    mutationFn: (planId: string) => subscriptionApi.subscribe(planId),
    onSuccess: (result) => {
      if (result.action === "checkout") {
        toast({
          title: "Redirecting",
          description: result.message || "Launching secure checkout...",
        });

        window.location.assign(normalizeCheckoutUrl(result.checkoutUrl));
        return;
      }

      queryClient.invalidateQueries({ queryKey: ["user-subscription"] });

      toast({
        title: result.action === "applied" ? "Subscription Updated" : "No Change",
        description:
          result.action === "applied"
            ? `${result.message} Please log out and log in again to refresh token limits.`
            : result.message,
      });
    },
    onError: (error: unknown) => {
      toast({
        title: "Error",
        description: getErrorMessage(error, "Failed to subscribe"),
        variant: "destructive",
      });
    },
  });

  const revokeMutation = useMutation({
    mutationFn: () => subscriptionApi.revokeSubscription(),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["user-subscription"] });
      toast({
        title: "Cancellation Scheduled",
        description: result.message || "Your subscription will end at the end of the billing period.",
      });
    },
    onError: (error: unknown) => {
      toast({
        title: "Error",
        description: getErrorMessage(error, "Failed to revoke"),
        variant: "destructive",
      });
    },
  });

  return {
    plans,
    currentSubscription,
    isLoading: isLoadingPlans || isLoadingSubscription,
    subscribe: subscribeMutation.mutate,
    isSubscribing: subscribeMutation.isPending,
    revokeSubscription: () => revokeMutation.mutate(),
    isRevoking: revokeMutation.isPending,
  };
};
