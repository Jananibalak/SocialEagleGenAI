import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { animations } from '../utils/animations';
import theme from '../config/theme';
import { User, Mail, Calendar, LogOut } from 'lucide-react';

const ProfileScreen = () => {
  const { user, tokenBalance, logout } = useAuth();
  const navigate = useNavigate();
  const avatarRef = useRef(null);
  const statsRefs = useRef([]);

  useEffect(() => {
    if (avatarRef.current) {
      animations.rotateIn(avatarRef.current, { rotation: 360, duration: 0.8 });
    }
    if (statsRefs.current.length > 0) {
      animations.staggerSlideIn(statsRefs.current, { y: 50, stagger: 0.2 });
    }
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={styles.container}>
      <div style={styles.profileCard}>
        <div ref={avatarRef} style={styles.avatar}>
          {user?.username?.charAt(0).toUpperCase() || 'U'}
        </div>
        <h1 style={styles.username}>{user?.username}</h1>
        <p style={styles.email}>{user?.email}</p>
      </div>

      <div style={styles.statsGrid}>
        <div ref={el => statsRefs.current[0] = el} style={styles.statCard}>
          <div style={styles.statIcon}>💰</div>
          <div style={styles.statValue}>{tokenBalance}</div>
          <div style={styles.statLabel}>Tokens</div>
        </div>
        <div ref={el => statsRefs.current[1] = el} style={styles.statCard}>
          <div style={styles.statIcon}>📚</div>
          <div style={styles.statValue}>-</div>
          <div style={styles.statLabel}>Mentors</div>
        </div>
        <div ref={el => statsRefs.current[2] = el} style={styles.statCard}>
          <div style={styles.statIcon}>🔥</div>
          <div style={styles.statValue}>-</div>
          <div style={styles.statLabel}>Streak</div>
        </div>
      </div>

      <div style={styles.actions}>
        <button style={styles.actionButton}>
          <User size={20} />
          <span>Edit Profile</span>
        </button>
        <button style={styles.actionButton}>
          <Mail size={20} />
          <span>Change Email</span>
        </button>
        <button style={styles.actionButton}>
          <Calendar size={20} />
          <span>Learning History</span>
        </button>
      </div>

      <button style={styles.logoutButton} onClick={handleLogout}>
        <LogOut size={20} />
        <span>Logout</span>
      </button>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '700px',
    margin: '0 auto',
    padding: theme.spacing.xl,
  },
  profileCard: {
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.xxl,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
  },
  avatar: {
    width: '120px',
    height: '120px',
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.secondary,
    color: theme.colors.white,
    fontSize: '48px',
    fontWeight: theme.typography.fontWeight.bold,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto',
    marginBottom: theme.spacing.lg,
  },
  username: {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.xs,
    fontFamily: theme.typography.fontFamily.display,
  },
  email: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.neutral,
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: theme.spacing.md,
    marginBottom: theme.spacing.xl,
  },
  statCard: {
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    textAlign: 'center',
  },
  statIcon: {
    fontSize: '32px',
    marginBottom: theme.spacing.sm,
  },
  statValue: {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.xs,
  },
  statLabel: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
  },
  actions: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.sm,
    marginBottom: theme.spacing.xl,
  },
  actionButton: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.white,
    border: '2px solid #e5e7eb',
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.dark,
    transition: theme.transitions.base,
  },
  logoutButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: theme.spacing.sm,
    width: '100%',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.error,
    border: 'none',
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.white,
    transition: theme.transitions.base,
  },
};

export default ProfileScreen;
