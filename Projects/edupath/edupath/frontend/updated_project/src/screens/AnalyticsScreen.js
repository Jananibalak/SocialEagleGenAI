import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Pressable,
  useWindowDimensions,
} from 'react-native';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService } from '../services/api';
import Colors from '../constants/colors';

// ✅ Mobile-responsive StatCard
const StatCard = ({ icon, label, value, subtitle, index }) => {
  const { width } = useWindowDimensions();
  const isSmallScreen = width < 400;
  
  return (
    <Animated.View 
      entering={FadeInDown.delay(index * 100).duration(500)}
      style={[styles.statCard, isSmallScreen && styles.statCardSmall]}
    >
      <LinearGradient
        colors={['rgba(255,255,255,0.08)', 'rgba(255,255,255,0.04)']}
        style={styles.statGradient}
      >
        <View style={styles.statIconContainer}>
          <Feather name={icon} size={isSmallScreen ? 20 : 24} color={Colors.accent} />
        </View>
        <Text style={[styles.statValue, isSmallScreen && styles.statValueSmall]}>{value}</Text>
        <Text style={[styles.statLabel, isSmallScreen && styles.statLabelSmall]}>{label}</Text>
        {subtitle && <Text style={styles.statSubtitle}>{subtitle}</Text>}
      </LinearGradient>
    </Animated.View>
  );
};

// ✅ Mobile-friendly InsightCard
const InsightCard = ({ insight, index }) => {
  const iconColors = {
    achievement: Colors.accent,
    positive: '#4ade80',
    motivation: '#60a5fa',
    pattern: '#a78bfa',
    suggestion: '#fbbf24',
    warning: '#f87171',
    reminder: '#fb923c',
    info: '#38bdf8',
    celebration: Colors.accent,
    encouragement: '#4ade80',
  };

  return (
    <Animated.View 
      entering={FadeInDown.delay(index * 100).duration(500)}
      style={styles.insightCard}
    >
      <View style={[styles.insightIcon, { backgroundColor: `${iconColors[insight.type] || Colors.accent}20` }]}>
        <Feather name={insight.icon} size={18} color={iconColors[insight.type] || Colors.accent} />
      </View>
      <View style={styles.insightContent}>
        <Text style={styles.insightTitle}>{insight.title}</Text>
        <Text style={styles.insightMessage}>{insight.message}</Text>
      </View>
    </Animated.View>
  );
};

// ✅ Compact MentorStatCard for mobile
const MentorStatCard = ({ mentor }) => {
  const statusColors = {
    active: '#4ade80',
    recent: '#fbbf24',
    inactive: '#94a3b8',
    completed: '#a78bfa',
    paused: '#fb923c',
  };

  const statusIcons = {
    active: 'check-circle',
    recent: 'clock',
    inactive: 'moon',
    completed: 'award',
    paused: 'pause-circle',
  };

  return (
    <View style={styles.mentorStatCard}>
      {/* Header */}
      <View style={styles.mentorHeader}>
        <View style={styles.mentorLeft}>
          <Text style={styles.mentorEmoji}>{mentor.mentor_emoji}</Text>
          <View style={styles.mentorInfo}>
            <Text style={styles.mentorName} numberOfLines={1}>{mentor.mentor_name}</Text>
            <Text style={styles.mentorTopic} numberOfLines={1}>{mentor.topic}</Text>
          </View>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: `${statusColors[mentor.status]}20` }]}>
          <Feather name={statusIcons[mentor.status]} size={10} color={statusColors[mentor.status]} />
        </View>
      </View>

      {/* Stats Row */}
      <View style={styles.mentorStatsRow}>
        <View style={styles.mentorStat}>
          <Text style={styles.mentorStatValue}>{mentor.message_count}</Text>
          <Text style={styles.mentorStatLabel}>msgs</Text>
        </View>
        <View style={styles.mentorStat}>
          <Text style={[styles.mentorStatValue, mentor.current_streak > 0 && { color: Colors.accent }]}>
            {mentor.current_streak > 0 ? '🔥' : ''}{mentor.current_streak}
          </Text>
          <Text style={styles.mentorStatLabel}>streak</Text>
        </View>
        <View style={styles.mentorStat}>
          <Text style={styles.mentorStatValue}>{mentor.knowledge_points || 0}</Text>
          <Text style={styles.mentorStatLabel}>points</Text>
        </View>
      </View>

      {/* Progress bar if plan exists */}
      {mentor.target_days > 0 && (
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${mentor.progress_percentage}%` }]} />
          </View>
          <Text style={styles.progressText}>
            Day {mentor.current_day}/{mentor.target_days} • {mentor.progress_percentage}%
          </Text>
        </View>
      )}
    </View>
  );
};

const AnalyticsScreen = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { width } = useWindowDimensions();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useFocusEffect(
    React.useCallback(() => {
      loadAnalytics();
    }, [])
  );

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiService.getAnalytics();
      
      if (response.success) {
        setAnalytics(response.analytics);
      } else {
        setError('Failed to load analytics');
      }
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError('Failed to load analytics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.accent} />
        <Text style={styles.loadingText}>Loading insights...</Text>
      </View>
    );
  }

  if (error || !analytics) {
    return (
      <View style={styles.errorContainer}>
        <Feather name="alert-circle" size={48} color={Colors.error} />
        <Text style={styles.errorText}>{error || 'No data available'}</Text>
        <Pressable style={styles.retryButton} onPress={loadAnalytics}>
          <Text style={styles.retryText}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  const isSmallScreen = width < 400;

  return (
    <View style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.headerTitle}>Analytics</Text>
        <Feather name="bar-chart-2" size={22} color={Colors.white} />
      </View>

      <ScrollView
        contentContainerStyle={[styles.scrollContent, { paddingBottom: insets.bottom + 100 }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Overview Stats - 2x2 Grid */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Overview</Text>
          <View style={styles.statsGrid}>
            <StatCard icon="message-circle" label="Messages" value={analytics.total_messages || 0} index={0} />
            <StatCard icon="zap" label="Points" value={analytics.total_knowledge_points || 0} index={1} />
            <StatCard icon="calendar" label="Active Days" value={analytics.active_days || 0} index={2} />
            <StatCard icon="users" label="Mentors" value={`${analytics.activity_summary?.active_mentors || 0}/${analytics.mentors_count || 0}`} index={3} />
          </View>
        </View>

        {/* LLM Insights */}
        {analytics.llm_insights && analytics.llm_insights.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>💡 AI Insights</Text>
            {analytics.llm_insights.map((insight, index) => (
              <InsightCard key={index} insight={insight} index={index} />
            ))}
          </View>
        )}

        {/* Standard Insights */}
        {analytics.global_insights && analytics.global_insights.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🎯 Your Progress</Text>
            {analytics.global_insights.map((insight, index) => (
              <InsightCard key={index} insight={insight} index={index} />
            ))}
          </View>
        )}

        {/* Mentors */}
        {analytics.mentor_stats && analytics.mentor_stats.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📚 Your Mentors</Text>
            {analytics.mentor_stats.map((mentor) => (
              <MentorStatCard key={mentor.mentor_id} mentor={mentor} />
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primaryDark,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 16,
    backgroundColor: Colors.primary,
  },
  headerTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 28,
    color: Colors.white,
  },
  scrollContent: {
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.primaryDark,
  },
  loadingText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 12,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.primaryDark,
    padding: 40,
  },
  errorText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 16,
    color: Colors.error,
    marginTop: 16,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 20,
    backgroundColor: Colors.accent,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.primaryDark,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.white,
    marginBottom: 12,
  },
  
  // ✅ Responsive Stats Grid (2x2)
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  statCard: {
    width: '48%',
    borderRadius: 12,
    overflow: 'hidden',
  },
  statCardSmall: {
    width: '48%',
  },
  statGradient: {
    padding: 12,
    alignItems: 'center',
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
    fontSize: 24,
    color: Colors.white,
    marginBottom: 2,
  },
  statValueSmall: {
    fontSize: 20,
  },
  statLabel: {
    fontFamily: 'Inter_500Medium',
    fontSize: 12,
    color: Colors.textSecondary,
  },
  statLabelSmall: {
    fontSize: 11,
  },
  statSubtitle: {
    fontFamily: 'Inter_400Regular',
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 2,
  },
  
  // Insight Cards
  insightCard: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  insightIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  insightContent: {
    flex: 1,
  },
  insightTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.white,
    marginBottom: 2,
  },
  insightMessage: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: Colors.textSecondary,
    lineHeight: 16,
  },
  
  // Mentor Cards
  mentorStatCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  mentorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  mentorLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  mentorEmoji: {
    fontSize: 28,
    marginRight: 10,
  },
  mentorInfo: {
    flex: 1,
  },
  mentorName: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.white,
    marginBottom: 2,
  },
  mentorTopic: {
    fontFamily: 'Inter_400Regular',
    fontSize: 11,
    color: Colors.textSecondary,
  },
  statusBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mentorStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  mentorStat: {
    alignItems: 'center',
  },
  mentorStatValue: {
    fontFamily: 'Inter_700Bold',
    fontSize: 16,
    color: Colors.white,
  },
  mentorStatLabel: {
    fontFamily: 'Inter_400Regular',
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 2,
  },
  progressContainer: {
    marginTop: 10,
  },
  progressBar: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: Colors.accent,
  },
  progressText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 4,
    textAlign: 'center',
  },
});

export default AnalyticsScreen;