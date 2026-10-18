import { useSubscriptions } from "@/hooks/useSubscriptions";
import PlanCard from "../components/subscriptions/PlanCard";
import CurrentSubscription from "../components/subscriptions/CurrentSubscription";
import { PageHeader } from "@/components/common/PageHeader";
import { LoadingState } from "@/components/common/LoadingState";

const Subscriptions = () => {
  const {
    plans,
    currentSubscription,
    isLoading,
    subscribe,
    isSubscribing,
    revokeSubscription,
    isRevoking,
  } = useSubscriptions();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingState message="Loading subscriptions..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="w-full py-8 px-6 lg:px-8">
        <PageHeader
          label="billing"
          title="Subscriptions"
          description="Manage your subscription plan and billing"
        />

        {currentSubscription && (
          <div className="mb-8">
            <CurrentSubscription
              subscription={currentSubscription}
              onRevoke={revokeSubscription}
              isRevoking={isRevoking}
            />
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-3">
          {plans?.map((plan) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              isCurrentPlan={currentSubscription?.id === plan.id}
              onSubscribe={subscribe}
              isSubscribing={isSubscribing}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Subscriptions;
