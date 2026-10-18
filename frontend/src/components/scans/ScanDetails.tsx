import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/card";
import { Button } from "@/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/ui/tabs";
import { Loader2, ArrowLeft, Brain, Terminal } from "lucide-react";
import { useScanResult } from "@/hooks/useScans";

const ScanDetails = () => {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const { result, isLoading } = useScanResult(scanId || "");

  const mono = "font-mono";

  const formatTabName = (key: string) =>
    key.split("_").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="w-full space-y-8">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => navigate("/scans")}
            className="border-border hover:border-primary/40 hover:text-primary hover:bg-primary/10"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <p className={`${mono} text-[10px] uppercase tracking-[0.3em] text-[#E5173F]`}>// security analysis</p>
            <h1 className="font-display text-4xl font-bold mb-2">Scan Details</h1>
            <div className="flex items-center gap-2">
              <span className={`${mono} text-xs text-[#7D8590]`}>scan_id:</span>
              <code className={`${mono} text-xs text-[#58A6FF] break-all`}>{scanId}</code>
            </div>
          </div>
        </div>

        <Card className="glass-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="font-display flex items-center gap-2">
                <Terminal className="h-5 w-5 text-primary" />
                Scan Results
              </CardTitle>
              <Button
                onClick={() => navigate(`/scans/${scanId}/analysis`)}
                className="flex items-center gap-2 cursor-pointer bg-primary text-primary-foreground hover:bg-primary-glow font-mono text-xs uppercase tracking-widest shadow-[0_0_24px_-4px_hsl(var(--primary)/0.6)]"
              >
                <Brain className="h-4 w-4" />
                View Analysis
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : result ? (
              <Tabs defaultValue={Object.keys(result)[0]} className="w-full">
                <TabsList className="w-full justify-start overflow-x-auto bg-transparent border-b border-border h-auto p-0 rounded-none">
                  {Object.keys(result).map((key) => (
                    <TabsTrigger
                      key={key}
                      value={key}
                      className="font-mono text-xs uppercase tracking-wider data-[state=active]:bg-transparent data-[state=active]:text-primary data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none border-b-2 border-transparent px-4 py-3"
                    >
                      {formatTabName(key)}
                    </TabsTrigger>
                  ))}
                </TabsList>
                {Object.entries(result).map(([key, value]) => (
                  <TabsContent key={key} value={key} className="mt-4">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="font-display text-lg font-semibold">{formatTabName(key)}</h3>
                        <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                          {Array.isArray(value) ? `${value.length} items` : "N/A"}
                        </span>
                      </div>
                      <pre className="json-terminal p-4 overflow-auto max-h-[600px]">
                        {JSON.stringify(value, null, 2)}
                      </pre>
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            ) : (
              <div className="text-center py-8 text-muted-foreground font-mono text-xs uppercase tracking-wider">
                No scan results available
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ScanDetails;
