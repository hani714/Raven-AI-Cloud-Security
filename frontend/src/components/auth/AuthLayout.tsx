import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

interface AuthLayoutProps {
  title: string;
  subtitle?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}

/**
 * Raven-themed auth layout: dark void background, hex grid texture,
 * radar pulse, glass card with crimson accents.
 */
export const AuthLayout = ({ title, subtitle, children, footer }: AuthLayoutProps) => {
  return (
    <div className="relative flex min-h-screen w-full overflow-hidden bg-[#080A0F] text-[#E6EDF3]">
      {/* Background: hex grid + radial glow + scan line */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.06]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(229,23,63,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(229,23,63,0.6) 1px, transparent 1px)",
          backgroundSize: '44px 44px',
        }}
      />
      <div className="pointer-events-none absolute -top-32 -left-32 h-[480px] w-[480px] rounded-full bg-[#E5173F]/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 -right-32 h-[520px] w-[520px] rounded-full bg-[#58A6FF]/10 blur-3xl" />
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px animate-[scanline_6s_linear_infinite] bg-gradient-to-r from-transparent via-[#E5173F]/70 to-transparent" />

      {/* Left brand panel */}
      <aside className="relative z-10 hidden w-1/2 flex-col justify-between border-r border-[#21262D]/70 bg-gradient-to-br from-[#0D1117] to-[#080A0F] p-12 lg:flex">
        <Link to="/" className="flex items-center gap-3">
          <img src="/raven.png" alt="Raven" className="h-9 w-9 object-contain drop-shadow-[0_0_12px_rgba(229,23,63,0.55)]" />
          <span className="font-mono text-lg font-bold tracking-[0.25em] text-[#E6EDF3]">RAVEN</span>
        </Link>

        {/* Radar */}
        <div className="relative mx-auto flex h-[340px] w-[340px] items-center justify-center">
          <div className="absolute inset-0 rounded-full border border-[#E5173F]/30" />
          <div className="absolute inset-6 rounded-full border border-[#E5173F]/25 animate-ping [animation-duration:3s]" />
          <div className="absolute inset-14 rounded-full border border-[#58A6FF]/25 animate-ping [animation-duration:4s]" />
          <div className="absolute inset-24 rounded-full border border-[#39D353]/25 animate-ping [animation-duration:5s]" />
          <div className="absolute h-3 w-3 rounded-full bg-[#E5173F] shadow-[0_0_24px_6px_rgba(229,23,63,0.6)]" />
          <span className="absolute top-2 font-mono text-[10px] tracking-widest text-[#7D8590]">IAM</span>
          <span className="absolute bottom-2 font-mono text-[10px] tracking-widest text-[#7D8590]">S3</span>
          <span className="absolute left-2 font-mono text-[10px] tracking-widest text-[#7D8590]">EC2</span>
          <span className="absolute right-2 font-mono text-[10px] tracking-widest text-[#7D8590]">LAMBDA</span>
        </div>

        <div className="space-y-3">
          <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-[#E5173F]">// offensive_security</p>
          <h2 className="text-2xl font-semibold leading-tight text-[#E6EDF3]">
            Automated AWS Security Testing — <span className="text-[#E5173F]">Done Right.</span>
          </h2>
          <p className="text-sm text-[#7D8590]">
            Predatory precision. Controlled danger. The last thing your AWS vulnerabilities will ever see.
          </p>
          <div className="flex items-center gap-4 pt-2 font-mono text-[11px] text-[#7D8590]">
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#39D353] shadow-[0_0_8px_rgba(57,211,83,0.8)]" />
              SOC 2
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#39D353] shadow-[0_0_8px_rgba(57,211,83,0.8)]" />
              GDPR
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#39D353] shadow-[0_0_8px_rgba(57,211,83,0.8)]" />
              OWASP
            </span>
          </div>
        </div>
      </aside>

      {/* Right form panel */}
      <main className="relative z-10 flex w-full items-center justify-center p-6 lg:w-1/2">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <Link to="/" className="mb-8 flex items-center justify-center gap-3 lg:hidden">
            <img src="/raven.png" alt="Raven" className="h-9 w-9 object-contain" />
            <span className="font-mono text-lg font-bold tracking-[0.25em]">RAVEN</span>
          </Link>

          <div className="relative rounded-xl border border-[#21262D] bg-[#0D1117]/80 p-8 shadow-[0_0_60px_-15px_rgba(229,23,63,0.25)] backdrop-blur-xl">
            {/* corner accents */}
            <span className="absolute -top-px left-6 h-px w-12 bg-[#E5173F]" />
            <span className="absolute -bottom-px right-6 h-px w-12 bg-[#E5173F]" />

            <div className="mb-6 space-y-1.5 text-center">
              <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-[#E5173F]">// secure_access</p>
              <h1 className="text-2xl font-semibold tracking-tight text-[#E6EDF3]">{title}</h1>
              {subtitle && <p className="text-sm text-[#7D8590]">{subtitle}</p>}
            </div>

            {children}

            {footer && <div className="mt-6 text-center text-sm text-[#7D8590]">{footer}</div>}
          </div>

          <p className="mt-6 text-center font-mono text-[10px] uppercase tracking-[0.25em] text-[#7D8590]">
            raven // aws pentest platform
          </p>
        </div>
      </main>

      <style>{`
        @keyframes scanline {
          0% { transform: translateY(0); opacity: 0; }
          10% { opacity: 1; }
          100% { transform: translateY(100vh); opacity: 0; }
        }
      `}</style>
    </div>
  );
};

export default AuthLayout;
