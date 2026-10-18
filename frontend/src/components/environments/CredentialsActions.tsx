import { Button } from "@/ui/button";
import { Card } from "@/ui/card";
import { Plus, Upload } from "lucide-react";

interface CredentialsActionsProps {
  onAdd: () => void;
  onImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

export const CredentialsActions = ({ onAdd, onImport }: CredentialsActionsProps) => {
  return (
    <Card className="glass-card mb-6 p-4">
      <div className="flex gap-3">
        <Button
          onClick={onAdd}
          className="gap-2 cursor-pointer bg-primary text-primary-foreground hover:bg-primary-glow font-mono text-xs uppercase tracking-widest shadow-[0_0_24px_-4px_hsl(var(--primary)/0.6)]"
        >
          <Plus className="h-4 w-4" />
          Add Credentials
        </Button>
        <Button
          variant="outline"
          className="gap-2 border-secondary/40 text-secondary hover:bg-secondary/10 hover:text-secondary hover:border-secondary font-mono text-xs uppercase tracking-widest"
          asChild
        >
          <label htmlFor="import-file" className="cursor-pointer">
            <Upload className="h-4 w-4" />
            Import from File
            <input
              id="import-file"
              type="file"
              accept=".csv,.json"
              className="hidden"
              onChange={onImport}
            />
          </label>
        </Button>
      </div>
    </Card>
  );
};
