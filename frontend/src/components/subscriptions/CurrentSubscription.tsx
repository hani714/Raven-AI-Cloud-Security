import type { UserSubscription } from "../../interfaces/subscription";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Button } from "../../ui/button";
import { Badge } from "../../ui/badge";
import { AlertTriangle } from "lucide-react";

interface CurrentSubscriptionProps {
  subscription: UserSubscription;
  onRevoke: () => void;
  isRevoking: boolean;
}

const statusVariantMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  active: "default",
  canceled: "destructive",
  expired: "outline",
  pending: "secondary",
  unknown: "outline",
};

const formatDate = (value?: string | null): string => {
  if (!value) return "Not available";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not available";
  return date.toLocaleDateString();
};

const formatAutoRenew = (value?: boolean | null): string => {
  if (value === null || value === undefined) return "Not available";
  return value ? "Yes" : "No";
};

const Field = ({ label, value }: { label: string; value: React.ReactNode }) => (
  <div>
    <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{label}</p>
    <p className="font-mono text-sm text-foreground mt-1">{value}</p>
  </div>
);

const CurrentSubscription = ({ subscription, onRevoke, isRevoking }: CurrentSubscriptionProps) => {
  return (
    <Card className="glass-card">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="font-display text-lg">Current Subscription</CardTitle>
        <Badge
          variant={statusVariantMap[subscription.status] || "outline"}
          className="font-mono uppercase tracking-wider"
        >
          {subscription.status}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <Field label="Plan" value={subscription.name} />
          <Field label="Start Date" value={formatDate(subscription.startDate)} />
          <Field label="End Date" value={formatDate(subscription.endDate)} />
          <Field label="Auto Renew" value={formatAutoRenew(subscription.autoRenew)} />
          <Field label="Max Environments" value={subscription.maxEnvironments} />
          <Field label="Scans / Month" value={subscription.maxScansPerMonth} />
        </div>

        {subscription.status === "active" && (
          <div className="flex items-center gap-3 pt-3 border-t border-border">
            <AlertTriangle className="h-4 w-4 text-primary shrink-0" />
            <p className="text-xs text-muted-foreground flex-1">
              Cancellation is scheduled at period end. Your current access remains active until expiry.
            </p>
            <Button
              variant="destructive"
              size="sm"
              onClick={onRevoke}
              disabled={isRevoking}
              className="bg-primary/15 border border-primary/40 text-primary hover:bg-primary/25 font-mono text-xs uppercase tracking-widest"
            >
              {isRevoking ? "Scheduling..." : "Cancel at period end"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CurrentSubscription;
