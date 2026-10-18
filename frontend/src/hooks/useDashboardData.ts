import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/services/api/dashboardApi';

/**
 * Custom hook for dashboard data management
 * Handles fetching, caching, and mutations of dashboard data
 */
export const useDashboardData = () => {
  const {
    data: dashboardData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.getDashboardData,
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: 2,
  });

  return {
    dashboardData,
    isLoading,
    isError,
    error,
    refetch,
  };
};
