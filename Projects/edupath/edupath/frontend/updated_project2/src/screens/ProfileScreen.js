import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Pressable,
  ScrollView,
  StyleSheet,
  Platform,
  Alert,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  FadeInRight,
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withDelay,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import Colors from '../constants/colors';

const StatCard = ({ icon, label, value, index }) => {
  const scale = useSharedValue(0);

  useEffect(() => {
    scale.value = withDelay(index * 100, withSpring(1, { damping: 10 }));
  }, []);

  const animStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Animated.View style={[styles.statCard, animStyle]}>
      <LinearGradient
        colors={['rgba(255,255,255,0.08)', 'rgba(255,255,255,0.04)']}
        style={styles.statGradient}
      >
        <View style={styles.statIconContainer}>
          <Feather name={icon} size={20} color={Colors.accent} />
        </View>
        <Text style={styles.statValue}>{value}</Text>
        <Text style={styles.statLabel}>{label}</Text>
      </LinearGradient>
    </Animated.View>
  );
};

const SettingItem = ({ icon, label, onPress, showArrow = true, destructive = false }) => {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.settingItem,
        pressed && styles.settingItemPressed,
      ]}
      onPress={() => {
        if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        onPress();
      }}
    >
      <View style={styles.settingLeft}>
        <View style={[styles.settingIcon, destructive && styles.settingIconDestructive]}>
          <Feather name={icon} size={18} color={destructive ? Colors.error : Colors.accent} />
        </View>
        <Text style={[styles.settingLabel, destructive && styles.settingLabelDestructive]}>
          {label}
        </Text>
      </View>
      {showArrow && <Feather name="chevron-right" size={18} color={Colors.textMuted} />}
    </Pressable>
  );
};

const ProfileScreen = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { user, logout, tokenBalance } = useAuth();
  const [stats, setStats] = useState({
    mentorsCount: 0,
    scrollsCount: 0,
    streakDays: 0,
  });

  useFocusEffect(
    React.useCallback(() => {
      loadStats();
    }, [])
  );

  const loadStats = async () => {
    try {
      const response = await apiService.getUserStats();
      setStats({
        mentorsCount: response.mentors_count || 0,
        scrollsCount: response.scrolls_count || 0,
        streakDays: response.streak_days || 0,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: async () => {
            if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
            await logout();
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.headerTitle}>Profile</Text>
        <Pressable
          style={styles.settingsButton}
          onPress={() => {
            if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          }}
        >
          <Feather name="settings" size={22} color={Colors.white} />
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,
          { paddingBottom: insets.bottom + 100 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View entering={FadeInDown.duration(500)} style={styles.profileSection}>
          <LinearGradient
            colors={[Colors.accent, Colors.accentDark]}
            style={styles.avatar}
          >
            <Feather name="user" size={40} color={Colors.primaryDark} />
          </LinearGradient>
          <Text style={styles.userName}>{user?.full_name || user?.username || 'User'}</Text>
          <Text style={styles.userEmail}>{user?.email || 'user@example.com'}</Text>
          
          <View style={styles.tokenContainer}>
            <LinearGradient
              colors={['rgba(245, 203, 125, 0.15)', 'rgba(245, 203, 125, 0.1)']}
              style={styles.tokenBadge}
            >
              <Feather name="zap" size={16} color={Colors.accent} />
              <Text style={styles.tokenText}>{tokenBalance} Tokens</Text>
            </LinearGradient>
          </View>
        </Animated.View>

        <View style={styles.statsContainer}>
          <StatCard icon="users" label="Mentors" value={stats.mentorsCount} index={0} />
          <StatCard icon="message-circle" label="Scrolls" value={stats.scrollsCount} index={1} />
          <StatCard icon="zap" label="Streak" value={`${stats.streakDays}d`} index={2} />
        </View>

        <Animated.View entering={FadeInRight.delay(400).duration(500)} style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          <View style={styles.settingsList}>
            <SettingItem
              icon="user"
              label="Edit Profile"
              onPress={() => {}}
            />
            <SettingItem
              icon="bell"
              label="Notifications"
              onPress={() => {}}
            />
            <SettingItem
              icon="shield"
              label="Privacy & Security"
              onPress={() => {}}
            />
          </View>
        </Animated.View>

        <Animated.View entering={FadeInRight.delay(500).duration(500)} style={styles.section}>
          <Text style={styles.sectionTitle}>Support</Text>
          <View style={styles.settingsList}>
            <SettingItem
              icon="help-circle"
              label="Help Center"
              onPress={() => {}}
            />
            <SettingItem
              icon="message-square"
              label="Contact Support"
              onPress={() => {}}
            />
            <SettingItem
              icon="info"
              label="About"
              onPress={() => {}}
            />
          </View>
        </Animated.View>

        <Animated.View entering={FadeInRight.delay(600).duration(500)} style={styles.section}>
          <View style={styles.settingsList}>
            <SettingItem
              icon="log-out"
              label="Sign Out"
              onPress={handleLogout}
              showArrow={false}
              destructive
            />
          </View>
        </Animated.View>

        <Text style={styles.version}>EduPath v2.0.0</Text>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.06)',
  },
  headerTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 28,
    color: Colors.white,
  },
  settingsButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 20,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 24,
  },
  profileSection: {
    alignItems: 'center',
    marginBottom: 24,
  },
  avatar: {
    width: 88,
    height: 88,
    borderRadius: 44,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  userName: {
    fontFamily: 'Inter_700Bold',
    fontSize: 22,
    color: Colors.white,
    marginBottom: 4,
  },
  userEmail: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 16,
  },
  tokenContainer: {
    borderRadius: 20,
    overflow: 'hidden',
  },
  tokenBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  tokenText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.accent,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 32,
  },
  statCard: {
    flex: 1,
    borderRadius: 12,
    overflow: 'hidden',
  },
  statGradient: {
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    borderRadius: 12,
  },
  statIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(245, 203, 125, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  statValue: {
    fontFamily: 'Inter_700Bold',
    fontSize: 20,
    color: Colors.white,
    marginBottom: 2,
  },
  statLabel: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: Colors.textSecondary,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.textMuted,
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  settingsList: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    overflow: 'hidden',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.04)',
  },
  settingItemPressed: {
    backgroundColor: 'rgba(255,255,255,0.04)',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  settingIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(245, 203, 125, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingIconDestructive: {
    backgroundColor: 'rgba(255, 107, 107, 0.15)',
  },
  settingLabel: {
    fontFamily: 'Inter_500Medium',
    fontSize: 15,
    color: Colors.white,
  },
  settingLabelDestructive: {
    color: Colors.error,
  },
  version: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: 24,
  },
});

export default ProfileScreen;
