import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/card";
import { Button } from "@/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/ui/tabs";
import { Loader2, ArrowLeft, Check, AlertTriangle, Terminal, Target } from "lucide-react";
import { useScanAnalysis } from "@/hooks/useScans";
import { Badge } from "@/ui/badge";

const AnalysisDetails = () => {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const { result, isLoading, error } = useScanAnalysis(scanId || "");

  const getSeverityClasses = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return "border-[#FF453A]/40 bg-[#FF453A]/10 text-[#FF453A]";
      case "high":
        return "border-[#E5173F]/40 bg-[#E5173F]/10 text-[#E5173F]";
      case "medium":
        return "border-[#F0A500]/40 bg-[#F0A500]/10 text-[#F0A500]";
      case "low":
        return "border-[#39D353]/40 bg-[#39D353]/10 text-[#39D353]";
      default:
        return "border-[#58A6FF]/40 bg-[#58A6FF]/10 text-[#58A6FF]";
    }
  };

  const glassCard = "border border-[#21262D] bg-[#0D1117]/80 backdrop-blur-xl shadow-[0_0_40px_-20px_rgba(229,23,63,0.25)]";
  const ravenCard = `${glassCard} border-l-2 border-l-[#E5173F]`;
  const mono = "font-mono";

  const renderTriage = (triage: any) => (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Badge variant="outline" className={`${mono} ${getSeverityClasses(triage.severity)}`}>
          {triage.severity?.toUpperCase()}
        </Badge>
        <span className={`text-sm text-[#7D8590] ${mono}`}>
          // requires_deep_analysis: <span className="text-[#E6EDF3]">{triage.requires_deep_analysis ? "yes" : "no"}</span>
        </span>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-[#E6EDF3]">
          <Target className="h-5 w-5 text-[#E5173F]" />
          Entry Points
        </h3>
        <div className="space-y-3">
          {triage.entry_points?.map((entry: any, idx: number) => (
            <Card key={idx} className={ravenCard}>
              <CardContent className="pt-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className={`${mono} border-[#21262D] text-[#7D8590]`}>Rank {entry.rank}</Badge>
                    <span className={`${mono} text-sm text-[#E5173F]`}>{entry.resource}</span>
                  </div>
                  <p className="text-sm text-[#E6EDF3]">{entry.risk}</p>
                  <Badge variant="outline" className={`${mono} text-xs border-[#21262D] text-[#7D8590]`}>
                    exploitability: <span className="text-[#F0A500] ml-1">{entry.exploitability}</span>
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Quick Wins</h3>
        <ul className="space-y-2">
          {triage.quick_wins?.map((win: string, idx: number) => (
            <li key={idx} className="flex items-start gap-2">
              <Check className="h-4 w-4 mt-1 text-[#39D353]" />
              <span className="text-sm text-[#E6EDF3]">{win}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );

  const renderAnalysis = (analysis: any) => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Attack Paths</h3>
        <div className="space-y-4">
          {analysis.attack_paths?.map((path: any) => (
            <Card key={path.path_id} className={ravenCard}>
              <CardHeader>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className={`${mono} border-[#21262D] text-[#7D8590]`}>Path {path.path_id}</Badge>
                    <Badge variant="outline" className={`${mono} ${getSeverityClasses(path.severity)}`}>
                      {path.severity}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg text-[#E6EDF3]">{path.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className={`${mono} text-xs uppercase tracking-widest text-[#E5173F] mb-2`}>// steps</h4>
                  <ol className="list-decimal list-inside space-y-1">
                    {path.steps?.map((step: string, idx: number) => (
                      <li key={idx} className="text-sm text-[#E6EDF3] ml-2">
                        {step}
                      </li>
                    ))}
                  </ol>
                </div>

                <div>
                  <h4 className={`${mono} text-xs uppercase tracking-widest text-[#E5173F] mb-2`}>// resources_involved</h4>
                  <div className="flex flex-wrap gap-2">
                    {path.resources_involved?.map((resource: string, idx: number) => (
                      <Badge key={idx} variant="outline" className={`${mono} text-xs border-[#21262D] bg-[#161B22] text-[#58A6FF]`}>
                        {resource}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className={`${mono} text-xs uppercase tracking-widest text-[#E5173F] mb-2`}>// impact</h4>
                  <p className="text-sm text-[#7D8590]">{path.impact}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {analysis.cross_service_risks && analysis.cross_service_risks.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Cross-Service Risks</h3>
          <div className="space-y-3">
            {analysis.cross_service_risks.map((risk: any, idx: number) => (
              <Card key={idx} className={glassCard}>
                <CardContent className="pt-4">
                  <Badge variant="outline" className={`${mono} mb-2 border-[#21262D] text-[#58A6FF]`}>{risk.chain}</Badge>
                  <p className="text-sm text-[#E6EDF3]">{risk.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Recommendations</h3>
          <ul className="space-y-2">
            {analysis.recommendations.map((rec: string, idx: number) => (
              <li key={idx} className="flex items-start gap-2">
                <Check className="h-4 w-4 mt-1 text-[#39D353]" />
                <span className="text-sm text-[#E6EDF3]">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderCommands = (commands: any) => (
    <div className="space-y-6">
      {commands.exploitation_commands?.map((exploit: any) => (
        <Card key={exploit.path_id} className={ravenCard}>
          <CardHeader>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="outline" className={`${mono} border-[#21262D] text-[#7D8590]`}>Path {exploit.path_id}</Badge>
              <CardTitle className="text-lg text-[#E6EDF3]">{exploit.path_title}</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {exploit.commands?.map((cmd: any, idx: number) => (
                <div key={idx} className="space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className={`${mono} border-[#21262D] text-[#7D8590]`}>Step {cmd.step}</Badge>
                    <span className="text-sm font-medium text-[#E6EDF3]">{cmd.description}</span>
                  </div>
                  <div className="rounded-lg border border-[#21262D] bg-[#010409] p-3">
                    <div className="flex items-start gap-2">
                      <Terminal className="h-4 w-4 mt-1 text-[#39D353]" />
                      <code className={`${mono} text-sm flex-1 text-[#39D353] break-all`}>$ {cmd.command}</code>
                    </div>
                  </div>
                  <p className={`${mono} text-xs text-[#7D8590]`}>
                    → expected: {cmd.expected_output}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}

      {commands.validation_commands && commands.validation_commands.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Validation Commands</h3>
          <div className="space-y-3">
            {commands.validation_commands.map((cmd: any, idx: number) => (
              <Card key={idx} className={glassCard}>
                <CardContent className="pt-4">
                  <p className="text-sm font-medium mb-2 text-[#E6EDF3]">{cmd.purpose}</p>
                  <div className="rounded-lg border border-[#21262D] bg-[#010409] p-3">
                    <code className={`${mono} text-sm text-[#58A6FF] break-all`}>$ {cmd.command}</code>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderRiskSummary = (summary: any) => (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Badge variant="outline" className={`${mono} ${getSeverityClasses(summary.overall_severity)}`}>
          {summary.overall_severity?.toUpperCase()}
        </Badge>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Risk Scores</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {Object.entries(summary.scores || {}).map(([key, value]: [string, any]) => (
            <Card key={key} className={glassCard}>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className={`${mono} text-3xl font-bold text-[#E5173F] drop-shadow-[0_0_12px_rgba(229,23,63,0.5)]`}>{value}</p>
                  <p className={`${mono} text-xs uppercase tracking-widest text-[#7D8590] mt-1`}>{key}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Findings</h3>
        <div className="space-y-3">
          {summary.findings?.map((finding: any, idx: number) => (
            <Card key={idx} className={ravenCard}>
              <CardContent className="pt-4">
                <div className="flex items-start justify-between mb-2 gap-2 flex-wrap">
                  <Badge variant="outline" className={`${mono} ${getSeverityClasses(finding.severity)}`}>
                    {finding.severity}
                  </Badge>
                  <span className={`${mono} text-xs text-[#7D8590]`}>
                    {finding.resource}
                  </span>
                </div>
                <p className="font-medium text-sm mb-1 text-[#E6EDF3]">{finding.type?.replace(/_/g, " ")}</p>
                <p className="text-sm text-[#7D8590] mb-1">{finding.detail}</p>
                <p className={`${mono} text-xs text-[#7D8590] italic`}>
                  // impact: {finding.impact}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {summary.metadata && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-[#E6EDF3]">Metadata</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(summary.metadata).map(([key, value]: [string, any]) => (
              <div key={key} className={`${glassCard} rounded-lg p-3 space-y-1`}>
                <p className={`${mono} text-[10px] uppercase tracking-widest text-[#E5173F]`}>
                  {key.replace(/_/g, " ")}
                </p>
                <p className={`${mono} text-sm text-[#E6EDF3] break-all`}>{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="relative min-h-screen bg-[#080A0F] text-[#E6EDF3] p-4 md:p-8 overflow-x-hidden">
      {/* Hex grid + glow background */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(229,23,63,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(229,23,63,0.6) 1px, transparent 1px)",
          backgroundSize: "44px 44px",
        }}
      />
      <div className="pointer-events-none absolute -top-32 -right-32 h-[480px] w-[480px] rounded-full bg-[#E5173F]/10 blur-3xl" />

      <div className="relative z-10 w-full space-y-8">
        <div className="flex items-start gap-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => navigate(`/scans/${scanId}`)}
            className="border-[#21262D] bg-[#0D1117] text-[#E6EDF3] hover:bg-[#161B22] hover:text-[#E5173F]"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="space-y-1">
            <p className={`${mono} text-[10px] uppercase tracking-[0.3em] text-[#E5173F]`}>// threat intel</p>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Security Analysis</h1>
            <div className="flex items-center gap-2">
              <span className={`${mono} text-xs text-[#7D8590]`}>scan_id:</span>
              <code className={`${mono} text-xs text-[#58A6FF] break-all`}>{scanId}</code>
            </div>
          </div>
        </div>

        <Card className={glassCard}>
          <CardHeader className="border-b border-[#21262D]">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-[#E6EDF3]">
                <AlertTriangle className="h-5 w-5 text-[#E5173F]" />
                Analysis Results
              </CardTitle>
              {result?.severity && (
                <Badge variant="outline" className={`${mono} ${getSeverityClasses(result.severity)}`}>
                  {result.severity.toUpperCase()}
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            {isLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-[#E5173F]" />
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-[#E6EDF3] mb-2">No analysis results found</p>
                <p className={`${mono} text-sm text-[#7D8590]`}>
                  // run a scan with analysis enabled to see results
                </p>
              </div>
            ) : result ? (
              <Tabs defaultValue="triage" className="w-full">
                <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 bg-[#161B22] border border-[#21262D] p-1">
                  <TabsTrigger
                    value="triage"
                    className={`${mono} text-xs uppercase tracking-wider data-[state=active]:bg-[#E5173F]/10 data-[state=active]:text-[#E5173F] data-[state=active]:shadow-[inset_0_-2px_0_0_#E5173F]`}
                  >
                    Triage
                  </TabsTrigger>
                  <TabsTrigger
                    value="analysis"
                    className={`${mono} text-xs uppercase tracking-wider data-[state=active]:bg-[#E5173F]/10 data-[state=active]:text-[#E5173F] data-[state=active]:shadow-[inset_0_-2px_0_0_#E5173F]`}
                  >
                    Analysis
                  </TabsTrigger>
                  <TabsTrigger
                    value="commands"
                    className={`${mono} text-xs uppercase tracking-wider data-[state=active]:bg-[#E5173F]/10 data-[state=active]:text-[#E5173F] data-[state=active]:shadow-[inset_0_-2px_0_0_#E5173F]`}
                  >
                    Commands
                  </TabsTrigger>
                  <TabsTrigger
                    value="risk-summary"
                    className={`${mono} text-xs uppercase tracking-wider data-[state=active]:bg-[#E5173F]/10 data-[state=active]:text-[#E5173F] data-[state=active]:shadow-[inset_0_-2px_0_0_#E5173F]`}
                  >
                    Risk Summary
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="triage" className="mt-6">
                  {result.triage ? renderTriage(result.triage) : (
                    <p className={`${mono} text-center text-[#7D8590] py-8`}>// no triage data available</p>
                  )}
                </TabsContent>

                <TabsContent value="analysis" className="mt-6">
                  {result.analysis ? renderAnalysis(result.analysis) : (
                    <p className={`${mono} text-center text-[#7D8590] py-8`}>// no analysis data available</p>
                  )}
                </TabsContent>

                <TabsContent value="commands" className="mt-6">
                  {result.commands ? renderCommands(result.commands) : (
                    <p className={`${mono} text-center text-[#7D8590] py-8`}>// no commands available</p>
                  )}
                </TabsContent>

                <TabsContent value="risk-summary" className="mt-6">
                  {result.risk_summary ? renderRiskSummary(result.risk_summary) : (
                    <p className={`${mono} text-center text-[#7D8590] py-8`}>// no risk summary available</p>
                  )}
                </TabsContent>
              </Tabs>
            ) : (
              <div className={`${mono} text-center py-8 text-[#7D8590]`}>
                // no analysis results available
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalysisDetails;
