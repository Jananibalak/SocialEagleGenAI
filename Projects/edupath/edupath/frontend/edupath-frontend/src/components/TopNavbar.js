import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Platform,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { useNavigation } from '@react-navigation/native';
import theme from '../config/theme';

const TopNavbar = ({ title, showProfile = true }) => {
  const { user, tokenBalance } = useAuth();
  const navigation = useNavigation();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getUserDisplayName = () => {
    if (user?.full_name) return user.full_name;
    if (user?.username) return user.username;
    return 'Scholar';
  };

  return (
    <View style={styles.container}>
      <View style={styles.leftSection}>
        <View style={styles.logoContainer}>
          <Text style={styles.logoIcon}>📚</Text>
          <Text style={styles.logoText}>EduPath</Text>
        </View>
        {title && <Text style={styles.title}>{title}</Text>}
      </View>

      {showProfile && user && (
        <View style={styles.rightSection}>
          {/* Token Balance */}
          <View style={styles.tokenBadge}>
            <Text style={styles.tokenIcon}>💰</Text>
            <Text style={styles.tokenText}>{tokenBalance || 0}</Text>
          </View>

          {/* User Profile */}
          <TouchableOpacity
            style={styles.profileButton}
            onPress={() => navigation.navigate('ProfileTab')}
          >
            <View style={styles.avatarContainer}>
              <Text style={styles.avatarText}>
                {getUserDisplayName().charAt(0).toUpperCase()}
              </Text>
            </View>
            <View style={styles.userInfo}>
              <Text style={styles.greeting}>{getGreeting()}</Text>
              <Text style={styles.userName}>{getUserDisplayName()}</Text>
            </View>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    backgroundColor: theme.colors.backgroundSecondary,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    ...theme.shadows.sm,
    // Safe area for mobile
    paddingTop: Platform.OS === 'ios' ? theme.spacing.xl : theme.spacing.md,
  },
  leftSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: theme.spacing.lg,
  },
  logoIcon: {
    fontSize: 24,
    marginRight: theme.spacing.xs,
  },
  logoText: {
    fontSize: theme.fonts.sizes.xl,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.secondaryDeep,
  },
  title: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.text,
  },
  rightSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.md,
  },
  tokenBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.full,
    ...theme.shadows.sm,
  },
  tokenIcon: {
    fontSize: 16,
    marginRight: theme.spacing.xs,
  },
  tokenText: {
    fontSize: theme.fonts.sizes.sm,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.secondaryDeep,
  },
  profileButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.sm,
  },
  avatarContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.colors.secondary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.textInverse,
  },
  userInfo: {
    // Hide on small screens
    display: Platform.OS === 'web' ? 'flex' : 'none',
  },
  greeting: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.textSecondary,
  },
  userName: {
    fontSize: theme.fonts.sizes.sm,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.text,
  },
});

export default TopNavbar;