import type { SeverityLevel } from '@/interfaces/dashboard';
import { componentStyles } from './theme';

/**
 * Severity Utilities
 * Reusable functions for handling security severity levels
 */
 
export const normalizeSeverity = (severity: string | null | undefined): SeverityLevel => {
  const normalized = String(severity ?? '').trim().toLowerCase();
  if (normalized === 'critical' || normalized === 'high' || normalized === 'medium' || normalized === 'low' || normalized === 'info') {
    return normalized;
  }
  return 'low';
};

export const getSeverityColor = (severity: string | null | undefined): string => {
  return componentStyles.badge[normalizeSeverity(severity)];
};

/**
 * Get severity order/priority (higher number = more severe)
 */
export const getSeverityPriority = (severity: SeverityLevel): number => {
  const priorities = {
    critical: 5,
    high: 4,
    medium: 3,
    low: 2,
    info: 1,
  };
  return priorities[severity];
};

/**
 * Get severity icon/emoji representation
 */
export const getSeverityIcon = (severity: SeverityLevel): string => {
  const icons = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🟢',
    info: '🔵',
  };
  return icons[severity];
};

/**
 * Sort items by severity (critical first)
 */
export const sortBySeverity = <T extends { severity: SeverityLevel }>(items: T[]): T[] => {
  return [...items].sort((a, b) => 
    getSeverityPriority(b.severity) - getSeverityPriority(a.severity)
  );
};

/**
 * Get severity label with proper capitalization
 */
export const getSeverityLabel = (severity: SeverityLevel): string => {
  return severity.charAt(0).toUpperCase() + severity.slice(1);
};

/**
 * Get all severity levels in priority order
 */
export const getAllSeverityLevels = (): SeverityLevel[] => {
  return ['critical', 'high', 'medium', 'low', 'info'];
};

/**
 * Check if severity is high priority (critical or high)
 */
export const isHighPriority = (severity: SeverityLevel): boolean => {
  return severity === 'critical' || severity === 'high';
};
