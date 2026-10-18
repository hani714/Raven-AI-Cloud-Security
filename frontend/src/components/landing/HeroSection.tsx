import { Button } from '@/ui/button';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden">
      {/* Background: hex grid + glows */}
      <div className="absolute inset-0 hex-grid-bg pointer-events-none opacity-60" />
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[480px] h-[480px] bg-primary/15 rounded-full blur-[120px] animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-1/4 w-[480px] h-[480px] bg-secondary/12 rounded-full blur-[120px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_transparent_0%,hsl(var(--background))_85%)]" />
      </div>
      {/* Sonar scan line */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/70 to-transparent" style={{ animation: 'scanY 8s linear infinite' }} />

      <div className="container mx-auto px-6 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left content */}
          <div className="space-y-8">
            <div className="animate-fade-up">
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-primary/30 bg-primary/5 font-mono text-[11px] uppercase tracking-[0.25em] text-primary">
                <span className="h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_8px_hsl(var(--primary))]" />
                Enterprise AWS Security
              </span>
            </div>

            <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold leading-tight tracking-tight animate-fade-up-delay-1">
              Automated AWS Security Testing —{' '}
              <span className="glitch-text text-primary" data-text="Done Right.">Done Right.</span>
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground-landing max-w-xl animate-fade-up-delay-2">
              Run guided pentests, detect misconfigurations, and secure your entire AWS cloud in minutes.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 animate-fade-up-delay-3">
              <Button
                asChild
                size="lg"
                className="group w-full cursor-pointer bg-primary text-primary-foreground hover:bg-primary-glow font-mono uppercase tracking-wider text-xs shadow-[0_0_32px_-4px_hsl(var(--primary)/0.7)] sm:w-auto"
              >
                <Link to="/scans">
                  Start Free Scan
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="w-full cursor-pointer border-secondary/50 bg-transparent text-secondary hover:border-secondary hover:bg-secondary/10 hover:text-secondary font-mono uppercase tracking-wider text-xs sm:w-auto"
              >
                <a href="#features">View Documentation</a>
              </Button>
            </div>

            <div className="flex items-center gap-6 pt-4 animate-fade-up-delay-3 font-mono text-xs">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[hsl(var(--status-success))] shadow-[0_0_8px_hsl(var(--status-success))]" />
                <span className="text-muted-foreground-landing uppercase tracking-wider">SOC 2 Compliant</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[hsl(var(--status-success))] shadow-[0_0_8px_hsl(var(--status-success))]" />
                <span className="text-muted-foreground-landing uppercase tracking-wider">GDPR Ready</span>
              </div>
            </div>
          </div>

          {/* Right radar visual */}
          <div className="relative hidden lg:flex items-center justify-center">
            <div className="relative w-full max-w-lg aspect-square">
              {/* Concentric rings - radar pulse */}
              <div className="absolute inset-0 rounded-full border border-primary/25 animate-radar-ping" />
              <div className="absolute inset-12 rounded-full border border-secondary/30 animate-radar-ping" style={{ animationDelay: '0.8s' }} />
              <div className="absolute inset-24 rounded-full border border-accent/30 animate-radar-ping" style={{ animationDelay: '1.6s' }} />

              {/* Static rings */}
              <div className="absolute inset-0 rounded-full border border-primary/15" />
              <div className="absolute inset-12 rounded-full border border-secondary/15" />
              <div className="absolute inset-24 rounded-full border border-accent/15" />

              {/* Center */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-primary/30 blur-2xl rounded-full" />
                  <div className="relative p-8 rounded-full bg-card-landing border border-primary/30 glow-red">
                    <img src="/raven.png" alt="Raven" className="h-24 w-24" />
                  </div>
                </div>
              </div>

              {/* AWS service labels on cardinal points */}
              <div className="absolute top-2 left-1/2 -translate-x-1/2 font-mono text-xs tracking-widest text-secondary px-3 py-1 rounded-full border border-secondary/40 bg-card-landing/80 backdrop-blur">IAM</div>
              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 font-mono text-xs tracking-widest text-[hsl(var(--severity-high))] px-3 py-1 rounded-full border border-[hsl(var(--severity-high))]/40 bg-card-landing/80 backdrop-blur">S3</div>
              <div className="absolute top-1/2 -translate-y-1/2 left-2 font-mono text-xs tracking-widest text-accent px-3 py-1 rounded-full border border-accent/40 bg-card-landing/80 backdrop-blur">EC2</div>
              <div className="absolute top-1/2 -translate-y-1/2 right-2 font-mono text-xs tracking-widest text-primary px-3 py-1 rounded-full border border-primary/40 bg-card-landing/80 backdrop-blur">LAMBDA</div>

              {/* Scan sweep */}
              <div className="absolute inset-0 overflow-hidden rounded-full">
                <div className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary to-transparent animate-scan opacity-60" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
