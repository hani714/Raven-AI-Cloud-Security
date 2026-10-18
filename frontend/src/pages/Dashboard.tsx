import { useDashboardData } from '@/hooks/useDashboardData';
import { LastPentestSession, SeverityBreakdown, ScanActivity } from '../components/dashboard';
import { ErrorState, LoadingState, PageHeader } from '@/components';

const Dashboard = () => {
  const { dashboardData, isLoading, isError, error, refetch } = useDashboardData();

  if (isLoading) return <LoadingState message="Loading dashboard..." />;

  if (isError) {
    return (
      <ErrorState
        title="Failed to Load Dashboard"
        message={error instanceof Error ? error.message : 'An unknown error occurred'}
        onRetry={refetch}
      />
    );
  }

  if (!dashboardData) return null;

  return (
    <div className="w-full h-full">
      <div className="px-8 py-6 space-y-6 min-h-full">
        <PageHeader
          label="pentest_dashboard"
          title="Pentest Dashboard"
          description="Monitor your security assessments and scan results"
        />

        <LastPentestSession session={dashboardData.lastSession} />
        <SeverityBreakdown trends={dashboardData.vulnerabilityTrends} />
        <ScanActivity activity={dashboardData.scanActivity} />
      </div>
    </div>
  );
};

export default Dashboard;
