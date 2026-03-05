import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  StyleSheet,
  Platform,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withSequence,
  withTiming,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import Colors from '../constants/colors';
import { showAlert } from '../utils/alert';
const SuccessAnimation = () => {
  const scale = useSharedValue(0);
  const rotation = useSharedValue(0);

  useEffect(() => {
    scale.value = withSpring(1, { damping: 8 });
    rotation.value = withSpring(360, { damping: 12 });
  }, []);

  const animStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { rotate: `${rotation.value}deg` },
    ],
  }));

  return (
    <Animated.View style={[styles.successContainer, animStyle]}>
      <LinearGradient
        colors={[Colors.success, '#2eb89e']}
        style={styles.successCircle}
      >
        <Feather name="check" size={48} color={Colors.white} />
      </LinearGradient>
    </Animated.View>
  );
};

const PaymentScreen = ({ route }) => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const plan = route.params?.plan;

  const [cardNumber, setCardNumber] = useState('');
  const [cardName, setCardName] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const buttonScale = useSharedValue(1);

  const formatCardNumber = (text) => {
    const cleaned = text.replace(/\s/g, '');
    const formatted = cleaned.match(/.{1,4}/g)?.join(' ') || cleaned;
    return formatted.substring(0, 19);
  };

  const formatExpiryDate = (text) => {
    const cleaned = text.replace(/\D/g, '');
    if (cleaned.length >= 2) {
      return cleaned.substring(0, 2) + '/' + cleaned.substring(2, 4);
    }
    return cleaned;
  };

  const handlePayment = async () => {
    if (!cardNumber || !cardName || !expiryDate || !cvv) {
      showAlert('Incomplete Information', 'Please fill in all card details');
      return;
    }

    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    
    buttonScale.value = withSequence(
      withTiming(0.95, { duration: 100 }),
      withTiming(1, { duration: 100 })
    );

    setIsProcessing(true);

    // Simulate payment processing
    await new Promise((resolve) => setTimeout(resolve, 2000));

    setIsProcessing(false);
    setPaymentSuccess(true);

    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }

    setTimeout(() => {
      navigation.navigate('LibraryTab');
    }, 2000);
  };

  const buttonAnimStyle = useAnimatedStyle(() => ({
    transform: [{ scale: buttonScale.value }],
  }));

  if (paymentSuccess) {
    return (
      <View style={styles.container}>
        <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
          <View style={{ width: 22 }} />
          <Text style={styles.headerTitle}>Payment</Text>
          <View style={{ width: 22 }} />
        </View>

        <View style={styles.successFullContainer}>
          <SuccessAnimation />
          <Text style={styles.successTitle}>Payment Successful!</Text>
          <Text style={styles.successText}>
            Your {plan?.name} plan is now active
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Pressable
          onPress={() => {
            if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            navigation.goBack();
          }}
          hitSlop={12}
        >
          <Feather name="arrow-left" size={22} color={Colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Payment</Text>
        <View style={{ width: 22 }} />
      </View>

      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,
          { paddingBottom: insets.bottom + 40 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View entering={FadeInDown.duration(500)} style={styles.planSummary}>
          <Text style={styles.planSummaryTitle}>Plan Summary</Text>
          <View style={styles.planSummaryRow}>
            <Text style={styles.planSummaryLabel}>{plan?.name} Plan</Text>
            <Text style={styles.planSummaryValue}>{plan?.price}{plan?.period}</Text>
          </View>
          <View style={styles.planSummaryRow}>
            <Text style={styles.planSummaryLabel}>Tokens</Text>
            <Text style={styles.planSummaryValue}>{plan?.tokens}/month</Text>
          </View>
          <View style={styles.planSummaryDivider} />
          <View style={styles.planSummaryRow}>
            <Text style={styles.planSummaryTotal}>Total</Text>
            <Text style={styles.planSummaryTotal}>{plan?.price}</Text>
          </View>
        </Animated.View>

        <Animated.View entering={FadeInDown.delay(200).duration(500)} style={styles.paymentCard}>
          <Text style={styles.cardTitle}>Payment Method</Text>

          <View style={styles.inputContainer}>
            <Feather name="credit-card" size={18} color={Colors.textSecondary} />
            <TextInput
              style={styles.input}
              placeholder="Card Number"
              placeholderTextColor={Colors.textMuted}
              value={cardNumber}
              onChangeText={(text) => setCardNumber(formatCardNumber(text))}
              keyboardType="numeric"
              maxLength={19}
            />
          </View>

          <View style={styles.inputContainer}>
            <Feather name="user" size={18} color={Colors.textSecondary} />
            <TextInput
              style={styles.input}
              placeholder="Cardholder Name"
              placeholderTextColor={Colors.textMuted}
              value={cardName}
              onChangeText={setCardName}
              autoCapitalize="words"
            />
          </View>

          <View style={styles.inputRow}>
            <View style={[styles.inputContainer, styles.inputHalf]}>
              <Feather name="calendar" size={18} color={Colors.textSecondary} />
              <TextInput
                style={styles.input}
                placeholder="MM/YY"
                placeholderTextColor={Colors.textMuted}
                value={expiryDate}
                onChangeText={(text) => setExpiryDate(formatExpiryDate(text))}
                keyboardType="numeric"
                maxLength={5}
              />
            </View>

            <View style={[styles.inputContainer, styles.inputHalf]}>
              <Feather name="lock" size={18} color={Colors.textSecondary} />
              <TextInput
                style={styles.input}
                placeholder="CVV"
                placeholderTextColor={Colors.textMuted}
                value={cvv}
                onChangeText={setCvv}
                keyboardType="numeric"
                maxLength={3}
                secureTextEntry
              />
            </View>
          </View>

          <View style={styles.securityNote}>
            <Feather name="shield" size={16} color={Colors.success} />
            <Text style={styles.securityText}>
              Your payment is secure and encrypted
            </Text>
          </View>
        </Animated.View>

        <Animated.View
          entering={FadeInDown.delay(400).duration(500)}
          style={[styles.payButton, buttonAnimStyle]}
        >
          <Pressable onPress={handlePayment} disabled={isProcessing}>
            <LinearGradient
              colors={[Colors.accent, Colors.accentDark]}
              style={styles.payButtonGradient}
            >
              {isProcessing ? (
                <View style={styles.processingContainer}>
                  <Text style={styles.payButtonText}>Processing...</Text>
                </View>
              ) : (
                <>
                  <Text style={styles.payButtonText}>Complete Payment</Text>
                  <Feather name="arrow-right" size={18} color={Colors.primaryDark} />
                </>
              )}
            </LinearGradient>
          </Pressable>
        </Animated.View>

        <Text style={styles.disclaimer}>
          By continuing, you agree to our Terms of Service and Privacy Policy.
          You can cancel your subscription at any time.
        </Text>
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
    fontFamily: 'Inter_600SemiBold',
    fontSize: 18,
    color: Colors.white,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 24,
  },
  planSummary: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    marginBottom: 20,
  },
  planSummaryTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.white,
    marginBottom: 16,
  },
  planSummaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  planSummaryLabel: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
  },
  planSummaryValue: {
    fontFamily: 'Inter_500Medium',
    fontSize: 14,
    color: Colors.white,
  },
  planSummaryDivider: {
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginVertical: 12,
  },
  planSummaryTotal: {
    fontFamily: 'Inter_700Bold',
    fontSize: 16,
    color: Colors.white,
  },
  paymentCard: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    marginBottom: 20,
  },
  cardTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.white,
    marginBottom: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.inputBg,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.inputBorder,
    paddingHorizontal: 14,
    height: 52,
    marginBottom: 12,
  },
  input: {
    flex: 1,
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    color: Colors.white,
    marginLeft: 10,
  },
  inputRow: {
    flexDirection: 'row',
    gap: 12,
  },
  inputHalf: {
    flex: 1,
  },
  securityNote: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: 'rgba(78, 205, 196, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    marginTop: 8,
  },
  securityText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: Colors.success,
    flex: 1,
  },
  payButton: {
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 16,
  },
  payButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 16,
  },
  payButtonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.primaryDark,
  },
  processingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  disclaimer: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: Colors.textMuted,
    textAlign: 'center',
    lineHeight: 18,
  },
  successFullContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 40,
  },
  successContainer: {
    marginBottom: 24,
  },
  successCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    alignItems: 'center',
    justifyContent: 'center',
  },
  successTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 24,
    color: Colors.white,
    marginBottom: 8,
  },
  successText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
});

export default PaymentScreen;
