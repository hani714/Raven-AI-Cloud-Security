import { Cloud, Scan, FileCheck, ArrowRight } from 'lucide-react';

const steps = [
  {
    icon: Cloud,
    title: 'Connect AWS Account',
    description: 'Securely link your AWS account using IAM roles with read-only access.',
    step: '01',
    glow: 'secondary',
    color: 'hsl(var(--secondary))',
  },
  {
    icon: Scan,
    title: 'Run Automated Pentest',
    description: 'Our engine scans your entire infrastructure for vulnerabilities and misconfigurations.',
    step: '02',
    glow: 'primary',
    color: 'hsl(var(--primary))',
  },
  {
    icon: FileCheck,
    title: 'Get Actionable Remediation',
    description: 'Receive detailed reports with prioritized fixes and one-click remediation steps.',
    step: '03',
    glow: 'accent',
    color: 'hsl(var(--accent))',
  },
] as const;

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-24 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card/30 to-background pointer-events-none" />

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <span className="font-mono text-primary text-xs font-semibold tracking-[0.3em] uppercase">// How It Works</span>
          <h2 className="text-3xl md:text-4xl font-bold mt-4 font-display">
            Three Steps to Complete AWS Security
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8 relative">
          <div className="hidden md:block absolute top-24 left-1/4 right-1/4 h-px bg-gradient-to-r from-secondary/50 via-primary/50 to-accent/50" />

          {steps.map((step, index) => (
            <div key={step.title} className="relative group">
              <div className="glass-card rounded-2xl p-8 h-full transition-all duration-300 hover:border-primary/50 hover:-translate-y-1 hover:shadow-[0_0_32px_-8px_hsl(var(--primary)/0.4)]">
                <div
                  className="absolute -top-4 left-8 h-8 w-8 flex items-center justify-center rounded-full font-mono text-sm font-bold border"
                  style={{ background: 'hsl(var(--card))', color: step.color, borderColor: step.color }}
                >
                  {step.step}
                </div>

                <div
                  className="mb-6 p-4 rounded-xl w-fit transition-all duration-300"
                  style={{
                    background: `${step.color.replace(')', ' / 0.1)')}`,
                    border: `1px solid ${step.color.replace(')', ' / 0.3)')}`,
                    boxShadow: `0 0 24px -8px ${step.color}`,
                  }}
                >
                  <step.icon className="h-8 w-8" style={{ color: step.color }} />
                </div>

                <h3 className="text-xl font-semibold mb-3 font-display">{step.title}</h3>
                <p className="text-muted-foreground-landing">{step.description}</p>

                {index < steps.length - 1 && (
                  <ArrowRight className="hidden md:block absolute top-24 -right-4 h-8 w-8 text-primary/40" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
