import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { format } from 'date-fns';
import theme from '../config/theme';

const ChatBubble = ({ message, sender, timestamp, sources }) => {
  const isUser = sender === 'user';

  return (
    <View style={[styles.container, isUser && styles.userContainer]}>
      {/* AI Avatar & Name */}
      {!isUser && (
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>🤖</Text>
          </View>
        </View>
      )}
      
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.aiBubble]}>
        {/* Message Text */}
        <Text style={[styles.messageText, isUser ? styles.userText : styles.aiText]}>
          {message}
        </Text>
        
        {/* Sources (for AI messages) */}
        {!isUser && sources && (sources.knowledge_graph?.length > 0 || sources.web_search?.length > 0) && (
          <View style={styles.sourcesContainer}>
            {sources.knowledge_graph?.length > 0 && (
              <View style={styles.sourceSection}>
                <Text style={styles.sourcesLabel}>📚 From Your Materials</Text>
                <View style={styles.sourcesList}>
                  {sources.knowledge_graph.slice(0, 3).map((source, index) => (
                    <View key={index} style={styles.sourceChip}>
                      <Text style={styles.sourceChipText} numberOfLines={1}>
                        {source}
                      </Text>
                    </View>
                  ))}
                </View>
              </View>
            )}
            
            {sources.web_search?.length > 0 && (
              <View style={styles.sourceSection}>
                <Text style={styles.sourcesLabel}>🌐 From Web</Text>
                <View style={styles.sourcesList}>
                  {sources.web_search.slice(0, 2).map((source, index) => (
                    <View key={index} style={styles.sourceChip}>
                      <Text style={styles.sourceChipText} numberOfLines={1}>
                        {source}
                      </Text>
                    </View>
                  ))}
                </View>
              </View>
            )}
          </View>
        )}
        
        {/* Timestamp */}
        <Text style={styles.timestamp}>
          {format(new Date(timestamp), 'h:mm a')}
        </Text>
      </View>

      {/* User Avatar */}
      {isUser && (
        <View style={styles.avatarContainer}>
          <View style={[styles.avatar, styles.userAvatar]}>
            <Text style={styles.avatarText}>👤</Text>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginVertical: theme.spacing.sm,
    alignItems: 'flex-end',
    paddingHorizontal: theme.spacing.sm,
  },
  userContainer: {
    flexDirection: 'row-reverse',
  },
  avatarContainer: {
    marginHorizontal: theme.spacing.xs,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.secondary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  userAvatar: {
    backgroundColor: theme.colors.primary,
  },
  avatarText: {
    fontSize: 18,
  },
  bubble: {
    maxWidth: '75%',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.xl,
    ...theme.shadows.sm,
  },
  userBubble: {
    backgroundColor: theme.colors.primary,
    borderBottomRightRadius: theme.borderRadius.sm,
  },
  aiBubble: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderBottomLeftRadius: theme.borderRadius.sm,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  messageText: {
    fontSize: theme.fonts.sizes.md,
    lineHeight: 22,
  },
  userText: {
    color: theme.colors.secondaryDeep,
  },
  aiText: {
    color: theme.colors.text,
  },
  timestamp: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.textLight,
    marginTop: theme.spacing.xs,
    alignSelf: 'flex-end',
  },
  sourcesContainer: {
    marginTop: theme.spacing.md,
    paddingTop: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.divider,
  },
  sourceSection: {
    marginBottom: theme.spacing.sm,
  },
  sourcesLabel: {
    fontSize: theme.fonts.sizes.xs,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
  sourcesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.xs,
  },
  sourceChip: {
    backgroundColor: theme.colors.background,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 4,
    borderRadius: theme.borderRadius.full,
    borderWidth: 1,
    borderColor: theme.colors.border,
    maxWidth: 150,
  },
  sourceChipText: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.textSecondary,
  },
});

export default ChatBubble;