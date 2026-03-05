import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  ActivityIndicator,
  Platform,
  KeyboardAvoidingView,
  ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSequence,
  FadeInDown,
  FadeInUp,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import Colors from '../constants/colors';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

const SignupScreen = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { signup } = useAuth();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const buttonScale = useSharedValue(1);
  const errorShake = useSharedValue(0);

  const usernameRef = useRef(null);
  const fullNameRef = useRef(null);
  const passwordRef = useRef(null);

  const buttonAnimStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  const errorStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: errorShake.value }],
  }));

  const handleSignup = async () => {
    if (!email.trim() || !username.trim() || !fullName.trim() || !password.trim()) {
      setError('Please fill in all fields');
      errorShake.value = withSequence(
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(0, { duration: 50 })
      );
      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      errorShake.value = withSequence(
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(-10, { duration: 50 }),
        withTiming(0, { duration: 50 })
      );
      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      return;
    }

    setIsSubmitting(true);
    setError('');
    buttonScale.value = withSequence(
      withTiming(0.95, { duration: 100 }),
      withTiming(1, { duration: 100 })
    );

    try {
      const result = await signup({ email, username, password, fullName });
      if (result.success) {
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else {
        setError(result.error || 'Signup failed');
        errorShake.value = withSequence(
          withTiming(-10, { duration: 50 }),
          withTiming(10, { duration: 50 }),
          withTiming(-10, { duration: 50 }),
          withTiming(0, { duration: 50 })
        );
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
    } catch (e) {
      setError(e.message || 'Signup failed');
      errorShake.value = withSequence(
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(-10, { duration: 50 }),
        withTiming(0, { duration: 50 })
      );
      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <LinearGradient colors={['#0e3248', '#1a4a6e', '#2f4954']} style={styles.gradient}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          contentContainerStyle={[
            styles.scrollContent,
            {
              paddingTop: insets.top + 40,
              paddingBottom: insets.bottom + 40,
            },
          ]}
          showsVerticalScrollIndicator={false}
        >
          <Pressable
            style={styles.backBtn}
            onPress={() => navigation.goBack()}
            hitSlop={12}
          >
            <Feather name="arrow-left" size={22} color={Colors.white} />
          </Pressable>

          <Animated.View entering={FadeInDown.delay(200).duration(600)} style={styles.logoContainer}>
            <LinearGradient
              colors={[Colors.accent, Colors.accentDark]}
              style={styles.logoCircle}
            >
              <Feather name="user-plus" size={32} color={Colors.primaryDark} />
            </LinearGradient>
          </Animated.View>

          <Animated.Text entering={FadeInDown.delay(300).duration(600)} style={styles.title}>
            Create Account
          </Animated.Text>
          <Animated.Text entering={FadeInDown.delay(400).duration(600)} style={styles.subtitle}>
            Join EduPath and start learning
          </Animated.Text>

          <Animated.View entering={FadeInDown.delay(500).duration(600)} style={styles.card}>
            <Animated.View style={errorStyle}>
              {error ? (
                <View style={styles.errorContainer}>
                  <Feather name="alert-circle" size={14} color={Colors.error} />
                  <Text style={styles.errorText}>{error}</Text>
                </View>
              ) : null}
            </Animated.View>

            <View style={styles.inputContainer}>
              <Feather name="mail" size={18} color={Colors.textSecondary} style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Email address"
                placeholderTextColor={Colors.textMuted}
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
                returnKeyType="next"
                onSubmitEditing={() => usernameRef.current?.focus()}
              />
            </View>

            <View style={styles.inputContainer}>
              <Feather name="user" size={18} color={Colors.textSecondary} style={styles.inputIcon} />
              <TextInput
                ref={usernameRef}
                style={styles.input}
                placeholder="Username"
                placeholderTextColor={Colors.textMuted}
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
                returnKeyType="next"
                onSubmitEditing={() => fullNameRef.current?.focus()}
              />
            </View>

            <View style={styles.inputContainer}>
              <Feather name="smile" size={18} color={Colors.textSecondary} style={styles.inputIcon} />
              <TextInput
                ref={fullNameRef}
                style={styles.input}
                placeholder="Full Name"
                placeholderTextColor={Colors.textMuted}
                value={fullName}
                onChangeText={setFullName}
                returnKeyType="next"
                onSubmitEditing={() => passwordRef.current?.focus()}
              />
            </View>

            <View style={styles.inputContainer}>
              <Feather name="lock" size={18} color={Colors.textSecondary} style={styles.inputIcon} />
              <TextInput
                ref={passwordRef}
                style={styles.input}
                placeholder="Password (min 6 characters)"
                placeholderTextColor={Colors.textMuted}
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                returnKeyType="done"
                onSubmitEditing={handleSignup}
              />
              <Pressable onPress={() => setShowPassword(!showPassword)} hitSlop={8}>
                <Feather name={showPassword ? 'eye-off' : 'eye'} size={18} color={Colors.textSecondary} />
              </Pressable>
            </View>

            <AnimatedPressable
              style={[styles.button, buttonAnimStyle]}
              onPress={handleSignup}
              disabled={isSubmitting}
            >
              <LinearGradient
                colors={[Colors.accent, Colors.accentDark]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.buttonGradient}
              >
                {isSubmitting ? (
                  <ActivityIndicator color={Colors.primaryDark} />
                ) : (
                  <Text style={styles.buttonText}>Create Account</Text>
                )}
              </LinearGradient>
            </AnimatedPressable>
          </Animated.View>

          <Animated.View entering={FadeInUp.delay(700).duration(600)} style={styles.footer}>
            <Text style={styles.footerText}>Already have an account?</Text>
            <Pressable onPress={() => navigation.navigate('Login')} hitSlop={8}>
              <Text style={styles.footerLink}>Sign In</Text>
            </Pressable>
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  gradient: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  backBtn: {
    position: 'absolute',
    top: 16,
    left: 24,
    zIndex: 10,
  },
  logoContainer: {
    marginBottom: 16,
  },
  logoCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontFamily: 'Inter_700Bold',
    fontSize: 32,
    color: Colors.white,
    marginBottom: 4,
  },
  subtitle: {
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    color: Colors.textSecondary,
    marginBottom: 32,
  },
  card: {
    width: '100%',
    maxWidth: 400,
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: 'rgba(255, 107, 107, 0.15)',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    marginBottom: 16,
  },
  errorText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 13,
    color: Colors.error,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.inputBg,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.inputBorder,
    marginBottom: 14,
    paddingHorizontal: 14,
    height: 52,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    color: Colors.white,
    height: '100%',
  },
  button: {
    marginTop: 6,
    borderRadius: 12,
    overflow: 'hidden',
  },
  buttonGradient: {
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
  },
  buttonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.primaryDark,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 28,
  },
  footerText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
  },
  footerLink: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.accent,
  },
});

export default SignupScreen;
