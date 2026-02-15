import React, { useEffect, useRef } from 'react';
import { animations } from '../utils/animations';
import theme from '../config/theme';

const LoadingSpinner = ({ size = 40, color = theme.colors.primary, fullScreen = false }) => {
  const spinnerRef = useRef(null);

  useEffect(() => {
    if (spinnerRef.current) {
      animations.spin(spinnerRef.current);
    }
  }, []);

  const spinnerStyle = {
    width: size,
    height: size,
    border: `4px solid ${theme.colors.background}`,
    borderTop: `4px solid ${color}`,
    borderRadius: '50%',
  };

  if (fullScreen) {
    return (
      <div style={styles.fullScreenContainer}>
        <div ref={spinnerRef} style={spinnerStyle} />
      </div>
    );
  }

  return <div ref={spinnerRef} style={spinnerStyle} />;
};

const styles = {
  fullScreenContainer: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    zIndex: theme.zIndex.modal,
  },
};

export default LoadingSpinner;
