import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { animations } from '../utils/animations';
import theme from '../config/theme';
import { toast } from 'react-toastify';
import LoadingSpinner from '../components/LoadingSpinner';

const AuthScreen = () => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();
  const { login, signup, isAuthenticated } = useAuth();
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/library');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div style={styles.container}>
      <div style={styles.background} />
      {isLogin ? (
        <LoginForm setIsLogin={setIsLogin} login={login} />
      ) : (
        <SignupForm setIsLogin={setIsLogin} signup={signup} />
      )}
    </div>
  );
};

const LoginForm = ({ setIsLogin, login }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const cardRef = useRef(null);
  const logoRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (logoRef.current) {
      animations.rotateIn(logoRef.current);
    }
    if (cardRef.current) {
      animations.slideInUp(cardRef.current, { delay: 0.3 });
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await login({ email, password });
    
    if (result.success) {
      navigate('/library');
    } else {
      toast.error(result.error || 'Login failed');
    }
    
    setLoading(false);
  };

  return (
    <>
      <div ref={logoRef} style={styles.logo}>
        <span style={styles.logoIcon}>📚</span>
        <span style={styles.logoText}>EduPath</span>
      </div>
      
      <div ref={cardRef} style={styles.card}>
        <h1 style={styles.title}>Welcome Back</h1>
        <p style={styles.subtitle}>Sign in to continue learning</p>
        
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              placeholder="you@example.com"
              required
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              placeholder="••••••••"
              required
            />
          </div>
          
          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? <LoadingSpinner size={20} color={theme.colors.white} /> : 'Sign In'}
          </button>
        </form>
        
        <div style={styles.footer}>
          <span style={styles.footerText}>Don't have an account? </span>
          <button
            onClick={() => setIsLogin(false)}
            style={styles.link}
          >
            Sign up
          </button>
        </div>
      </div>
    </>
  );
};

const SignupForm = ({ setIsLogin, signup }) => {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const cardRef = useRef(null);
  const otpRefs = useRef([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (cardRef.current) {
      animations.slideInUp(cardRef.current, { delay: 0.3 });
    }
  }, []);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleSendOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await apiService.auth.sendOTP(email);
      toast.success('OTP sent to your email!');
      setStep(2);
      setCountdown(60);
    } catch (error) {
      toast.error('Failed to send OTP');
    }
    
    setLoading(false);
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    const otpString = otp.join('');
    
    if (otpString.length !== 6) {
      toast.error('Please enter complete OTP');
      return;
    }
    
    setLoading(true);
    
    try {
      await apiService.auth.verifyOTP(email, otpString);
      toast.success('Email verified!');
      setStep(3);
    } catch (error) {
      toast.error('Invalid OTP');
      animations.shake(cardRef.current);
    }
    
    setLoading(false);
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await signup({
      email,
      username,
      password,
      full_name: fullName,
      otp_verified: true,
    });
    
    if (result.success) {
      navigate('/library');
    } else {
      toast.error(result.error || 'Signup failed');
    }
    
    setLoading(false);
  };

  const handleOtpChange = (index, value) => {
    if (value.length <= 1 && /^\d*$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);
      
      if (value && index < 5) {
        otpRefs.current[index + 1]?.focus();
      }
    }
  };

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  return (
    <div ref={cardRef} style={styles.card}>
      <h1 style={styles.title}>Create Account</h1>
      <p style={styles.subtitle}>
        {step === 1 && 'Enter your email to get started'}
        {step === 2 && 'Verify your email'}
        {step === 3 && 'Complete your profile'}
      </p>
      
      {step === 1 && (
        <form onSubmit={handleSendOTP} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              placeholder="you@example.com"
              required
            />
          </div>
          
          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? <LoadingSpinner size={20} color={theme.colors.white} /> : 'Send OTP'}
          </button>
        </form>
      )}
      
      {step === 2 && (
        <form onSubmit={handleVerifyOTP} style={styles.form}>
          <div style={styles.otpContainer}>
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => (otpRefs.current[index] = el)}
                type="text"
                value={digit}
                onChange={(e) => handleOtpChange(index, e.target.value)}
                onKeyDown={(e) => handleOtpKeyDown(index, e)}
                style={styles.otpInput}
                maxLength={1}
                required
              />
            ))}
          </div>
          
          <div style={styles.countdown}>
            {countdown > 0 ? (
              <span>Resend OTP in {countdown}s</span>
            ) : (
              <button
                type="button"
                onClick={() => handleSendOTP({ preventDefault: () => {} })}
                style={styles.resendButton}
              >
                Resend OTP
              </button>
            )}
          </div>
          
          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? <LoadingSpinner size={20} color={theme.colors.white} /> : 'Verify OTP'}
          </button>
        </form>
      )}
      
      {step === 3 && (
        <form onSubmit={handleSignup} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              style={styles.input}
              placeholder="John Doe"
              required
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={styles.input}
              placeholder="johndoe"
              required
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>
          
          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? <LoadingSpinner size={20} color={theme.colors.white} /> : 'Create Account'}
          </button>
        </form>
      )}
      
      <div style={styles.footer}>
        <span style={styles.footerText}>Already have an account? </span>
        <button
          onClick={() => setIsLogin(true)}
          style={styles.link}
        >
          Sign in
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing.lg,
    position: 'relative',
    overflow: 'hidden',
  },
  background: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: theme.gradients.dark,
    zIndex: -1,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.xl,
  },
  logoIcon: {
    fontSize: '48px',
  },
  logoText: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.white,
    fontFamily: theme.typography.fontFamily.display,
  },
  card: {
    width: '100%',
    maxWidth: '440px',
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.xxl,
    boxShadow: theme.shadows.xl,
  },
  title: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.sm,
    fontFamily: theme.typography.fontFamily.display,
  },
  subtitle: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.neutral,
    marginBottom: theme.spacing.xl,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.lg,
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.xs,
  },
  label: {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.dark,
  },
  input: {
    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
    fontSize: theme.typography.fontSize.base,
    border: `2px solid #e5e7eb`,
    borderRadius: theme.borderRadius.md,
    outline: 'none',
    transition: theme.transitions.base,
    backgroundColor: theme.colors.white,
    color: theme.colors.dark,
  },
  button: {
    padding: `${theme.spacing.md} ${theme.spacing.lg}`,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.dark,
    backgroundColor: theme.colors.primary,
    border: 'none',
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    transition: theme.transitions.base,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '48px',
  },
  otpContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(6, 1fr)',
    gap: theme.spacing.sm,
  },
  otpInput: {
    width: '100%',
    aspectRatio: '1',
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    textAlign: 'center',
    border: `2px solid #e5e7eb`,
    borderRadius: theme.borderRadius.md,
    outline: 'none',
    transition: theme.transitions.base,
    backgroundColor: theme.colors.white,
    color: theme.colors.dark,
  },
  countdown: {
    textAlign: 'center',
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
  },
  resendButton: {
    background: 'none',
    border: 'none',
    color: theme.colors.primary,
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  footer: {
    marginTop: theme.spacing.lg,
    textAlign: 'center',
  },
  footerText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
  },
  link: {
    background: 'none',
    border: 'none',
    color: theme.colors.primary,
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    textDecoration: 'underline',
  },
};

export default AuthScreen;
