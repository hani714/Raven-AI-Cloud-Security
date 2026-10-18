import { Button } from '@/ui/button';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border-landing/50 bg-background/70 backdrop-blur-xl">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <img
                src="/raven.png"
                alt="Raven Logo"
                className="h-8 w-8 transition-all duration-300 group-hover:scale-110 drop-shadow-[0_0_10px_hsl(var(--primary)/0.5)]"
              />
              <div className="absolute inset-0 bg-primary-landing/20 blur-xl rounded-full animate-pulse-glow" />
            </div>
            <span className="font-display text-lg font-bold tracking-[0.3em] text-foreground">
              RAVEN
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8 font-mono text-xs uppercase tracking-wider">
            <a href="#features" className="text-muted-foreground-landing hover:text-primary-landing transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-muted-foreground-landing hover:text-primary-landing transition-colors">
              How It Works
            </a>
            <a href="#pricing" className="text-muted-foreground-landing hover:text-primary-landing transition-colors">
              Pricing
            </a>
            <a href="#faq" className="text-muted-foreground-landing hover:text-primary-landing transition-colors">
              FAQ
            </a>
          </div>

          <div className="flex items-center gap-3">
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="cursor-pointer text-muted-foreground-landing hover:bg-accent-landing/10 hover:text-foreground font-mono uppercase tracking-wider text-xs"
            >
              <Link to="/login">Sign In</Link>
            </Button>
            <Button
              asChild
              size="sm"
              className="cursor-pointer bg-primary text-primary-foreground hover:bg-primary-glow font-mono uppercase tracking-wider text-xs shadow-[0_0_24px_-4px_hsl(var(--primary)/0.7)]"
            >
              <Link to="/dashboard">Get Started →</Link>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
