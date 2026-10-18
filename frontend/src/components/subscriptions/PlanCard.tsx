import type { SubscriptionPlan } from "@/interfaces/subscription";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../../ui/card";
import { Button } from "../../ui/button";
import { Check } from "lucide-react";

interface PlanCardProps {
  plan: SubscriptionPlan;
  isCurrentPlan: boolean;
  onSubscribe: (planId: string) => void;
  isSubscribing: boolean;
}

const PlanCard = ({ plan, isCurrentPlan, onSubscribe, isSubscribing }: PlanCardProps) => {
  return (
    <Card
      className={`relative flex flex-col glass-card transition-all duration-300 hover:-translate-y-1 ${
        plan.isPopular
          ? "border-primary/60 shadow-[0_0_48px_-10px_hsl(var(--primary)/0.6)] scale-[1.02]"
          : "hover:border-secondary/40"
      }`}
    >
      {plan.isPopular && (
        <>
          <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-0.5 font-mono text-[10px] uppercase tracking-widest font-semibold text-primary-foreground shadow-[0_0_24px_-4px_hsl(var(--primary))]">
            Most Popular
          </span>
          <div className="pointer-events-none absolute inset-0 rounded-xl border border-primary/30 animate-pulse-glow" />
        </>
      )}
      <CardHeader>
        <CardTitle className="font-display text-xl">{plan.name}</CardTitle>
        <CardDescription>{plan.description}</CardDescription>
        <div className="mt-4">
          <span className="font-display text-4xl font-bold text-foreground">${plan.price}</span>
          <span className="font-mono text-sm text-muted-foreground">/{plan.interval}</span>
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <ul className="space-y-3">
          {plan.features.map((feature) => (
            <li key={feature} className="flex items-center gap-2 text-sm text-muted-foreground">
              <Check className="h-4 w-4 text-primary shrink-0" />
              {feature}
            </li>
          ))}
        </ul>
      </CardContent>
      <CardFooter>
        {isCurrentPlan ? (
          <Button className="w-full font-mono text-xs uppercase tracking-widest" variant="secondary" disabled>
            Current Plan
          </Button>
        ) : (
          <Button
            className={`w-full font-mono text-xs uppercase tracking-widest ${
              plan.isPopular
                ? "bg-primary text-primary-foreground hover:bg-primary-glow shadow-[0_0_24px_-4px_hsl(var(--primary)/0.6)]"
                : "bg-secondary/10 hover:bg-secondary/20 text-secondary border border-secondary/30"
            }`}
            variant={plan.isPopular ? "default" : "outline"}
            onClick={() => onSubscribe(plan.id)}
            disabled={isSubscribing}
          >
            {isSubscribing ? "Subscribing..." : "Subscribe →"}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
};

export default PlanCard;
