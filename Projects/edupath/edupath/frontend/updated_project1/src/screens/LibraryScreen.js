import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  Pressable,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  Platform,
  Alert,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather, Ionicons } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  FadeInUp,
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  withSequence,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService } from '../services/api';
import Colors from '../constants/colors';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

const MentorCard = ({ mentor, index, onDelete, onPress }) => {
  const iconMap = {
    '📚': 'book-open',
    '💻': 'cpu',
    '🎨': 'feather',
    '🔬': 'activity',
    '📊': 'bar-chart-2',
    '🎵': 'music',
    '⚡': 'zap',
    '🌍': 'globe',
    '🏆': 'award',
    '🧠': 'cpu',
  };
  const iconName = iconMap[mentor.emoji] || 'book-open';
  
  const getTimeAgo = (dateStr) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'now';
    if (mins < 60) return `${mins}m`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h`;
    const days = Math.floor(hrs / 24);
    if (days < 7) return `${days}d`;
    return `${Math.floor(days / 7)}w`;
  };

  const timeAgo = getTimeAgo(mentor.created_at);

  const handlePress = () => {
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    onPress(mentor);
  };

  const handleLongPress = () => {
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    if (Platform.OS === 'web') {
      if (confirm(`Delete "${mentor.name}"?`)) onDelete(mentor.id);
    } else {
      Alert.alert('Delete Mentor', `Remove "${mentor.name}"?`, [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => onDelete(mentor.id) },
      ]);
    }
  };

  return (
    <Animated.View entering={FadeInDown.delay(index * 80).duration(500)}>
      <Pressable
        style={({ pressed }) => [styles.mentorCard, pressed && styles.mentorCardPressed]}
        onPress={handlePress}
        onLongPress={handleLongPress}
      >
        <LinearGradient
          colors={[Colors.accent, Colors.accentDark]}
          style={styles.mentorAvatar}
        >
          <Feather name={iconName} size={24} color={Colors.primaryDark} />
        </LinearGradient>

        <View style={styles.mentorInfo}>
          <View style={styles.mentorNameRow}>
            <Text style={styles.mentorName} numberOfLines={1}>{mentor.name}</Text>
            <Text style={styles.mentorTime}>{timeAgo}</Text>
          </View>
          <Text style={styles.mentorTopic} numberOfLines={1}>{mentor.topic}</Text>
          <Text style={styles.mentorLastMsg} numberOfLines={1}>
            {mentor.last_message || 'Start your learning journey...'}
          </Text>
        </View>

        <View style={styles.mentorBadges}>
          {mentor.scrolls_count > 0 && (
            <View style={styles.badge}>
              <Feather name="message-circle" size={11} color={Colors.accent} />
              <Text style={styles.badgeText}>{mentor.scrolls_count}</Text>
            </View>
          )}
          {mentor.streak > 0 && (
            <View style={styles.badge}>
              <Feather name="zap" size={11} color={Colors.success} />
              <Text style={styles.badgeText}>{mentor.streak}</Text>
            </View>
          )}
        </View>

        <Feather name="chevron-right" size={18} color={Colors.textMuted} />
      </Pressable>
    </Animated.View>
  );
};

const EmptyState = ({ onCreateMentor }) => {
  const floatY = useSharedValue(0);

  useEffect(() => {
    floatY.value = withRepeat(
      withSequence(
        withTiming(-8, { duration: 1500 }),
        withTiming(8, { duration: 1500 })
      ),
      -1,
      true
    );
  }, []);

  const floatStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: floatY.value }],
  }));

  return (
    <View style={styles.emptyContainer}>
      <Animated.View style={[styles.emptyIconContainer, floatStyle]}>
        <LinearGradient
          colors={[Colors.accent, Colors.accentDark]}
          style={styles.emptyIcon}
        >
          <Feather name="book-open" size={40} color={Colors.primaryDark} />
        </LinearGradient>
      </Animated.View>
      <Text style={styles.emptyTitle}>No Mentors Yet</Text>
      <Text style={styles.emptySubtitle}>
        Create your first AI mentor to begin your learning journey
      </Text>
      <Pressable
        style={styles.emptyButton}
        onPress={() => {
          if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          onCreateMentor();
        }}
      >
        <LinearGradient
          colors={[Colors.accent, Colors.accentDark]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.emptyButtonGradient}
        >
          <Feather name="plus" size={18} color={Colors.primaryDark} />
          <Text style={styles.emptyButtonText}>Create Mentor</Text>
        </LinearGradient>
      </Pressable>
    </View>
  );
};

const LibraryScreen = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [tokenBalance, setTokenBalance] = useState(100);

  useFocusEffect(
    React.useCallback(() => {
      loadMentors();
    }, [])
  );

  const loadMentors = async () => {
    try {
      setLoading(true);
      const response = await apiService.listMentors();
      const mentorList = response.mentors || [];
      setMentors(mentorList);
    } catch (error) {
      console.error('Error loading mentors:', error);
      setMentors([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadMentors();
  };

  const handleCreateNewMentor = () => {
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    navigation.navigate('CreateMentor');
  };

  const handleOpenMentor = (mentor) => {
    navigation.navigate('MentorChat', {
      mentorId: mentor.id,
      mentorName: mentor.name,
    });
  };

  const handleDeleteMentor = async (mentorId) => {
    try {
      await apiService.deleteMentor(mentorId);
      setMentors(mentors.filter(m => m.id !== mentorId));
      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      console.error('Error deleting mentor:', error);
      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  };

  if (loading && !refreshing) {
    return (
      <View style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={Colors.accent} />
          <Text style={styles.loadingText}>Loading your mentors...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <View>
          <Text style={styles.headerTitle}>Library</Text>
          <Text style={styles.headerSubtitle}>
            {mentors.length} Mentor{mentors.length !== 1 ? 's' : ''}
          </Text>
        </View>
        <View style={styles.headerRight}>
          <View style={styles.tokenBadge}>
            <Ionicons name="flash" size={14} color={Colors.accent} />
            <Text style={styles.tokenText}>{tokenBalance}</Text>
          </View>
          <Pressable
            style={styles.addBtn}
            onPress={handleCreateNewMentor}
          >
            <Feather name="plus" size={22} color={Colors.accent} />
          </Pressable>
        </View>
      </View>

      <FlatList
        data={mentors}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item, index }) => (
          <MentorCard
            mentor={item}
            index={index}
            onDelete={handleDeleteMentor}
            onPress={handleOpenMentor}
          />
        )}
        contentContainerStyle={[
          styles.listContent,
          mentors.length === 0 && styles.listEmpty,
          { paddingBottom: 100 },
        ]}
        ListEmptyComponent={!loading ? <EmptyState onCreateMentor={handleCreateNewMentor} /> : null}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={Colors.accent}
            colors={[Colors.accent]}
          />
        }
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 14,
    fontFamily: 'Inter_400Regular',
    color: Colors.textSecondary,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
  headerSubtitle: {
    fontFamily: 'Inter_400Regular',
    fontSize: 13,
    color: Colors.textMuted,
    marginTop: 2,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  tokenBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(245, 203, 125, 0.12)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 20,
  },
  tokenText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.accent,
  },
  addBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(245, 203, 125, 0.12)',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingTop: 8,
  },
  listEmpty: {
    flex: 1,
    justifyContent: 'center',
  },
  mentorCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 16,
    padding: 14,
    marginVertical: 4,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  mentorCardPressed: {
    backgroundColor: 'rgba(255,255,255,0.08)',
  },
  mentorAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  mentorInfo: {
    flex: 1,
    marginRight: 8,
  },
  mentorNameRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  mentorName: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.white,
    flex: 1,
  },
  mentorTime: {
    fontFamily: 'Inter_400Regular',
    fontSize: 11,
    color: Colors.textMuted,
    marginLeft: 8,
  },
  mentorTopic: {
    fontFamily: 'Inter_500Medium',
    fontSize: 13,
    color: Colors.accent,
    marginBottom: 2,
  },
  mentorLastMsg: {
    fontFamily: 'Inter_400Regular',
    fontSize: 13,
    color: Colors.textSecondary,
  },
  mentorBadges: {
    flexDirection: 'column',
    gap: 4,
    marginRight: 6,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3,
    backgroundColor: 'rgba(255,255,255,0.06)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  badgeText: {
    fontFamily: 'Inter_500Medium',
    fontSize: 11,
    color: Colors.textSecondary,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyIconContainer: {
    marginBottom: 24,
  },
  emptyIcon: {
    width: 88,
    height: 88,
    borderRadius: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 22,
    color: Colors.white,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 28,
  },
  emptyButton: {
    borderRadius: 14,
    overflow: 'hidden',
  },
  emptyButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 14,
  },
  emptyButtonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.primaryDark,
  },
});

export default LibraryScreen;
