import React from 'react';
import {
  View,
  Text,
  Pressable,
  ScrollView,
  StyleSheet,
  Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  FadeInRight,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import Colors from '../constants/colors';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: '$9.99',
    period: '/month',
    tokens: 100,
    features: [
      '100 AI messages per month',
      'Up to 5 mentors',
      'Basic learning analytics',
      'Email support',
    ],
    isPopular: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$19.99',
    period: '/month',
    tokens: 500,
    features: [
      '500 AI messages per month',
      'Unlimited mentors',
      'Advanced analytics',
      'Priority support',
      'Custom learning paths',
    ],
    isPopular: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    price: '$49.99',
    period: '/month',
    tokens: 2000,
    features: [
      '2000 AI messages per month',
      'Unlimited everything',
      'White-glove support',
      'API access',
      'Team collaboration',
      'Custom integrations',
    ],
    isPopular: false,
  },
];

const PlanCard = ({ plan, index, onSelect }) => {
  return (
    <Animated.View
      entering={FadeInRight.delay(index * 150).duration(600)}
      style={styles.planCardContainer}
    >
      <LinearGradient
        colors={plan.isPopular
          ? [Colors.accent, Colors.accentDark]
          : ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.1)']
        }
        style={styles.planBorder}
      >
        <View style={[styles.planCard, plan.isPopular && styles.planCardPopular]}>
          {plan.isPopular && (
            <View style={styles.popularBadge}>
              <LinearGradient
                colors={[Colors.accent, Colors.accentDark]}
                style={styles.popularBadgeGradient}
              >
                <Feather name="star" size={12} color={Colors.primaryDark} />
                <Text style={styles.popularText}>MOST POPULAR</Text>
              </LinearGradient>
            </View>
          )}

          <Text style={styles.planName}>{plan.name}</Text>
          <View style={styles.priceContainer}>
            <Text style={styles.planPrice}>{plan.price}</Text>
            <Text style={styles.planPeriod}>{plan.period}</Text>
          </View>

          <View style={styles.tokensContainer}>
            <Feather name="zap" size={16} color={Colors.accent} />
            <Text style={styles.tokensText}>{plan.tokens} tokens/month</Text>
          </View>

          <View style={styles.featuresContainer}>
            {plan.features.map((feature, idx) => (
              <View key={idx} style={styles.feature}>
                <Feather name="check" size={16} color={Colors.success} />
                <Text style={styles.featureText}>{feature}</Text>
              </View>
            ))}
          </View>

          <Pressable
            style={styles.selectButton}
            onPress={() => {
              if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
              onSelect(plan);
            }}
          >
            <LinearGradient
              colors={plan.isPopular
                ? [Colors.accent, Colors.accentDark]
                : ['rgba(255,255,255,0.08)', 'rgba(255,255,255,0.08)']
              }
              style={styles.selectButtonGradient}
            >
              <Text style={[
                styles.selectButtonText,
                plan.isPopular && styles.selectButtonTextPopular,
              ]}>
                Choose Plan
              </Text>
            </LinearGradient>
          </Pressable>
        </View>
      </LinearGradient>
    </Animated.View>
  );
};

const PlansScreen = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();

  const handleSelectPlan = (plan) => {
    navigation.navigate('Payment', { plan });
  };

  return (
    <View style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.headerTitle}>Plans</Text>
        <Pressable
          style={styles.closeButton}
          onPress={() => {
            if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            navigation.goBack();
          }}
        >
          <Feather name="x" size={22} color={Colors.white} />
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,
          { paddingBottom: insets.bottom + 40 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View entering={FadeInDown.duration(500)} style={styles.heroSection}>
          <LinearGradient
            colors={[Colors.accent, Colors.accentDark]}
            style={styles.heroIcon}
          >
            <Feather name="zap" size={32} color={Colors.primaryDark} />
          </LinearGradient>
          <Text style={styles.heroTitle}>Choose Your Learning Plan</Text>
          <Text style={styles.heroSubtitle}>
            Unlock unlimited AI-powered learning and accelerate your growth
          </Text>
        </Animated.View>

        <View style={styles.plansContainer}>
          {PLANS.map((plan, index) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              index={index}
              onSelect={handleSelectPlan}
            />
          ))}
        </View>

        <Animated.View entering={FadeInDown.delay(800).duration(500)} style={styles.faqSection}>
          <Text style={styles.faqTitle}>Frequently Asked Questions</Text>
          
          <View style={styles.faqItem}>
            <Feather name="help-circle" size={20} color={Colors.accent} />
            <View style={styles.faqContent}>
              <Text style={styles.faqQuestion}>Can I cancel anytime?</Text>
              <Text style={styles.faqAnswer}>
                Yes! You can cancel your subscription at any time. No hidden fees.
              </Text>
            </View>
          </View>

          <View style={styles.faqItem}>
            <Feather name="help-circle" size={20} color={Colors.accent} />
            <View style={styles.faqContent}>
              <Text style={styles.faqQuestion}>What happens to unused tokens?</Text>
              <Text style={styles.faqAnswer}>
                Unused tokens roll over to the next month, up to 2x your plan limit.
              </Text>
            </View>
          </View>

          <View style={styles.faqItem}>
            <Feather name="help-circle" size={20} color={Colors.accent} />
            <View style={styles.faqContent}>
              <Text style={styles.faqQuestion}>Can I upgrade later?</Text>
              <Text style={styles.faqAnswer}>
                Absolutely! Upgrade or downgrade your plan at any time.
              </Text>
            </View>
          </View>
        </Animated.View>
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
  closeButton: {
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
  heroSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  heroIcon: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  heroTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 24,
    color: Colors.white,
    textAlign: 'center',
    marginBottom: 8,
  },
  heroSubtitle: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  plansContainer: {
    gap: 16,
    marginBottom: 32,
  },
  planCardContainer: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  planBorder: {
    padding: 2,
    borderRadius: 16,
  },
  planCard: {
    backgroundColor: Colors.primary,
    borderRadius: 14,
    padding: 20,
  },
  planCardPopular: {
    backgroundColor: 'rgba(245, 203, 125, 0.05)',
  },
  popularBadge: {
    position: 'absolute',
    top: 20,
    right: 20,
    borderRadius: 12,
    overflow: 'hidden',
  },
  popularBadgeGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  popularText: {
    fontFamily: 'Inter_700Bold',
    fontSize: 10,
    color: Colors.primaryDark,
    letterSpacing: 0.5,
  },
  planName: {
    fontFamily: 'Inter_700Bold',
    fontSize: 22,
    color: Colors.white,
    marginBottom: 8,
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 12,
  },
  planPrice: {
    fontFamily: 'Inter_700Bold',
    fontSize: 36,
    color: Colors.white,
  },
  planPeriod: {
    fontFamily: 'Inter_400Regular',
    fontSize: 16,
    color: Colors.textSecondary,
    marginLeft: 4,
  },
  tokensContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: 'rgba(245, 203, 125, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    alignSelf: 'flex-start',
    marginBottom: 20,
  },
  tokensText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 13,
    color: Colors.accent,
  },
  featuresContainer: {
    gap: 12,
    marginBottom: 24,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  featureText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    flex: 1,
  },
  selectButton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  selectButtonGradient: {
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  selectButtonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.white,
  },
  selectButtonTextPopular: {
    color: Colors.primaryDark,
  },
  faqSection: {
    gap: 16,
  },
  faqTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 20,
    color: Colors.white,
    marginBottom: 8,
  },
  faqItem: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: 'rgba(255,255,255,0.04)',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  faqContent: {
    flex: 1,
  },
  faqQuestion: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.white,
    marginBottom: 4,
  },
  faqAnswer: {
    fontFamily: 'Inter_400Regular',
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
});

export default PlansScreen;
