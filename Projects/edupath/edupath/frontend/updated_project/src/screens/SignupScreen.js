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
  FadeOutLeft,
  FadeInRight,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import Colors from '../constants/colors';
import { showAlert } from '../utils/alert';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

const SignupScreen = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { signup } = useAuth();
  
  // ✅ STEP MANAGEMENT
  const [step, setStep] = useState(1); // 1: Email, 2: OTP, 3: Details
  
  // Step 1: Email
  const [email, setEmail] = useState('');
  const [sendingOTP, setSendingOTP] = useState(false);
  
  // Step 2: OTP
  const [otp, setOtp] = useState('');
  const [verifyingOTP, setVerifyingOTP] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  
  // Step 3: User Details
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [error, setError] = useState('');

  const buttonScale = useSharedValue(1);
  const errorShake = useSharedValue(0);

  const otpRef = useRef(null);
  const usernameRef = useRef(null);
  const fullNameRef = useRef(null);
  const passwordRef = useRef(null);

  const buttonAnimStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  const errorStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: errorShake.value }],
  }));

  // ✅ STEP 1: Send OTP
  const handleSendOTP = async () => {
    if (!email.trim()) {
      setError('Please enter your email');
      shakeError();
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email');
      shakeError();
      return;
    }

    setSendingOTP(true);
    setError('');
    animateButton();

    try {
      const response = await apiService.sendOTP(email);
      
      if (response.success) {
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
        setStep(2);
        startResendCooldown();
        
        // Focus OTP input after transition
        setTimeout(() => otpRef.current?.focus(), 300);
      } else {
        setError(response.message || 'Failed to send OTP');
        shakeError();
      }
    } catch (error) {
      console.error('Send OTP error:', error);
      setError(error.response?.data?.error || 'Failed to send OTP. Please try again.');
      shakeError();
    } finally {
      setSendingOTP(false);
    }
  };

  // ✅ STEP 2: Verify OTP
  const handleVerifyOTP = async () => {
    if (!otp.trim() || otp.length !== 6) {
      setError('Please enter the 6-digit OTP');
      shakeError();
      return;
    }

    setVerifyingOTP(true);
    setError('');
    animateButton();

    try {
      const response = await apiService.verifyOTP(email, otp);
      
      if (response.success) {
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
        setOtpVerified(true);
        setStep(3);
        
        // Focus username input after transition
        setTimeout(() => usernameRef.current?.focus(), 300);
      } else {
        setError(response.message || 'Invalid OTP');
        shakeError();
      }
    } catch (error) {
      console.error('Verify OTP error:', error);
      setError(error.response?.data?.error || 'Invalid OTP. Please try again.');
      shakeError();
    } finally {
      setVerifyingOTP(false);
    }
  };

  // ✅ STEP 3: Complete Signup
  const handleCompleteSignup = async () => {
    if (!username.trim() || !fullName.trim() || !password.trim()) {
      setError('Please fill in all fields');
      shakeError();
      return;
    }

    if (username.length < 3) {
      setError('Username must be at least 3 characters');
      shakeError();
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      shakeError();
      return;
    }

    setIsSubmitting(true);
    setError('');
    animateButton();

    try {
      const result = await signup({
        email,
        username,
        password,
        full_name: fullName,
        otp_verified: true,
      });

      if (result.success) {
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
        // Navigation handled by AuthContext
      } else {
        setError(result.error || 'Signup failed');
        shakeError();
      }
    } catch (error) {
      console.error('Signup error:', error);
      setError(error.message || 'Signup failed. Please try again.');
      shakeError();
    } finally {
      setIsSubmitting(false);
    }
  };

  // ✅ Resend OTP
  const handleResendOTP = async () => {
    if (resendCooldown > 0) return;

    setSendingOTP(true);
    setError('');

    try {
      const response = await apiService.sendOTP(email);
      
      if (response.success) {
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
        showAlert('Success', 'OTP sent successfully!');
        startResendCooldown();
      } else {
        setError(response.message || 'Failed to resend OTP');
        shakeError();
      }
    } catch (error) {
      console.error('Resend OTP error:', error);
      setError('Failed to resend OTP. Please try again.');
      shakeError();
    } finally {
      setSendingOTP(false);
    }
  };

  // Helper functions
  const shakeError = () => {
    errorShake.value = withSequence(
      withTiming(-10, { duration: 50 }),
      withTiming(10, { duration: 50 }),
      withTiming(-10, { duration: 50 }),
      withTiming(10, { duration: 50 }),
      withTiming(0, { duration: 50 })
    );
    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  };

  const animateButton = () => {
    buttonScale.value = withSequence(
      withTiming(0.95, { duration: 100 }),
      withTiming(1, { duration: 100 })
    );
  };

  const startResendCooldown = () => {
    setResendCooldown(60);
    const interval = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const goBack = () => {
    if (step === 1) {
      navigation.goBack();
    } else if (step === 2) {
      setStep(1);
      setOtp('');
      setError('');
    } else if (step === 3) {
      setStep(2);
      setError('');
    }
  };

  // ✅ RENDER STEP 1: EMAIL
  const renderEmailStep = () => (
    <Animated.View 
      entering={FadeInRight.duration(400)} 
      exiting={FadeOutLeft.duration(300)}
      style={styles.card}
    >
      <Animated.View style={errorStyle}>
        {error ? (
          <View style={styles.errorContainer}>
            <Feather name="alert-circle" size={14} color={Colors.error} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : null}
      </Animated.View>

      <Text style={styles.stepTitle}>Step 1 of 3</Text>
      <Text style={styles.stepDescription}>
        Enter your email to receive a verification code
      </Text>

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
          onSubmitEditing={handleSendOTP}
          autoFocus
        />
      </View>

      <AnimatedPressable
        style={[styles.button, buttonAnimStyle]}
        onPress={handleSendOTP}
        disabled={sendingOTP}
      >
        <LinearGradient
          colors={[Colors.accent, Colors.accentDark]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.buttonGradient}
        >
          {sendingOTP ? (
            <ActivityIndicator color={Colors.primaryDark} />
          ) : (
            <>
              <Text style={styles.buttonText}>Send OTP</Text>
              <Feather name="arrow-right" size={18} color={Colors.primaryDark} />
            </>
          )}
        </LinearGradient>
      </AnimatedPressable>
    </Animated.View>
  );

  // ✅ RENDER STEP 2: OTP VERIFICATION
  const renderOTPStep = () => (
    <Animated.View 
      entering={FadeInRight.duration(400)} 
      exiting={FadeOutLeft.duration(300)}
      style={styles.card}
    >
      <Animated.View style={errorStyle}>
        {error ? (
          <View style={styles.errorContainer}>
            <Feather name="alert-circle" size={14} color={Colors.error} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : null}
      </Animated.View>

      <Text style={styles.stepTitle}>Step 2 of 3</Text>
      <Text style={styles.stepDescription}>
        Enter the 6-digit code sent to {email}
      </Text>

      <View style={styles.inputContainer}>
        <Feather name="shield" size={18} color={Colors.textSecondary} style={styles.inputIcon} />
        <TextInput
          ref={otpRef}
          style={styles.input}
          placeholder="Enter OTP"
          placeholderTextColor={Colors.textMuted}
          value={otp}
          onChangeText={(text) => setOtp(text.replace(/[^0-9]/g, ''))}
          keyboardType="number-pad"
          maxLength={6}
          returnKeyType="done"
          onSubmitEditing={handleVerifyOTP}
        />
      </View>

      <AnimatedPressable
        style={[styles.button, buttonAnimStyle]}
        onPress={handleVerifyOTP}
        disabled={verifyingOTP}
      >
        <LinearGradient
          colors={[Colors.accent, Colors.accentDark]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.buttonGradient}
        >
          {verifyingOTP ? (
            <ActivityIndicator color={Colors.primaryDark} />
          ) : (
            <>
              <Text style={styles.buttonText}>Verify OTP</Text>
              <Feather name="check" size={18} color={Colors.primaryDark} />
            </>
          )}
        </LinearGradient>
      </AnimatedPressable>

      <Pressable
        onPress={handleResendOTP}
        disabled={resendCooldown > 0 || sendingOTP}
        style={styles.resendButton}
      >
        <Text style={[styles.resendText, (resendCooldown > 0 || sendingOTP) && styles.resendDisabled]}>
          {resendCooldown > 0 ? `Resend OTP in ${resendCooldown}s` : 'Resend OTP'}
        </Text>
      </Pressable>
    </Animated.View>
  );

  // ✅ RENDER STEP 3: USER DETAILS
  const renderDetailsStep = () => (
    <Animated.View 
      entering={FadeInRight.duration(400)} 
      exiting={FadeOutLeft.duration(300)}
      style={styles.card}
    >
      <Animated.View style={errorStyle}>
        {error ? (
          <View style={styles.errorContainer}>
            <Feather name="alert-circle" size={14} color={Colors.error} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : null}
      </Animated.View>

      <Text style={styles.stepTitle}>Step 3 of 3</Text>
      <Text style={styles.stepDescription}>
        Complete your profile to get started
      </Text>

      <View style={styles.inputContainer}>
        <Feather name="user" size={18} color={Colors.textSecondary} style={styles.inputIcon} />
        <TextInput
          ref={usernameRef}
          style={styles.input}
          placeholder="Username (min 3 characters)"
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
          onSubmitEditing={handleCompleteSignup}
        />
        <Pressable onPress={() => setShowPassword(!showPassword)} hitSlop={8}>
          <Feather name={showPassword ? 'eye-off' : 'eye'} size={18} color={Colors.textSecondary} />
        </Pressable>
      </View>

      <AnimatedPressable
        style={[styles.button, buttonAnimStyle]}
        onPress={handleCompleteSignup}
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
            <>
              <Text style={styles.buttonText}>Create Account</Text>
              <Feather name="check-circle" size={18} color={Colors.primaryDark} />
            </>
          )}
        </LinearGradient>
      </AnimatedPressable>
    </Animated.View>
  );

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
          keyboardShouldPersistTaps="handled"
        >
          <Pressable
            style={styles.backBtn}
            onPress={goBack}
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

          {/* ✅ STEP INDICATOR */}
          <Animated.View entering={FadeInDown.delay(500).duration(600)} style={styles.stepIndicator}>
            <View style={[styles.stepDot, step >= 1 && styles.stepDotActive]} />
            <View style={[styles.stepLine, step >= 2 && styles.stepLineActive]} />
            <View style={[styles.stepDot, step >= 2 && styles.stepDotActive]} />
            <View style={[styles.stepLine, step >= 3 && styles.stepLineActive]} />
            <View style={[styles.stepDot, step >= 3 && styles.stepDotActive]} />
          </Animated.View>

          {/* ✅ RENDER CURRENT STEP */}
          {step === 1 && renderEmailStep()}
          {step === 2 && renderOTPStep()}
          {step === 3 && renderDetailsStep()}

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
    marginBottom: 24,
  },
  // ✅ STEP INDICATOR
  stepIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  stepDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  stepDotActive: {
    backgroundColor: Colors.accent,
  },
  stepLine: {
    width: 40,
    height: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  stepLineActive: {
    backgroundColor: Colors.accent,
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
  stepTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.accent,
    marginBottom: 8,
  },
  stepDescription: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 20,
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    borderRadius: 12,
  },
  buttonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.primaryDark,
  },
  resendButton: {
    marginTop: 16,
    alignSelf: 'center',
  },
  resendText: {
    fontFamily: 'Inter_500Medium',
    fontSize: 14,
    color: Colors.accent,
  },
  resendDisabled: {
    color: Colors.textMuted,
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