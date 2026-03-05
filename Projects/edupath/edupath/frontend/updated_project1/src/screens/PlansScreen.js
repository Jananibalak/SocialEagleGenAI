import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import theme from '../config/theme';
import TopNavbar from '../components/TopNavbar';
import {
  Pressable,
  Platform
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather, Ionicons } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  FadeInUp,
  FadeInRight,
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withSequence,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import Colors from '../constants/colors';

const PlansScreen = ({ navigation }) => {
  const { user, tokenBalance, loadTokenBalance } = useAuth();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);

  useEffect(() => {
    loadPlans();
    loadBalance();
  }, []);

  const loadPlans = async () => {
    try {
      const response = await apiService.getPlans();
      setPlans(response.token_packages || []);
    } catch (error) {
      console.error('Error loading plans:', error);
      Alert.alert('Error', 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const loadBalance = async () => {
    try {
      await loadTokenBalance();
    } catch (error) {
      console.error('Error loading balance:', error);
    }
  };

  const handleSelectPlan = async (packageId) => {
    if (!user) {
      Alert.alert('Error', 'Please login first');
      return;
    }

    setPurchasing(true);

    try {
      const response = await apiService.createTokenOrder(packageId);
      
      navigation.navigate('Payment', {
        orderId: response.order_id,
        amount: response.amount,
        packageId: packageId,
      });
      
    } catch (error) {
      console.error('Error creating order:', error);
      
      if (error.response?.status === 401) {
        Alert.alert('Session Expired', 'Please login again');
      } else {
        Alert.alert('Error', error.response?.data?.error || 'Failed to create order');
      }
    } finally {
      setPurchasing(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <TopNavbar title="Tokens" />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TopNavbar title="Tokens" />
      
      <ScrollView contentContainerStyle={styles.content}>
        {/* Balance Card */}
        <View style={styles.balanceCard}>
          <Text style={styles.balanceLabel}>Current Balance</Text>
          <View style={styles.balanceRow}>
            <Text style={styles.balanceIcon}>💰</Text>
            <Text style={styles.balanceAmount}>
              {tokenBalance !== null && tokenBalance !== undefined ? tokenBalance : 0}
            </Text>
            <Text style={styles.balanceText}>Tokens</Text>
          </View>
          <TouchableOpacity 
            style={styles.refreshButton}
            onPress={loadBalance}
          >
            <Text style={styles.refreshButtonText}>🔄 Refresh</Text>
          </TouchableOpacity>
        </View>

        {/* Plans */}
        <Text style={styles.sectionTitle}>Choose Your Plan</Text>
        
        {plans.map((plan, index) => (
          <View 
            key={plan.id} 
            style={[
              styles.planCard,
              plan.bonus_percentage > 0 && styles.planCardFeatured
            ]}
          >
            {plan.bonus_percentage > 0 && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>
                  🎁 +{plan.bonus_percentage}% Bonus
                </Text>
              </View>
            )}
            
            <View style={styles.planHeader}>
              <Text style={styles.planName}>{plan.name}</Text>
              <View style={styles.priceContainer}>
                <Text style={styles.currency}>₹</Text>
                <Text style={styles.planPrice}>{plan.price_inr}</Text>
              </View>
            </View>

            <View style={styles.planContent}>
              <View style={styles.tokenInfo}>
                <Text style={styles.tokenAmount}>{plan.tokens}</Text>
                <Text style={styles.tokenLabel}>Tokens</Text>
              </View>

              {plan.bonus_tokens > 0 && (
                <View style={styles.bonusInfo}>
                  <Text style={styles.bonusText}>
                    + {plan.bonus_tokens} bonus tokens
                  </Text>
                </View>
              )}
            </View>

            <TouchableOpacity
              style={[
                styles.selectButton,
                plan.bonus_percentage > 0 && styles.selectButtonFeatured
              ]}
              onPress={() => handleSelectPlan(plan.id)}
              disabled={purchasing}
            >
              {purchasing ? (
                <ActivityIndicator color={theme.colors.secondaryDeep} />
              ) : (
                <Text style={styles.selectButtonText}>Purchase</Text>
              )}
            </TouchableOpacity>
          </View>
        ))}

        {/* Info */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>💡 Token Usage</Text>
          <View style={styles.infoList}>
            <Text style={styles.infoItem}>• Chat message: 1 token</Text>
            <Text style={styles.infoItem}>• Daily check-in: 0.5 tokens</Text>
            <Text style={styles.infoItem}>• Progress report: 5 tokens</Text>
          </View>
        </View>
      </ScrollView>
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
  content: {
    padding: theme.spacing.lg,
  },
  balanceCard: {
    backgroundColor: theme.colors.secondary,
    borderRadius: theme.borderRadius.xxl,
    padding: theme.spacing.xl,
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
    ...theme.shadows.lg,
  },
  balanceLabel: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.textInverse,
    opacity: 0.8,
    marginBottom: theme.spacing.sm,
  },
  balanceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: theme.spacing.sm,
  },
  balanceIcon: {
    fontSize: 32,
    marginRight: theme.spacing.sm,
  },
  balanceAmount: {
    fontSize: 48,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.primary,
    marginRight: theme.spacing.xs,
  },
  balanceText: {
    fontSize: theme.fonts.sizes.lg,
    color: theme.colors.textInverse,
  },
  refreshButton: {
    marginTop: theme.spacing.md,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.secondaryDeep,
    borderRadius: theme.borderRadius.full,
  },
  refreshButtonText: {
    fontSize: theme.fonts.sizes.sm,
    fontWeight: theme.fonts.weights.medium,
    color: theme.colors.textInverse,
  },
  sectionTitle: {
    fontSize: theme.fonts.sizes.xl,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.lg,
  },
  planCard: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    position: 'relative',
    ...theme.shadows.md,
  },
  planCardFeatured: {
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  badge: {
    position: 'absolute',
    top: -12,
    right: 20,
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.xs,
    borderRadius: theme.borderRadius.full,
    ...theme.shadows.sm,
  },
  badgeText: {
    fontSize: theme.fonts.sizes.xs,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.secondaryDeep,
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  planName: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.text,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  currency: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.text,
  },
  planPrice: {
    fontSize: theme.fonts.sizes.xxl,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.text,
    marginLeft: 2,
  },
  planContent: {
    marginBottom: theme.spacing.md,
  },
  tokenInfo: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: theme.spacing.xs,
  },
  tokenAmount: {
    fontSize: theme.fonts.sizes.xl,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.primary,
    marginRight: theme.spacing.xs,
  },
  tokenLabel: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.textSecondary,
  },
  bonusInfo: {
    backgroundColor: theme.colors.background,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 4,
    borderRadius: theme.borderRadius.full,
    alignSelf: 'flex-start',
  },
  bonusText: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.success,
    fontWeight: theme.fonts.weights.semibold,
  },
  selectButton: {
    backgroundColor: theme.colors.secondary,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.md,
    alignItems: 'center',
  },
  selectButtonFeatured: {
    backgroundColor: theme.colors.primary,
  },
  selectButtonText: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.textInverse,
  },
  infoCard: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.lg,
    marginTop: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  infoTitle: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: theme.fonts.weights.semibold,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  infoList: {
    gap: theme.spacing.xs,
  },
  infoItem: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
});

export default PlansScreen;