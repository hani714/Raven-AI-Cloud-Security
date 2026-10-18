import { useNavigate } from "react-router-dom";
import { useScans } from "@/hooks/useScans";
import { useEnvironments } from "@/hooks/useEnvironments";
import { StartScanForm } from "@/components/scans/StartScanForm";
import { ScanHistoryTable } from "@/components/scans/ScanHistoryTable";
import { PageHeader } from "@/components/common/PageHeader";
import type { ScanMode } from "@/interfaces/scan";

const Scans = () => {
  const navigate = useNavigate();
  const { scans, isLoading, startScan, isStarting } = useScans();
  const { credentials } = useEnvironments();

  const handleStartScan = (environmentId: string, scanName: string, mode: ScanMode, modelId?: string) => {
    startScan({ environmentId, scanName, mode, modelId });
  };

  const handleRowClick = (scanId: string) => {
    navigate(`/scans/${scanId}`);
  };

  return (
    <div className="min-h-screen bg-background p-6 md:p-8">
      <div className="w-full space-y-7">
        <PageHeader
          label="active_scans"
          title="Scans"
          description="Manage and view your security scans"
        />

        <StartScanForm
          credentials={credentials}
          onStartScan={handleStartScan}
          isStarting={isStarting}
        />

        <ScanHistoryTable
          scans={scans}
          isLoading={isLoading}
          onRowClick={handleRowClick}
        />
      </div>
    </div>
  );
};

export default Scans;
