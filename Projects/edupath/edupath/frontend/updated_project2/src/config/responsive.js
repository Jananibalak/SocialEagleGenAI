import { Dimensions, Platform } from 'react-native';
import theme from './theme';

const { width, height } = Dimensions.get('window');

export const isWeb = Platform.OS === 'web';
export const isMobile = width < theme.breakpoints.tablet;
export const isTablet = width >= theme.breakpoints.tablet && width < theme.breakpoints.desktop;
export const isDesktop = width >= theme.breakpoints.desktop;

export const getResponsiveValue = (mobile, tablet, desktop) => {
  if (isDesktop && desktop !== undefined) return desktop;
  if (isTablet && tablet !== undefined) return tablet;
  return mobile;
};

export const getResponsivePadding = () => {
  return getResponsiveValue(
    theme.spacing.md,
    theme.spacing.lg,
    theme.spacing.xl
  );
};

export const getMaxWidth = (type = 'content') => {
  if (!isWeb) return '100%';
  return theme.maxWidths[type] || theme.maxWidths.content;
};

export const responsiveStyles = {
  container: {
    width: '100%',
    maxWidth: isWeb ? theme.maxWidths.content : '100%',
    alignSelf: 'center',
  },
  chatContainer: {
    width: '100%',
    maxWidth: isWeb ? theme.maxWidths.chat : '100%',
    alignSelf: 'center',
  },
  formContainer: {
    width: '100%',
    maxWidth: isWeb ? theme.maxWidths.form : '100%',
    alignSelf: 'center',
  },
};