import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/card";
import { Button } from "@/ui/button";
import { Input } from "@/ui/input";
import { Label } from "@/ui/label";
import { Checkbox } from "@/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/ui/select";
import { Loader2, PlayCircle } from "lucide-react";
import type { AWSCredential } from "@/interfaces/environment";
import type { ScanMode } from "@/interfaces/scan";
import { useByok } from "@/hooks/useByok";

interface StartScanFormProps {
  credentials: AWSCredential[] | undefined;
  onStartScan: (environmentId: string, name: string, mode: ScanMode, modelId?: string) => void;
  isStarting: boolean;
}

export const StartScanForm = ({ credentials, onStartScan, isStarting }: StartScanFormProps) => {
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>("");
  const [scanName, setScanName] = useState<string>("");
  const [analysisMode, setAnalysisMode] = useState<boolean>(false);
  const [selectedModelId, setSelectedModelId] = useState<string>("");
  const { keys: byokKeys = [] } = useByok();

  const handleStartScan = () => {
    if (!selectedEnvironment || !scanName.trim()) return;
    onStartScan(selectedEnvironment, scanName, analysisMode ? "analysis" : "enumeration", selectedModelId || "default");
    setScanName("");
    setSelectedEnvironment("");
    setAnalysisMode(false);
    setSelectedModelId("");
  };

  const labelCls = "font-mono text-[10px] uppercase tracking-widest text-muted-foreground";
  const inputCls = "font-mono bg-card border-border text-foreground placeholder:text-muted-foreground focus-visible:ring-primary";

  return (
    <Card className="glass-card">
      <CardHeader className="pb-3">
        <CardTitle className="font-display">Start New Scan</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="scan-name" className={labelCls}>Scan name</Label>
            <Input
              id="scan-name"
              placeholder="prod_weekly_audit"
              value={scanName}
              onChange={(e) => setScanName(e.target.value)}
              className={inputCls}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="environment" className={labelCls}>Environment</Label>
            <Select value={selectedEnvironment} onValueChange={setSelectedEnvironment}>
              <SelectTrigger className={inputCls}>
                <SelectValue placeholder="Select environment" />
              </SelectTrigger>
              <SelectContent>
                {credentials?.map((credential) => (
                  <SelectItem key={credential.id} value={credential.id} className="font-mono">
                    {credential.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="model" className={labelCls}>Model</Label>
            <Select value={selectedModelId} onValueChange={setSelectedModelId}>
              <SelectTrigger className={inputCls}>
                <SelectValue placeholder={analysisMode ? "Select model for analysis" : "Optional: select model"} />
              </SelectTrigger>
              <SelectContent>
                {byokKeys && byokKeys.length > 0 ? (
                  byokKeys.map((k) => (
                    <SelectItem key={k.id} value={k.modelId} className="font-mono">
                      {k.label ? `${k.label} — ${k.model}` : `${k.provider} • ${k.model}`}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="__empty" disabled>
                    No saved models (add in BYOK)
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground font-mono">
              If no model is selected, the default model will be used.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 rounded-lg border border-border bg-card/40 px-4 py-3">
          <div className="flex items-start gap-3">
            <div className="pt-1">
              <Checkbox
                id="analysis-mode"
                checked={analysisMode}
                onCheckedChange={(checked) => setAnalysisMode(checked === true)}
                className="border-primary/50 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="analysis-mode" className="cursor-pointer text-sm font-medium">
                Run analysis mode
              </Label>
              <p className="text-xs text-muted-foreground font-mono">
                Enumeration + deep analysis. Unchecked = enumeration only.
              </p>
            </div>
          </div>
          <Button
            onClick={handleStartScan}
            disabled={!selectedEnvironment || !scanName.trim() || isStarting}
            className="ml-auto min-w-40 cursor-pointer bg-primary text-primary-foreground hover:bg-primary-glow font-mono text-xs uppercase tracking-widest shadow-[0_0_24px_-4px_hsl(var(--primary)/0.6)] disabled:pointer-events-auto disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground disabled:shadow-none"
          >
            {isStarting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting...
              </>
            ) : (
              <>
                <PlayCircle className="mr-2 h-4 w-4" />
                Start Scan ▶
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
