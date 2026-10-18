import { useState } from "react";
import { Button } from "@/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/ui/table";
import type { AWSCredential } from "@/interfaces/environment";
import { Eye, EyeOff, Trash2 } from "lucide-react";

interface CredentialsTableProps {
  credentials: AWSCredential[];
  onDelete: (id: string) => void;
  onTest: (id: string) => void;
  testingId: string | null;
}

export const CredentialsTable = ({
  credentials,
  onDelete,
  onTest,
  testingId,
}: CredentialsTableProps) => {
  const [visibleSecrets, setVisibleSecrets] = useState<Set<string>>(new Set());

  const toggleSecretVisibility = (id: string) => {
    setVisibleSecrets((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const maskSecret = (_s: string) => "●".repeat(32);

  return (
    <Table>
      <TableHeader>
        <TableRow className="border-b border-border hover:bg-transparent">
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Name</TableHead>
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Access Key</TableHead>
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Secret Key</TableHead>
          <TableHead className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Region</TableHead>
          <TableHead className="text-right font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {credentials?.map((credential, idx) => {
          const isRowTesting = testingId === credential.id;
          return (
            <TableRow
              key={credential.id}
              className="group relative border-b border-border/60 transition-colors hover:bg-primary/5"
              style={{ animation: `fadeUp 0.3s ease-out ${idx * 0.04}s both` }}
            >
              <TableCell className="relative font-medium">
                <span className="absolute left-0 top-1/2 h-6 w-[2px] -translate-y-1/2 -translate-x-2 bg-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                {credential.name}
              </TableCell>
              <TableCell className="font-mono text-sm text-foreground/90">
                {credential.accessKey}
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-foreground/90">
                    {visibleSecrets.has(credential.id)
                      ? credential.secretAccessKey
                      : maskSecret(credential.secretAccessKey)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-muted-foreground hover:text-primary hover:bg-primary/10"
                    onClick={() => toggleSecretVisibility(credential.id)}
                  >
                    {visibleSecrets.has(credential.id) ? (
                      <EyeOff className="h-3 w-3" />
                    ) : (
                      <Eye className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              </TableCell>
              <TableCell className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                {credential.region || "N/A"}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onTest(credential.id)}
                    disabled={isRowTesting}
                    className="cursor-pointer border-border font-mono text-xs uppercase tracking-wider hover:border-accent hover:text-accent hover:bg-accent/10 disabled:cursor-not-allowed"
                  >
                    {isRowTesting ? "Testing..." : "Test"}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(credential.id)}
                    className="group/del cursor-pointer text-muted-foreground hover:text-primary hover:bg-primary/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};
