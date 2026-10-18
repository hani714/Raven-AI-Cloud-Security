import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/ui/card';
import type { ScanActivity as ScanActivityType } from '@/interfaces/dashboard';

interface ScanActivityProps {
  activity: ScanActivityType;
}

interface ActivityCardProps {
  label: string;
  current: number;
  total: number;
  progressColor: string;
}

const ActivityCard = ({ label, current, total, progressColor }: ActivityCardProps) => {
  const percentage = total > 0 ? (current / total) * 100 : 0;
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center p-6 rounded-lg border border-border bg-card/60 transition-colors hover:bg-card hover:border-primary/30">
      <h3 className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-foreground mb-4">
        {label}
      </h3>
      <div className="relative w-40 h-40">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="hsl(var(--muted))"
            strokeWidth="12"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke={progressColor}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
            style={{ filter: `drop-shadow(0 0 8px ${progressColor})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-mono text-4xl font-bold"
            style={{ color: progressColor, textShadow: `0 0 12px ${progressColor}` }}
          >
            {current}
          </span>
          <span className="font-mono text-sm text-muted-foreground">/ {total}</span>
        </div>
      </div>
    </div>
  );
};

export const ScanActivity = ({ activity }: ScanActivityProps) => {
  const activeScansTotal = Math.max(activity.max_scans_per_month, 1);
  const activeScansCurrent = Math.min(activity.current_scans_per_month, activeScansTotal);
  const envTotal = Math.max(activity.max_environments, 1);
  const envCurrent = Math.min(activity.current_environments, envTotal);
  const availableScanSlots = Math.max(activeScansTotal - activeScansCurrent, 0);
  const availableEnvSlots = Math.max(envTotal - envCurrent, 0);

  // High-usage gets crimson, healthy gets green
  const usageColor = (current: number, total: number) =>
    current / total > 0.75 ? 'hsl(var(--primary))' : 'hsl(var(--accent))';

  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle className="font-display">Scan Activity</CardTitle>
        <CardDescription className="text-muted-foreground">
          Current usage across environments and monthly scan quota ({activity.analysis_level} analysis)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <ActivityCard
            label="Active scans"
            current={activeScansCurrent}
            total={activeScansTotal}
            progressColor={usageColor(activeScansCurrent, activeScansTotal)}
          />
          <ActivityCard
            label="Environment usage"
            current={envCurrent}
            total={envTotal}
            progressColor={usageColor(envCurrent, envTotal)}
          />
          <ActivityCard
            label="Available scan slots"
            current={availableScanSlots}
            total={activeScansTotal}
            progressColor="hsl(var(--secondary))"
          />
          <ActivityCard
            label="Available env slots"
            current={availableEnvSlots}
            total={envTotal}
            progressColor="hsl(var(--secondary))"
          />
        </div>
      </CardContent>
    </Card>
  );
};
