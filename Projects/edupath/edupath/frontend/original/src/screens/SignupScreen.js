import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import theme from '../config/theme';

const SignupScreen = () => {
  const navigation = useNavigation();
  const { signup } = useAuth();
  
  const [step, setStep] = useState(1); // 1: Email, 2: OTP, 3: Details
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);

const handleSendOTP = async () => {
    if (!email || !email.includes('@')) {
      Alert.alert('Invalid Email', 'Please enter a valid email address');
      return;
    }

    setLoading(true);
    
    try {
      await apiService.sendOTP(email);
      setOtpSent(true);
      setStep(2);
      Alert.alert('✅ OTP Sent', 'Please check your email for the verification code');
    } catch (error) {
      console.error('Send OTP error:', error);
      const errorMsg = error.response?.data?.error || 'Failed to send OTP';
      Alert.alert('❌ Error', errorMsg);  // ✅ Show actual error
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!otp || otp.length !== 6) {
      Alert.alert('Invalid OTP', 'Please enter the 6-digit code');
      return;
    }

    setLoading(true);
    
    try {
      await apiService.verifyOTP(email, otp);
      setStep(3);
      Alert.alert('✅ Verified', 'Email verified successfully');
    } catch (error) {
      console.error('Verify OTP error:', error);
      const errorMsg = error.response?.data?.error || 'Invalid OTP';
      Alert.alert('❌ Verification Failed', errorMsg);  // ✅ Show actual error
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async () => {
    // ✅ Better validation
    if (!username || username.length < 3) {
      Alert.alert('Invalid Username', 'Username must be at least 3 characters');
      return;
    }

    if (!password || password.length < 6) {
      Alert.alert('Invalid Password', 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    
    try {
      const result = await signup({
        email,
        username,
        password,
        full_name: fullName,
        otp_verified: true,
      });

      if (!result.success) {
        Alert.alert('❌ Signup Failed', result.error || 'Please try again');
      }
      // Success handled by AuthContext navigation
    } catch (error) {
      console.error('Signup error:', error);
      const errorMsg = error.response?.data?.error || 'Signup failed. Please try again.';
      Alert.alert('❌ Error', errorMsg);  // ✅ Show actual error
    } finally {
      setLoading(false);
    }
  };
  const renderStep1 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Create Your Account</Text>
      <Text style={styles.stepSubtitle}>Enter your email to get started</Text>

      <TextInput
        style={styles.input}
        placeholder="Email Address"
        placeholderTextColor={theme.colors.textLight}
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        editable={!otpSent}
      />

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleSendOTP}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color={theme.colors.textInverse} />
        ) : (
          <Text style={styles.buttonText}>Send Verification Code</Text>
        )}
      </TouchableOpacity>
    </View>
  );

  const renderStep2 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Verify Your Email</Text>
      <Text style={styles.stepSubtitle}>
        We sent a 6-digit code to {email}
      </Text>

      <TextInput
        style={[styles.input, styles.otpInput]}
        placeholder="000000"
        placeholderTextColor={theme.colors.textLight}
        value={otp}
        onChangeText={setOtp}
        keyboardType="number-pad"
        maxLength={6}
      />

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleVerifyOTP}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color={theme.colors.textInverse} />
        ) : (
          <Text style={styles.buttonText}>Verify Code</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.resendButton}
        onPress={handleSendOTP}
      >
        <Text style={styles.resendText}>Resend Code</Text>
      </TouchableOpacity>
    </View>
  );

  const renderStep3 = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Complete Your Profile</Text>
      <Text style={styles.stepSubtitle}>Just a few more details</Text>

      <TextInput
        style={styles.input}
        placeholder="Full Name (Optional)"
        placeholderTextColor={theme.colors.textLight}
        value={fullName}
        onChangeText={setFullName}
      />

      <TextInput
        style={styles.input}
        placeholder="Username"
        placeholderTextColor={theme.colors.textLight}
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />

      <TextInput
        style={styles.input}
        placeholder="Password (min 6 characters)"
        placeholderTextColor={theme.colors.textLight}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleSignup}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color={theme.colors.textInverse} />
        ) : (
          <Text style={styles.buttonText}>Create Account</Text>
        )}
      </TouchableOpacity>
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>EduPath</Text>
          <View style={styles.stepIndicator}>
            <View style={[styles.stepDot, step >= 1 && styles.stepDotActive]} />
            <View style={[styles.stepDot, step >= 2 && styles.stepDotActive]} />
            <View style={[styles.stepDot, step >= 3 && styles.stepDotActive]} />
          </View>
        </View>

        {/* Content */}
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Already have an account?</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Login')}>
            <Text style={styles.footerLink}>Sign In</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    padding: theme.spacing.xl,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: theme.spacing.xxxl,
  },
  logo: {
    fontSize: theme.fonts.sizes.xxxl,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.secondaryDeep,
    marginBottom: theme.spacing.lg,
  },
  stepIndicator: {
    flexDirection: 'row',
    gap: theme.spacing.sm,
  },
  stepDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: theme.colors.border,
  },
  stepDotActive: {
    backgroundColor: theme.colors.primary,
  },
  stepContainer: {
    marginBottom: theme.spacing.xl,
  },
  stepTitle: {
    fontSize: theme.fonts.sizes.xxl,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
  },
  stepSubtitle: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
  },
  input: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.md,
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  otpInput: {
    textAlign: 'center',
    fontSize: theme.fonts.sizes.xxl,
    letterSpacing: 8,
    fontWeight: theme.fonts.weights.bold,
  },
  button: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginTop: theme.spacing.md,
    ...theme.shadows.md,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.secondaryDeep,
  },
  resendButton: {
    marginTop: theme.spacing.lg,
    alignItems: 'center',
  },
  resendText: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.secondary,
    fontWeight: theme.fonts.weights.medium,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: theme.spacing.xxl,
    gap: theme.spacing.xs,
  },
  footerText: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.textSecondary,
  },
  footerLink: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.primary,
    fontWeight: theme.fonts.weights.semibold,
  },
});

export default SignupScreen;