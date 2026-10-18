import { Github, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="relative border-t border-border-landing/50 bg-[#050709] overflow-hidden">
      {/* Raven watermark */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center opacity-[0.03]">
        <img src="/raven.png" alt="" className="h-[420px] w-[420px]" />
      </div>

      <div className="container mx-auto px-6 py-16 relative z-10">
        <div className="grid md:grid-cols-4 gap-12">
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-3">
              <img src="/raven.png" alt="Raven Logo" className="h-8 w-8 drop-shadow-[0_0_10px_hsl(var(--primary)/0.5)]" />
              <span className="font-display text-lg font-bold tracking-[0.3em]">RAVEN</span>
            </Link>
            <p className="text-sm text-muted-foreground-landing">
              Enterprise-grade AWS security testing platform. The last thing your vulnerabilities will ever see.
            </p>
          </div>

          <div>
            <h4 className="font-mono text-xs uppercase tracking-widest text-primary mb-4">// Product</h4>
            <ul className="space-y-3">
              {['Features', 'Pricing', 'Integrations', 'Changelog'].map((item) => (
                <li key={item}>
                  <a href="#" className="text-sm text-muted-foreground-landing hover:text-primary transition-colors">
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-mono text-xs uppercase tracking-widest text-primary mb-4">// Resources</h4>
            <ul className="space-y-3">
              {['Documentation', 'API Reference', 'Blog', 'Security'].map((item) => (
                <li key={item}>
                  <a href="#" className="text-sm text-muted-foreground-landing hover:text-primary transition-colors">
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-mono text-xs uppercase tracking-widest text-primary mb-4">// Company</h4>
            <ul className="space-y-3">
              <li>
                <Link to="/privacy-policy" className="text-sm text-muted-foreground-landing hover:text-primary transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms-of-service" className="text-sm text-muted-foreground-landing hover:text-primary transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/refund-policy" className="text-sm text-muted-foreground-landing hover:text-primary transition-colors">
                  Refund Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-border-landing/50 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-muted-foreground-landing font-mono uppercase tracking-wider">
            © {new Date().getFullYear()} Raven // AWS Pentest Toolkit
          </p>

          <div className="flex items-center gap-4">
            <a
              href="https://github.com/YarKhan02/AWSPentest"
              target="_blank"
              rel="noreferrer"
              className="p-2 text-muted-foreground-landing hover:text-primary transition-colors"
            >
              <Github className="h-5 w-5" />
            </a>
            <a href="#" className="p-2 text-muted-foreground-landing hover:text-primary transition-colors">
              <Mail className="h-5 w-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
