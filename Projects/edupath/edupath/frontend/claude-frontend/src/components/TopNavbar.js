import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { animations } from '../utils/animations';
import theme from '../config/theme';
import { LogOut, User, Settings } from 'lucide-react';

const TopNavbar = ({ title = 'EduPath' }) => {
  const navigate = useNavigate();
  const { user, tokenBalance, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const tokenBadgeRef = useRef(null);
  const prevTokenBalance = useRef(tokenBalance);

  useEffect(() => {
    // Animate token badge when balance changes
    if (tokenBadgeRef.current && tokenBalance !== prevTokenBalance.current) {
      animations.scaleIn(tokenBadgeRef.current, { scale: 1.3, duration: 0.5, ease: 'elastic.out' });
      prevTokenBalance.current = tokenBalance;
    }
  }, [tokenBalance]);

  useEffect(() => {
    if (showDropdown && dropdownRef.current) {
      animations.fadeIn(dropdownRef.current, { y: -10, duration: 0.3 });
    }
  }, [showDropdown]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={styles.navbar}>
      <div style={styles.container}>
        <div style={styles.left}>
          <div style={styles.logo}>
            <span style={styles.logoIcon}>📚</span>
            <span style={styles.logoText}>EduPath</span>
          </div>
          <span style={styles.title}>{title}</span>
        </div>
        
        <div style={styles.right}>
          <div 
            ref={tokenBadgeRef}
            style={styles.tokenBadge}
            onClick={() => navigate('/plans')}
          >
            <span style={styles.tokenIcon}>💰</span>
            <span style={styles.tokenCount}>{tokenBalance}</span>
          </div>
          
          <div style={styles.userSection}>
            <button
              style={styles.avatar}
              onClick={() => setShowDropdown(!showDropdown)}
            >
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </button>
            
            {showDropdown && (
              <div ref={dropdownRef} style={styles.dropdown}>
                <div style={styles.dropdownHeader}>
                  <div style={styles.dropdownUser}>{user?.username}</div>
                  <div style={styles.dropdownEmail}>{user?.email}</div>
                </div>
                <div style={styles.dropdownDivider} />
                <button
                  style={styles.dropdownItem}
                  onClick={() => {
                    navigate('/profile');
                    setShowDropdown(false);
                  }}
                >
                  <User size={16} />
                  <span>Profile</span>
                </button>
                <button
                  style={styles.dropdownItem}
                  onClick={() => {
                    navigate('/settings');
                    setShowDropdown(false);
                  }}
                >
                  <Settings size={16} />
                  <span>Settings</span>
                </button>
                <div style={styles.dropdownDivider} />
                <button
                  style={{ ...styles.dropdownItem, color: theme.colors.error }}
                  onClick={handleLogout}
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

const styles = {
  navbar: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '64px',
    backgroundColor: theme.colors.white,
    boxShadow: theme.shadows.sm,
    zIndex: theme.zIndex.sticky,
  },
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
    height: '100%',
    padding: `0 ${theme.spacing.lg}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  left: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.lg,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    cursor: 'pointer',
  },
  logoIcon: {
    fontSize: '28px',
  },
  logoText: {
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    fontFamily: theme.typography.fontFamily.display,
  },
  title: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.neutral,
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.md,
  },
  tokenBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    padding: `${theme.spacing.xs} ${theme.spacing.md}`,
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.full,
    cursor: 'pointer',
    transition: theme.transitions.base,
    ':hover': {
      transform: 'scale(1.05)',
    },
  },
  tokenIcon: {
    fontSize: '18px',
  },
  tokenCount: {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
  },
  userSection: {
    position: 'relative',
  },
  avatar: {
    width: '40px',
    height: '40px',
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.secondary,
    color: theme.colors.white,
    border: 'none',
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.bold,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: theme.transitions.base,
  },
  dropdown: {
    position: 'absolute',
    top: '50px',
    right: 0,
    width: '240px',
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.lg,
    boxShadow: theme.shadows.xl,
    padding: theme.spacing.sm,
    zIndex: theme.zIndex.dropdown,
  },
  dropdownHeader: {
    padding: theme.spacing.sm,
  },
  dropdownUser: {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.dark,
  },
  dropdownEmail: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
    marginTop: theme.spacing.xs,
  },
  dropdownDivider: {
    height: '1px',
    backgroundColor: '#e5e7eb',
    margin: `${theme.spacing.sm} 0`,
  },
  dropdownItem: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    padding: theme.spacing.sm,
    backgroundColor: 'transparent',
    border: 'none',
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.dark,
    transition: theme.transitions.fast,
    ':hover': {
      backgroundColor: theme.colors.background,
    },
  },
};

export default TopNavbar;
