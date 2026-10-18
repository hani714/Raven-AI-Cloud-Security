import { Copy, KeyRound, Trash2 } from "lucide-react";
import { Button } from "@/ui/button";
import { Badge } from "@/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/ui/table";
import { toast } from "@/hooks/use-toast";
import type { ByokKey, ByokProviderOption } from "@/interfaces/byok";

interface ByokKeysTableProps {
  keys: ByokKey[];
  onDelete: (id: string) => void;
  providers: ByokProviderOption[];
}

const relativeDate = (iso: string) => {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "—";
  const diff = Date.now() - then;
  const s = Math.floor(diff / 1000);
  if (s < 60) return "just now";
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} minute${m === 1 ? "" : "s"} ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} hour${h === 1 ? "" : "s"} ago`;
  const d = Math.floor(h / 24);
  if (d < 30) return `${d} day${d === 1 ? "" : "s"} ago`;
  const mo = Math.floor(d / 30);
  if (mo < 12) return `${mo} month${mo === 1 ? "" : "s"} ago`;
  const y = Math.floor(mo / 12);
  return `${y} year${y === 1 ? "" : "s"} ago`;
};

const maskedPreview = (preview: string) => {
  const last4 = (preview || "").slice(-4);
  return `••••••••${last4}`;
};

export const ByokKeysTable = ({ keys, onDelete, providers }: ByokKeysTableProps) => {
  const providerLabel = new Map(providers.map((p) => [p.value, p.label]));

  if (keys.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="rounded-xl border border-primary/30 bg-primary/10 p-4 shadow-[0_0_24px_-8px_hsl(var(--primary)/0.5)]">
          <KeyRound className="h-8 w-8 text-primary" />
        </div>
        <p className="mt-4 font-display text-lg">No API keys saved yet.</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Add your first key using the form above.
        </p>
      </div>
    );
  }

  const handleCopy = async (preview: string) => {
    try {
      await navigator.clipboard.writeText(maskedPreview(preview));
      toast({ title: "Copied!", description: "Masked preview copied to clipboard." });
    } catch {
      toast({ title: "Copy failed", variant: "destructive" });
    }
  };

  return (
    <Table>
      <TableHeader>
        <TableRow className="border-b border-border hover:bg-transparent">
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Provider</TableHead>
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Model</TableHead>
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Label</TableHead>
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Key</TableHead>
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Added</TableHead>
          <TableHead className="text-right font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {keys.map((k, idx) => (
          <TableRow
            key={k.id}
            className="group relative border-b border-border/60 transition-colors hover:bg-primary/5"
            style={{ animation: `fadeUp 0.3s ease-out ${idx * 0.04}s both` }}
          >
            <TableCell>
              <Badge variant="outline" className="border-primary/30 text-primary bg-primary/10">
                {providerLabel.get(k.provider) ?? k.provider}
              </Badge>
            </TableCell>
            <TableCell className="font-mono text-sm text-foreground/90">{k.model}</TableCell>
            <TableCell className={k.label ? "" : "text-muted-foreground"}>
              {k.label || "—"}
            </TableCell>
            <TableCell className="font-mono text-sm text-foreground/90">
              {maskedPreview(k.keyPreview)}
            </TableCell>
            <TableCell className="font-mono text-xs text-muted-foreground">
              {relativeDate(k.createdAt)}
            </TableCell>
            <TableCell className="text-right">
              <div className="flex justify-end gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleCopy(k.keyPreview)}
                  className="h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/10"
                  title="Copy masked preview"
                >
                  <Copy className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onDelete(k.id)}
                  className="h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/10"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
