/**
 * Raven Theme Configuration
 */

export const ravenTheme = {
  // Color palette in HSL format (Hue, Saturation, Lightness)
  colors: {
    // Main theme colors
    background: '240 10% 5%',        // Deep space black
    foreground: '210 40% 98%',        // Near white text
    card: '240 10% 8%',               // Elevated dark surfaces
    cardForeground: '210 40% 98%',
    popover: '240 10% 10%',           // Slightly lighter than cards
    popoverForeground: '210 40% 98%',
    primary: '271 91% 65%',           // Electric Purple (Raven's intelligence)
    primaryForeground: '240 10% 5%',
    secondary: '199 89% 48%',         // Cyber Blue (AWS/Cloud)
    secondaryForeground: '0 0% 100%',
    accent: '142 71% 45%',            // Neon Green (Active scans)
    accentForeground: '0 0% 100%',
    muted: '240 10% 15%',             // Subdued backgrounds
    mutedForeground: '215 20% 65%',
    destructive: '0 63% 31%',         // Critical alerts
    destructiveForeground: '0 0% 100%',
    border: '240 10% 18%',            // Subtle purple-tinted borders
    input: '240 10% 18%',
    ring: '271 91% 65%',              // Focus ring
    
    // Security severity colors (same for both modes)
    severity: {
      critical: '348 83% 47%',
      criticalForeground: '0 0% 100%',
      high: '24 95% 53%',
      highForeground: '0 0% 100%',
      medium: '45 93% 47%',
      mediumForeground: '0 0% 100%',
      low: '142 71% 45%',
      lowForeground: '0 0% 100%',
      info: '199 89% 48%',
      infoForeground: '0 0% 100%',
    },
    
    // Raven brand colors
    brand: {
      purple: '271 91% 65%',
      purpleDark: '271 91% 45%',
      cyberBlue: '199 89% 48%',
      neonGreen: '142 71% 45%',
      warning: '45 93% 47%',
    },
  },
  
  // Border radius values
  radius: {
    default: '0.75rem',
    lg: 'var(--radius)',
    md: 'calc(var(--radius) - 2px)',
    sm: 'calc(var(--radius) - 4px)',
  },
  
  // Spacing system
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  
  // Typography
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
  },
  
  // Animation durations
  animation: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },
  
  // Shadow effects
  shadows: {
    glow: {
      sm: '0 0 10px hsl(271 91% 65% / 0.2)',
      md: '0 0 20px hsl(271 91% 65% / 0.3)',
      lg: '0 0 40px hsl(271 91% 65% / 0.4)',
      cyber: '0 0 30px hsl(271 91% 65% / 0.5), 0 0 60px hsl(199 89% 48% / 0.3)',
    },
  },
} as const;

// Helper function to get CSS variable format
export const getCSSVariable = (value: string) => `hsl(${value})`;

// Type-safe color getter
export const getThemeColor = (colorPath: string): string => {
  const [category, color] = colorPath.split('.');
  
  if (category === 'severity') {
    return ravenTheme.colors.severity[color as keyof typeof ravenTheme.colors.severity];
  }
  
  if (category === 'brand') {
    return ravenTheme.colors.brand[color as keyof typeof ravenTheme.colors.brand];
  }
  
  // Return base color (skip nested objects)
  const value = ravenTheme.colors[color as keyof typeof ravenTheme.colors];
  return typeof value === 'string' ? value : '';
};

// Predefined component styles
export const componentStyles = {
  // Card variants
  card: {
    default: 'bg-card text-card-foreground border border-border rounded-lg',
    glass: 'bg-card/80 backdrop-blur-md border border-border rounded-lg',
    glow: 'bg-card border border-primary/50 rounded-lg shadow-glow',
  },
  
  // Button variants
  button: {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/90',
    accent: 'bg-accent text-accent-foreground hover:bg-accent/90',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
  },
  
  // Badge variants
  badge: {
    critical: 'bg-severity-critical text-severity-critical-foreground',
    high: 'bg-severity-high text-severity-high-foreground',
    medium: 'bg-severity-medium text-severity-medium-foreground',
    low: 'bg-severity-low text-severity-low-foreground',
    info: 'bg-severity-info text-severity-info-foreground',
  },
  
  // Status indicators
  status: {
    active: 'bg-accent animate-pulse',
    success: 'bg-severity-low',
    warning: 'bg-severity-medium',
    error: 'bg-severity-critical animate-pulse',
  },
} as const;

// Export type for TypeScript autocomplete
export type RavenTheme = typeof ravenTheme;
export type ComponentStyles = typeof componentStyles;
