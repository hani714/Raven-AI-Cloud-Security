import { ravenTheme, getThemeColor, componentStyles } from '@/lib/theme';

/**
 * Custom hook to access Raven theme
**/
export const useRavenTheme = () => {
  return {
    // Theme configuration
    theme: ravenTheme,
    colors: ravenTheme.colors,
    severityColors: ravenTheme.colors.severity,
    brandColors: ravenTheme.colors.brand,
    
    // Component styles
    styles: componentStyles,
    
    // Helper functions
    getColor: (colorPath: string) => getThemeColor(colorPath),
    getCSSVar: (varName: string) => `hsl(var(--${varName}))`,
    
    // Utility classes
    classes: {
      glass: 'bg-card/80 backdrop-blur-md border border-border',
      glow: 'shadow-glow',
      cyberGlow: 'shadow-cyber',
      scanPulse: 'animate-pulse-glow',
      terminal: 'font-mono text-sm',
    },
  };
};
