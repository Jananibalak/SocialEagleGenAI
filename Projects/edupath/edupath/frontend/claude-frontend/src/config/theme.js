// Theme Configuration
export const theme = {
  colors: {
    primary: '#f5cb7d',
    secondary: '#2f4954',
    dark: '#1f3e4e',
    deepDark: '#0e3248',
    neutral: '#636e65',
    background: '#f8f9fa',
    white: '#ffffff',
    error: '#ef4444',
    success: '#22c55e',
    warning: '#f59e0b',
  },
  
  gradients: {
    primary: 'linear-gradient(135deg, #f5cb7d 0%, #e8b960 100%)',
    dark: 'linear-gradient(180deg, #0e3248 0%, #2f4954 100%)',
    darkReverse: 'linear-gradient(180deg, #2f4954 0%, #0e3248 100%)',
    subtle: 'linear-gradient(135deg, #f8f9fa 0%, #e5e7eb 100%)',
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    glow: '0 0 20px rgba(245, 203, 125, 0.4)',
    glowLarge: '0 0 40px rgba(245, 203, 125, 0.6)',
  },
  
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
  
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
  },
  
  breakpoints: {
    mobile: '0px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1440px',
  },
  
  typography: {
    fontFamily: {
      display: "'Poppins', -apple-system, BlinkMacSystemFont, sans-serif",
      body: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      mono: "'JetBrains Mono', 'Courier New', monospace",
    },
    fontSize: {
      xs: '12px',
      sm: '14px',
      base: '16px',
      lg: '18px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '30px',
      '4xl': '36px',
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
  },
  
  transitions: {
    fast: '150ms ease-in-out',
    base: '300ms ease-in-out',
    slow: '500ms ease-in-out',
  },
  
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060,
  },
};

// Responsive helpers
export const mediaQuery = {
  mobile: `@media (max-width: ${theme.breakpoints.tablet})`,
  tablet: `@media (min-width: ${theme.breakpoints.tablet}) and (max-width: ${theme.breakpoints.desktop})`,
  desktop: `@media (min-width: ${theme.breakpoints.desktop})`,
  wide: `@media (min-width: ${theme.breakpoints.wide})`,
};

export default theme;
