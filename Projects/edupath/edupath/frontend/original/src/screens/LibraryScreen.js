import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { apiService } from '../services/api';
import theme from '../config/theme';
import TopNavbar from '../components/TopNavbar';

const LibraryScreen = () => {
  const navigation = useNavigation();
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    React.useCallback(() => {
      console.log('📚 Library screen focused, loading mentors...');
      loadMentors();
    }, [])
  );

  const loadMentors = async () => {
    try {
      setLoading(true);
      console.log('🔄 Fetching mentors from API...');
      
      const response = await apiService.listMentors();
      const mentorList = response.mentors || [];
      
      console.log(`✅ Mentors loaded: ${mentorList.length} mentors`);
      setMentors(mentorList);
    } catch (error) {
      console.error('❌ Error loading mentors:', error);
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
    navigation.navigate('CreateMentor');
  };

  const handleOpenMentor = (mentor) => {
    console.log('📖 Opening mentor:', mentor.name);
    navigation.navigate('MentorChat', { 
      mentorId: mentor.id, 
      mentorName: mentor.name 
    });
  };

  const renderMentorCard = ({ item }) => (
    <TouchableOpacity
      style={styles.mentorCard}
      onPress={() => handleOpenMentor(item)}
      activeOpacity={0.8}
    >
      {/* Avatar */}
      <View style={styles.avatarCircle}>
        <Text style={styles.avatarEmoji}>{item.emoji}</Text>
      </View>

      {/* Content - ✅ FIX: Proper flexbox */}
      <View style={styles.cardContent}>
        <View style={styles.cardHeader}>
          <Text style={styles.mentorName} numberOfLines={1}>
            {item.name}
          </Text>
          <Text style={styles.timestamp}>
            {new Date(item.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </Text>
        </View>

        <Text style={styles.mentorTopic} numberOfLines={1}>
          {item.topic}
        </Text>

        <Text style={styles.lastMessage} numberOfLines={2}>
          {item.last_message || 'Start your learning journey...'}
        </Text>

        {/* Stats */}
        <View style={styles.statsRow}>
          <View style={styles.statBadge}>
            <Text style={styles.statIcon}>📜</Text>
            <Text style={styles.statText}>{item.scrolls_count || 0}</Text>
          </View>
          
          {item.streak > 0 && (
            <View style={styles.statBadge}>
              <Text style={styles.statIcon}>🔥</Text>
              <Text style={styles.statText}>{item.streak}</Text>
            </View>
          )}
        </View>
      </View>

      {/* Arrow */}
      <View style={styles.arrowContainer}>
        <Text style={styles.arrow}>›</Text>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyEmoji}>📚</Text>
      <Text style={styles.emptyTitle}>Your Library is Empty</Text>
      <Text style={styles.emptySubtitle}>
        Create your first mentor to begin your learning journey
      </Text>
      <TouchableOpacity
        style={styles.createButton}
        onPress={handleCreateNewMentor}
      >
        <Text style={styles.createButtonText}>+ Create Mentor</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.container}>
        <TopNavbar title="Library" />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={styles.loadingText}>Loading your mentors...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TopNavbar title="Library" />

      {/* Header Actions */}
      <View style={styles.headerActions}>
        <Text style={styles.headerTitle}>
          {mentors.length} {mentors.length === 1 ? 'Mentor' : 'Mentors'}
        </Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={handleCreateNewMentor}
        >
          <Text style={styles.addButtonText}>+ New</Text>
        </TouchableOpacity>
      </View>

      {/* Mentor List */}
      <FlatList
        data={mentors}
        renderItem={renderMentorCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={mentors.length === 0 ? styles.emptyListContent : styles.listContent}
        ListEmptyComponent={renderEmptyState}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={theme.colors.primary}
            colors={[theme.colors.primary]}
          />
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: theme.spacing.md,
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.textSecondary,
  },
  headerActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    backgroundColor: theme.colors.backgroundSecondary,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  headerTitle: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.text,
  },
  addButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.lg,
    ...theme.shadows.sm,
  },
  addButtonText: {
    fontSize: theme.fonts.sizes.sm,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.secondaryDeep,
  },
  listContent: {
    padding: theme.spacing.lg,
  },
  emptyListContent: {
    flexGrow: 1,
  },
  mentorCard: {
    flexDirection: 'row',  // ✅ CRITICAL: Horizontal layout
    alignItems: 'center',
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    ...theme.shadows.md,
  },
  avatarCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: theme.spacing.md,  // ✅ Space between avatar and content
    flexShrink: 0,  // ✅ Prevent shrinking
  },
  avatarEmoji: {
    fontSize: 32,
  },
  cardContent: {
    flex: 1,  // ✅ CRITICAL: Takes remaining space
    minWidth: 0,  // ✅ Allows text to wrap
  },
  cardHeader: {
    flexDirection: 'row',  // ✅ Name and date in row
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.xs,
  },
  mentorName: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.text,
    flex: 1,  // ✅ Take space, but allow wrapping
    marginRight: theme.spacing.sm,
  },
  timestamp: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.textLight,
    flexShrink: 0,  // ✅ Never shrink
  },
  mentorTopic: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.secondary,
    fontWeight: theme.fonts.weights.medium,
    marginBottom: theme.spacing.xs,
  },
  lastMessage: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.textSecondary,
    lineHeight: 18,
    marginBottom: theme.spacing.sm,
  },
  statsRow: {
    flexDirection: 'row',
    gap: theme.spacing.sm,
    flexWrap: 'wrap',  // ✅ Allow wrapping if needed
  },
  statBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 4,
    borderRadius: theme.borderRadius.full,
  },
  statIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  statText: {
    fontSize: theme.fonts.sizes.xs,
    fontWeight: theme.fonts.weights.medium,
    color: theme.colors.textSecondary,
  },
  arrowContainer: {
    marginLeft: theme.spacing.sm,
    flexShrink: 0,  // ✅ Never shrink
  },
  arrow: {
    fontSize: 28,
    color: theme.colors.textLight,
    fontWeight: theme.fonts.weights.light,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xxxl,
  },
  emptyEmoji: {
    fontSize: 80,
    marginBottom: theme.spacing.lg,
  },
  emptyTitle: {
    fontSize: theme.fonts.sizes.xxl,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
    lineHeight: 22,
  },
  createButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.xxl,
    paddingVertical: theme.spacing.lg,
    borderRadius: theme.borderRadius.xl,
    ...theme.shadows.lg,
  },
  createButtonText: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.secondaryDeep,
  },
});

export default LibraryScreen;