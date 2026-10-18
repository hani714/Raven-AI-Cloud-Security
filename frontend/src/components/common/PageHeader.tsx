import type { LucideIcon } from 'lucide-react';

interface PageHeaderProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  actions?: React.ReactNode;
  label?: string;
}

/**
 * PageHeader with Raven aesthetic: mono uppercase eyebrow label,
 * display headline, optional icon with primary color, actions slot.
 */
export const PageHeader = ({
  icon: Icon,
  title,
  description,
  actions,
  label,
}: PageHeaderProps) => {
  return (
    <div className="mb-6 flex items-start justify-between gap-4">
      <div className="flex items-center gap-4">
        {Icon && (
          <div className="rounded-xl border border-primary/30 bg-primary/10 p-3 shadow-[0_0_24px_-8px_hsl(var(--primary)/0.5)]">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        )}
        <div>
          {label && (
            <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-primary text-[#E5173F] mb-1">
              // {label}
            </p>
          )}
          <h1 className="font-display text-3xl font-bold tracking-tight">{title}</h1>
          {description && (
            <p className="mt-1 text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
};
