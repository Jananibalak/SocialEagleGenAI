import React, { useEffect, useRef } from 'react';
import { Animated, View, StyleSheet, Dimensions } from 'react-native';
import theme from '../config/theme';

const { width } = Dimensions.get('window');

/**
 * PageTurnTransition - Creates a book page turning effect
 * 
 * Usage:
 * <PageTurnTransition show={isVisible}>
 *   <YourScreen />
 * </PageTurnTransition>
 */
const PageTurnTransition = ({ children, show = true, onComplete }) => {
  const rotateAnim = useRef(new Animated.Value(show ? 0 : 1)).current;
  const fadeAnim = useRef(new Animated.Value(show ? 1 : 0)).current;

  useEffect(() => {
    if (show) {
      // Page turn IN (from right to center)
      Animated.parallel([
        Animated.timing(rotateAnim, {
          toValue: 0,
          duration: theme.animations.pageTurn,
          useNativeDriver: true,
        }),
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: theme.animations.pageTurn * 0.6,
          delay: theme.animations.pageTurn * 0.3,
          useNativeDriver: true,
        }),
      ]).start(onComplete);
    } else {
      // Page turn OUT (from center to left)
      Animated.parallel([
        Animated.timing(rotateAnim, {
          toValue: 1,
          duration: theme.animations.pageTurn,
          useNativeDriver: true,
        }),
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: theme.animations.pageTurn * 0.4,
          useNativeDriver: true,
        }),
      ]).start(onComplete);
    }
  }, [show]);

  const rotateY = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '-90deg'],
  });

  const translateX = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -width / 2],
  });

  return (
    <Animated.View
      style={[
        styles.page,
        {
          opacity: fadeAnim,
          transform: [
            { perspective: 1200 },
            { rotateY },
            { translateX },
          ],
        },
      ]}
    >
      {/* Page shadow for depth */}
      <View style={styles.pageShadow} />
      {children}
    </Animated.View>
  );
};

/**
 * BookPageContainer - Wraps content in a book page with decorative elements
 */
export const BookPageContainer = ({ children, showOrnaments = true }) => {
  return (
    <View style={styles.bookContainer}>
      {/* Decorative ornaments */}
      {showOrnaments && (
        <>
          <View style={styles.ornamentTopLeft}>✦</View>
          <View style={styles.ornamentTopRight}>✦</View>
          <View style={styles.ornamentBottomLeft}>✦</View>
          <View style={styles.ornamentBottomRight}>✦</View>
        </>
      )}
      
      {/* Content */}
      {children}
    </View>
  );
};

/**
 * TextEtchingAnimation - Animates text appearing as if being written
 */
export const TextEtchingAnimation = ({ children, delay = 0, style }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(10)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: theme.animations.inkFade,
        delay,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: theme.animations.inkFade,
        delay,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  return (
    <Animated.View
      style={[
        {
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }],
        },
        style,
      ]}
    >
      {children}
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  page: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  pageShadow: {
    position: 'absolute',
    right: -10,
    top: 0,
    bottom: 0,
    width: 20,
    backgroundColor: 'transparent',
    shadowColor: '#000',
    shadowOffset: { width: -5, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  bookContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,
    borderWidth: 2,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.lg,
    margin: theme.spacing.md,
    padding: theme.spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 4, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  
  // Ornamental corners
  ornamentTopLeft: {
    position: 'absolute',
    top: 12,
    left: 12,
    fontSize: 20,
    color: theme.colors.goldLeaf,
    zIndex: 10,
  },
  ornamentTopRight: {
    position: 'absolute',
    top: 12,
    right: 12,
    fontSize: 20,
    color: theme.colors.goldLeaf,
    zIndex: 10,
  },
  ornamentBottomLeft: {
    position: 'absolute',
    bottom: 12,
    left: 12,
    fontSize: 20,
    color: theme.colors.goldLeaf,
    zIndex: 10,
  },
  ornamentBottomRight: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    fontSize: 20,
    color: theme.colors.goldLeaf,
    zIndex: 10,
  },
});

export default PageTurnTransition;
