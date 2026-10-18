import { Button } from '@/ui/button';
import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';

const plans = [
  {
    name: 'Starter',
    price: '$49',
    period: '/month',
    description: 'Perfect for small teams getting started with AWS security.',
    features: [
      'Up to 5 AWS accounts',
      'Weekly automated scans',
      'Basic vulnerability reports',
      'Email support',
      '30-day scan history',
    ],
    highlighted: false,
    cta: 'Start Free Trial',
  },
  {
    name: 'Pro',
    price: '$199',
    period: '/month',
    description: 'For growing organizations with advanced security needs.',
    features: [
      'Unlimited AWS accounts',
      'Daily automated scans',
      'Advanced threat detection',
      'Priority support',
      '1-year scan history',
      'Custom compliance reports',
      'API access',
    ],
    highlighted: true,
    cta: 'Start Free Trial',
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'Tailored solutions for large-scale enterprise deployments.',
    features: [
      'Everything in Pro',
      'Dedicated account manager',
      'Custom integrations',
      'SLA guarantees',
      'On-premise deployment option',
      'Advanced RBAC',
      '24/7 phone support',
    ],
    highlighted: false,
    cta: 'Contact Sales',
  },
];

const PricingSection = () => {
  return (
    <section id="pricing" className="py-24 relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <span className="font-mono text-primary text-xs font-semibold tracking-[0.3em] uppercase">// Pricing</span>
          <h2 className="text-3xl md:text-4xl font-bold mt-4 font-display">
            Simple, Transparent Pricing
          </h2>
          <p className="text-muted-foreground-landing mt-4 max-w-2xl mx-auto">
            Choose the plan that fits your security needs. All plans include a 14-day free trial.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative glass-card rounded-2xl p-8 transition-all duration-300 hover:-translate-y-1 ${
                plan.highlighted
                  ? 'border-primary/60 shadow-[0_0_48px_-10px_hsl(var(--primary)/0.6)] scale-105'
                  : 'hover:border-secondary/40'
              }`}
            >
              {plan.highlighted && (
                <>
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-primary-foreground font-mono text-xs uppercase tracking-widest font-semibold rounded-full shadow-[0_0_24px_-4px_hsl(var(--primary))]">
                    Most Popular
                  </div>
                  <div className="pointer-events-none absolute inset-0 rounded-2xl border border-primary/30 animate-pulse-glow" />
                </>
              )}

              <div className="mb-6">
                <h3 className="font-display text-xl font-semibold mb-2">{plan.name}</h3>
                <div className="flex items-baseline gap-1">
                  <span className="font-display text-4xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground-landing font-mono text-sm">{plan.period}</span>
                </div>
                <p className="text-sm text-muted-foreground-landing mt-2">{plan.description}</p>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3">
                    <Check className="h-4 w-4 text-primary flex-shrink-0" />
                    <span className="text-sm text-muted-foreground-landing">{feature}</span>
                  </li>
                ))}
              </ul>

              <Link to="/register">
                <Button
                  className={`w-full font-mono text-xs uppercase tracking-widest ${
                    plan.highlighted
                      ? 'bg-primary hover:bg-primary-glow text-primary-foreground shadow-[0_0_24px_-4px_hsl(var(--primary)/0.6)]'
                      : 'bg-secondary/10 hover:bg-secondary/20 text-secondary border border-secondary/30'
                  }`}
                >
                  {plan.cta}
                </Button>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PricingSection;
