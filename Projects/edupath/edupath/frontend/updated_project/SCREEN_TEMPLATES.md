# Screen Templates for Remaining Updates

## Quick Reference for Modernizing Remaining Screens

### Standard Imports
```javascript
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Pressable,
  StyleSheet,
  Platform,
  ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather, Ionicons } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  FadeInUp,
  FadeInRight,
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withSequence,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import Colors from '../constants/colors';
```

### ChatScreen Updates Needed

1. **Gradient Send Button**
```javascript
<Pressable onPress={handleSend} style={styles.sendButton}>
  <LinearGradient
    colors={[Colors.accent, Colors.accentDark]}
    style={styles.sendButtonGradient}
  >
    <Feather name="send" size={18} color={Colors.primaryDark} />
  </LinearGradient>
</Pressable>
```

2. **Message Bubbles with Animation**
```javascript
<Animated.View 
  entering={FadeInDown.delay(index * 50).duration(300)}
  style={[
    styles.messageBubble,
    isUser ? styles.userBubble : styles.aiBubble
  ]}
>
  <Text style={styles.messageText}>{message.text}</Text>
</Animated.View>
```

3. **Gradient User Bubbles**
```javascript
userBubble: {
  background: 'linear-gradient' // Use LinearGradient component
  colors={[Colors.accent, Colors.accentDark]}
}
```

### CreateMentorScreen Updates Needed

1. **Icon Selector with Gradients**
```javascript
const iconOptions = [
  'book-open', 'cpu', 'code', 'globe', 'layers',
  'terminal', 'zap', 'award', 'compass', 'feather'
];

{iconOptions.map((icon, index) => (
  <Pressable
    key={icon}
    onPress={() => {
      setSelectedIcon(icon);
      if (Platform.OS !== 'web') 
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }}
    style={[
      styles.iconOption,
      selectedIcon === icon && styles.iconOptionSelected
    ]}
  >
    <LinearGradient
      colors={selectedIcon === icon 
        ? [Colors.accent, Colors.accentDark]
        : ['rgba(255,255,255,0.04)', 'rgba(255,255,255,0.04)']
      }
      style={styles.iconGradient}
    >
      <Feather name={icon} size={24} color={
        selectedIcon === icon ? Colors.primaryDark : Colors.white
      } />
    </LinearGradient>
  </Pressable>
))}
```

2. **Animated Processing Steps**
```javascript
const ProcessingStep = ({ label, completed }) => {
  const checkScale = useSharedValue(0);
  
  useEffect(() => {
    if (completed) {
      checkScale.value = withSpring(1, { damping: 8 });
    }
  }, [completed]);
  
  const checkStyle = useAnimatedStyle(() => ({
    transform: [{ scale: checkScale.value }],
  }));
  
  return (
    <View style={styles.processStep}>
      <Animated.View style={[styles.processCheck, checkStyle]}>
        {completed ? (
          <Feather name="check-circle" size={20} color={Colors.success} />
        ) : (
          <ActivityIndicator size="small" color={Colors.accent} />
        )}
      </Animated.View>
      <Text style={styles.processLabel}>{label}</Text>
    </View>
  );
};
```

### ProfileScreen Updates Needed

1. **Gradient Avatar**
```javascript
<LinearGradient
  colors={[Colors.accent, Colors.accentDark]}
  style={styles.profileAvatar}
>
  <Feather name="user" size={48} color={Colors.primaryDark} />
</LinearGradient>
```

2. **Stats Cards with Animation**
```javascript
const stats = [
  { label: 'Mentors', value: mentorCount, icon: 'users' },
  { label: 'Scrolls', value: scrollCount, icon: 'message-circle' },
  { label: 'Streak', value: streakDays, icon: 'zap' },
];

{stats.map((stat, index) => (
  <Animated.View
    entering={FadeInDown.delay(index * 100).duration(500)}
    key={stat.label}
    style={styles.statCard}
  >
    <LinearGradient
      colors={['rgba(255,255,255,0.06)', 'rgba(255,255,255,0.04)']}
      style={styles.statGradient}
    >
      <Feather name={stat.icon} size={20} color={Colors.accent} />
      <Text style={styles.statValue}>{stat.value}</Text>
      <Text style={styles.statLabel}>{stat.label}</Text>
    </LinearGradient>
  </Animated.View>
))}
```

### PlansScreen Updates Needed

1. **Plan Cards with Gradient Borders**
```javascript
{plans.map((plan, index) => (
  <Animated.View
    entering={FadeInRight.delay(index * 150).duration(600)}
    key={plan.id}
    style={styles.planCardContainer}
  >
    <LinearGradient
      colors={plan.isPopular 
        ? [Colors.accent, Colors.accentDark]
        : ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.1)']
      }
      style={styles.planBorder}
    >
      <View style={styles.planCard}>
        {plan.isPopular && (
          <View style={styles.popularBadge}>
            <Text style={styles.popularText}>POPULAR</Text>
          </View>
        )}
        <Text style={styles.planName}>{plan.name}</Text>
        <Text style={styles.planPrice}>{plan.price}</Text>
        <View style={styles.planFeatures}>
          {plan.features.map((feature, i) => (
            <View key={i} style={styles.feature}>
              <Feather name="check" size={16} color={Colors.success} />
              <Text style={styles.featureText}>{feature}</Text>
            </View>
          ))}
        </View>
      </View>
    </LinearGradient>
  </Animated.View>
))}
```

### PaymentScreen Updates Needed

1. **Glassmorphic Card Form**
```javascript
<View style={styles.paymentCard}>
  <Text style={styles.cardTitle}>Payment Method</Text>
  
  <View style={styles.inputContainer}>
    <Feather name="credit-card" size={18} color={Colors.textSecondary} />
    <TextInput
      style={styles.input}
      placeholder="Card Number"
      placeholderTextColor={Colors.textMuted}
      keyboardType="numeric"
    />
  </View>
  
  <View style={styles.inputRow}>
    <View style={[styles.inputContainer, styles.inputHalf]}>
      <Feather name="calendar" size={18} color={Colors.textSecondary} />
      <TextInput
        style={styles.input}
        placeholder="MM/YY"
        placeholderTextColor={Colors.textMuted}
      />
    </View>
    <View style={[styles.inputContainer, styles.inputHalf]}>
      <Feather name="lock" size={18} color={Colors.textSecondary} />
      <TextInput
        style={styles.input}
        placeholder="CVV"
        placeholderTextColor={Colors.textMuted}
        keyboardType="numeric"
        maxLength={3}
      />
    </View>
  </View>
</View>
```

2. **Success Animation**
```javascript
const SuccessAnimation = () => {
  const scale = useSharedValue(0);
  const rotation = useSharedValue(0);
  
  useEffect(() => {
    scale.value = withSpring(1, { damping: 8 });
    rotation.value = withSpring(360, { damping: 12 });
  }, []);
  
  const animStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { rotate: `${rotation.value}deg` }
    ],
  }));
  
  return (
    <Animated.View style={[styles.successContainer, animStyle]}>
      <LinearGradient
        colors={[Colors.success, '#2eb89e']}
        style={styles.successCircle}
      >
        <Feather name="check" size={48} color={Colors.white} />
      </LinearGradient>
    </Animated.View>
  );
};
```

### OnboardingScreen Updates Needed

1. **Page Indicators with Gradients**
```javascript
<View style={styles.pageIndicators}>
  {[0, 1, 2].map((index) => (
    <View
      key={index}
      style={[
        styles.indicator,
        currentPage === index && styles.indicatorActive
      ]}
    >
      {currentPage === index ? (
        <LinearGradient
          colors={[Colors.accent, Colors.accentDark]}
          style={styles.indicatorGradient}
        />
      ) : (
        <View style={styles.indicatorInactive} />
      )}
    </View>
  ))}
</View>
```

2. **Floating Illustrations**
```javascript
const FloatingImage = ({ children }) => {
  const translateY = useSharedValue(0);
  
  useEffect(() => {
    translateY.value = withRepeat(
      withSequence(
        withTiming(-12, { duration: 2000 }),
        withTiming(12, { duration: 2000 })
      ),
      -1,
      true
    );
  }, []);
  
  const floatStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));
  
  return (
    <Animated.View style={floatStyle}>
      {children}
    </Animated.View>
  );
};
```

## Common Styling Patterns

### Glassmorphic Card
```javascript
card: {
  backgroundColor: 'rgba(255, 255, 255, 0.06)',
  borderRadius: 16,
  padding: 16,
  borderWidth: 1,
  borderColor: 'rgba(255, 255, 255, 0.1)',
}
```

### Gradient Button
```javascript
button: {
  borderRadius: 12,
  overflow: 'hidden',
},
buttonGradient: {
  paddingVertical: 14,
  paddingHorizontal: 24,
  alignItems: 'center',
  justifyContent: 'center',
},
```

### Input Field
```javascript
inputContainer: {
  flexDirection: 'row',
  alignItems: 'center',
  backgroundColor: Colors.inputBg,
  borderRadius: 12,
  borderWidth: 1,
  borderColor: Colors.inputBorder,
  paddingHorizontal: 14,
  height: 52,
},
input: {
  flex: 1,
  fontFamily: 'Inter_400Regular',
  fontSize: 15,
  color: Colors.white,
  marginLeft: 10,
}
```

### Icon Avatar
```javascript
avatar: {
  width: 60,
  height: 60,
  borderRadius: 30,
  alignItems: 'center',
  justifyContent: 'center',
}
```

## Animation Timing Reference

- **Entrance Delays**: 80-150ms between items
- **Duration**: 400-600ms for entrances
- **Button Press**: 100ms scale down, 100ms scale up
- **Shake**: 50ms per direction (4-5 shakes total)
- **Float**: 1500-2000ms per direction
- **Spring Damping**: 8-12 for natural feel
- **Spring Stiffness**: 60-100

## Haptic Feedback Intensity

- **Light**: Card taps, selections
- **Medium**: Button presses, form submissions
- **Heavy**: Long press, delete actions
- **Success**: Successful operations
- **Error**: Form errors, failed operations

---

Use these templates and patterns to update the remaining screens consistently with the modernized LibraryScreen and LoginScreen.
