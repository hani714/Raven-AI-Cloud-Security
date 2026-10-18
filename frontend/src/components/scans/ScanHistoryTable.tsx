import { Card, CardContent, CardHeader, CardTitle } from "@/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/ui/table";
import { Loader2 } from "lucide-react";
import type { Scan } from "@/interfaces/scan";

interface ScanHistoryTableProps {
  scans: Scan[] | undefined;
  isLoading: boolean;
  onRowClick: (scanId: string) => void;
}

const formatMode = (mode: Scan["mode"] | undefined): string => {
  if (mode === "analysis") return "Enum + analysis";
  return "Enumeration only";
};

const getStatusChip = (status: string) => {
  const config: Record<string, { cls: string; pulse: boolean }> = {
    completed: { cls: "bg-[hsl(var(--severity-low))]/15 text-[hsl(var(--severity-low))] border border-[hsl(var(--severity-low))]/40", pulse: false },
    running: { cls: "bg-[hsl(var(--severity-high))]/15 text-[hsl(var(--severity-high))] border border-[hsl(var(--severity-high))]/40", pulse: true },
    failed: { cls: "bg-[hsl(var(--severity-critical))]/15 text-[hsl(var(--severity-critical))] border border-[hsl(var(--severity-critical))]/40", pulse: false },
  };
  const entry = config[status] || { cls: "bg-muted text-foreground", pulse: false };
  const label = status.charAt(0).toUpperCase() + status.slice(1);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest font-semibold ${entry.cls}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full bg-current ${entry.pulse ? 'animate-ping' : ''}`} />
      <span className="-ml-3 h-1.5 w-1.5 rounded-full bg-current" />
      {label}
    </span>
  );
};

const formatDateCell = (value?: string) => {
  if (!value) return <span className="text-muted-foreground font-mono">-</span>;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return <span className="text-muted-foreground font-mono">-</span>;

  const day = date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  const time = date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", hour12: false });

  return (
    <div className="font-mono text-xs leading-tight">
      <div>{day}</div>
      <div className="text-muted-foreground">{time}</div>
    </div>
  );
};

export const ScanHistoryTable = ({ scans, isLoading, onRowClick }: ScanHistoryTableProps) => {
  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle className="font-display">Scan History</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="border-b border-border hover:bg-transparent">
                <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Scan name</TableHead>
                <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Environment</TableHead>
                <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Mode</TableHead>
                <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Status</TableHead>
                <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Created</TableHead>
                <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Completed</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {scans && scans.length > 0 ? (
                scans.map((scan, idx) => (
                  <TableRow
                    key={scan.id}
                    onClick={() => onRowClick(scan.id)}
                    className="group cursor-pointer border-b border-border/60 transition-colors hover:bg-primary/5 relative"
                    style={{ animation: `fadeUp 0.3s ease-out ${idx * 0.04}s both` }}
                  >
                    <TableCell className="relative font-medium">
                      <span className="absolute left-0 top-1/2 h-6 w-[2px] -translate-y-1/2 -translate-x-2 bg-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                      {scan.scanName}
                    </TableCell>
                    <TableCell>
                      <span className="inline-flex rounded-full bg-secondary/15 border border-secondary/30 text-secondary px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-wider">
                        {scan.environmentName}
                      </span>
                    </TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground max-w-[150px] whitespace-normal leading-tight">
                      {formatMode(scan.mode)}
                    </TableCell>
                    <TableCell>{getStatusChip(scan.status)}</TableCell>
                    <TableCell>{formatDateCell(scan.createdAt)}</TableCell>
                    <TableCell>{formatDateCell(scan.completedAt)}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow className="border-b-0">
                  <TableCell colSpan={6} className="py-8 text-center text-muted-foreground font-mono text-xs uppercase tracking-wider">
                    No scans yet. Start your first scan above.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};
