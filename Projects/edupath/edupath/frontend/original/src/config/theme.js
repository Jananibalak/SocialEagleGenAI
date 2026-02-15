// 🎨 Modern Professional Theme - Clean & Minimal
export const theme = {
  colors: {
    // Primary Palette - Warm Gold & Deep Blues
    primary: '#f5cb7d',           // Warm gold (accent)
    primaryLight: '#f9d89c',      // Light gold
    primaryDark: '#d4af5e',       // Dark gold
    
    // Secondary Palette - Deep Blues
    secondary: '#2f4954',         // Medium blue
    secondaryDark: '#1f3e4e',     // Dark blue
    secondaryDeep: '#0e3248',     // Deepest blue (headers)
    
    // Neutral
    neutral: '#636e65',           // Sage gray
    neutralLight: '#8a9189',      // Light sage
    
    // Backgrounds
    background: '#f8f9fa',        // Light background
    backgroundSecondary: '#ffffff', // White
    backgroundDark: '#0e3248',    // Dark background
    chatBackground: '#f8f9fa',    // Chat area
    
    // Text
    text: '#1f3e4e',              // Primary text (dark blue)
    textSecondary: '#636e65',     // Secondary text (sage)
    textLight: '#8a9189',         // Light text
    textInverse: '#ffffff',       // White text
    
    // Message Bubbles
    userBubble: '#f5cb7d',        // Gold user bubble
    userBubbleText: '#1f3e4e',    // Dark text on gold
    aiBubble: '#ffffff',          // White AI bubble
    aiBubbleText: '#1f3e4e',      // Dark text
    
    // UI States
    success: '#10b981',           // Green
    error: '#ef4444',             // Red
    warning: '#f59e0b',           // Amber
    info: '#3b82f6',              // Blue
    
    // Borders & Dividers
    border: '#e5e7eb',            // Light gray
    borderDark: '#d1d5db',        // Medium gray
    divider: '#f3f4f6',           // Very light
    
    // Shadows
    shadow: 'rgba(31, 62, 78, 0.1)',
    shadowDark: 'rgba(14, 50, 72, 0.15)',
    
    // Overlays
    overlay: 'rgba(14, 50, 72, 0.8)',
  },
  
  fonts: {
    // Modern clean fonts
    primary: '"Inter", "SF Pro Display", -apple-system, system-ui, sans-serif',
    secondary: '"Poppins", "Helvetica Neue", sans-serif',
    
    sizes: {
      xs: 12,
      sm: 14,
      md: 16,
      lg: 18,
      xl: 24,
      xxl: 32,
      xxxl: 48,
    },
    
    weights: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    }
  },
  
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    xxxl: 64,
  },
  
  borderRadius: {
    none: 0,
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    xxl: 24,
    full: 9999,
  },
  
  shadows: {
    sm: {
      shadowColor: '#1f3e4e',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 2,
      elevation: 2,
    },
    md: {
      shadowColor: '#1f3e4e',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 4,
    },
    lg: {
      shadowColor: '#1f3e4e',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 8,
    },
    xl: {
      shadowColor: '#0e3248',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.2,
      shadowRadius: 16,
      elevation: 12,
    }
  },
  
  animations: {
    fast: 200,
    normal: 300,
    slow: 500,
  },
  
  // Responsive
  breakpoints: {
    mobile: 0,
    tablet: 768,
    desktop: 1024,
    wide: 1440,
  },
  
  maxWidths: {
    chat: 1000,
    form: 480,
    content: 1200,
  },
};

export default theme;