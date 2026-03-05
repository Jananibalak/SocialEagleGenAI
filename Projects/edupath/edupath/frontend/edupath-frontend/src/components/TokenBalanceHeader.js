import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import theme from '../config/theme';

const TokenBalanceHeader = ({ tokenBalance, freeMessagesLeft, onPressBalance }) => {
  const hasTokens = tokenBalance > 0;

  return (
    <LinearGradient
      colors={[theme.colors.primary, theme.colors.primaryDark]}
      style={styles.header}
    >
      <View style={styles.container}>
        <View style={styles.titleContainer}>
          <Text style={styles.title}>EduPath AI Coach</Text>
          <Text style={styles.subtitle}>Your Learning Buddy 🎓</Text>
        </View>

        <TouchableOpacity style={styles.balanceContainer} onPress={onPressBalance}>
          {hasTokens ? (
            <View style={styles.tokenBadge}>
              <Text style={styles.balanceLabel}>Tokens</Text>
              <Text style={styles.balanceValue}>{tokenBalance.toFixed(0)}</Text>
            </View>
          ) : (
            <View style={styles.freeTrialBadge}>
              <Text style={styles.freeTrialLabel}>Free Trial</Text>
              <Text style={styles.freeTrialValue}>
                {freeMessagesLeft} {freeMessagesLeft === 1 ? 'message' : 'messages'} left
              </Text>
            </View>
          )}
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  header: {
    paddingTop: 50,
    paddingBottom: theme.spacing.md,
    paddingHorizontal: theme.spacing.md,
    ...theme.shadows.md,
  },
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  titleContainer: {
    flex: 1,
  },
  title: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  subtitle: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  balanceContainer: {
    marginLeft: theme.spacing.md,
  },
  tokenBadge: {
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    alignItems: 'center',
    minWidth: 80,
  },
  balanceLabel: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.textSecondary,
    fontWeight: '600',
  },
  balanceValue: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginTop: 2,
  },
  freeTrialBadge: {
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.md,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    alignItems: 'center',
  },
  freeTrialLabel: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.background,
    fontWeight: '600',
  },
  freeTrialValue: {
    fontSize: theme.fonts.sizes.sm,
    fontWeight: 'bold',
    color: theme.colors.background,
    marginTop: 2,
  },
});

export default TokenBalanceHeader;