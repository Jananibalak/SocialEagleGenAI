import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { RAZORPAY_CONFIG } from '../config/constants';
import theme from '../config/theme';

const PaymentScreen = ({ route, navigation }) => {
  const { orderData, plan } = route.params;
  const { loadTokenBalance } = useAuth();
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    // For web, we need to load Razorpay script dynamically
    if (Platform.OS === 'web') {
      handleWebPayment();
    } else {
      // For mobile, we'll use a webview or redirect (simplified for now)
      Alert.alert(
        'Payment',
        'Razorpay mobile integration requires additional native modules. For testing, use the web version.',
        [
          { text: 'OK', onPress: () => navigation.goBack() }
        ]
      );
    }
  };

  const handleWebPayment = () => {
    setLoading(true);

    // Load Razorpay script
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => {
      openRazorpay();
    };
    script.onerror = () => {
      Alert.alert('Error', 'Failed to load payment gateway');
      setLoading(false);
    };
    document.body.appendChild(script);
  };

  const openRazorpay = () => {
    const options = {
      key: orderData.key_id || RAZORPAY_CONFIG.KEY_ID,
      amount: orderData.amount,
      currency: orderData.currency,
      name: 'EduPath',
      description: `Purchase ${plan.name}`,
      order_id: orderData.order_id,
      theme: {
        color: RAZORPAY_CONFIG.THEME_COLOR,
      },
      handler: async function (response) {
        await verifyPayment(response);
      },
      modal: {
        ondismiss: function () {
          setLoading(false);
          Alert.alert('Payment Cancelled', 'You cancelled the payment');
        },
      },
      prefill: {
        name: '',
        email: '',
        contact: '',
      },
      notes: {
        package: plan.name,
      },
    };

    const razorpay = new window.Razorpay(options);
    razorpay.open();
    setLoading(false);
  };

  const verifyPayment = async (response) => {
    setLoading(true);

    try {
      const verificationData = {
        razorpay_order_id: response.razorpay_order_id,
        razorpay_payment_id: response.razorpay_payment_id,
        razorpay_signature: response.razorpay_signature,
      };

      const result = await apiService.verifyPayment(verificationData);

      if (result.success) {
        // Reload token balance
        await loadTokenBalance();

        Alert.alert(
          'Payment Successful! 🎉',
          `${plan.actual_tokens} tokens have been added to your account`,
          [
            {
              text: 'Start Chatting',
              onPress: () => navigation.navigate('Chat'),
            },
          ]
        );
      } else {
        Alert.alert('Payment Verification Failed', 'Please contact support');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      Alert.alert('Error', 'Payment verification failed');
    } finally {
      setLoading(false);
    }
  };

  // Test mode handler
  const handleTestPayment = async () => {
    Alert.alert(
      'Test Payment',
      'This will simulate a successful payment in test mode',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Proceed',
          onPress: async () => {
            setLoading(true);
            
            // Simulate payment delay
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // In a real scenario, you'd need to trigger the payment webhook
            // For testing, you can manually credit tokens via backend
            Alert.alert(
              'Test Mode',
              'In production, Razorpay will process the payment. For testing, please use Razorpay test cards:\n\n4111 1111 1111 1111\nCVV: 123\nExpiry: Any future date',
              [
                {
                  text: 'OK',
                  onPress: () => navigation.goBack(),
                },
              ]
            );
            
            setLoading(false);
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.primaryDark]}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Complete Payment</Text>
      </LinearGradient>

      <View style={styles.content}>
        {/* Order Summary */}
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Order Summary</Text>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Plan</Text>
            <Text style={styles.summaryValue}>{plan.name}</Text>
          </View>

          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Tokens</Text>
            <Text style={styles.summaryValue}>{plan.actual_tokens}</Text>
          </View>

          {plan.bonus_tokens > 0 && (
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Bonus</Text>
              <Text style={[styles.summaryValue, styles.bonusText]}>
                +{plan.bonus_tokens} 🎁
              </Text>
            </View>
          )}

          <View style={[styles.summaryRow, styles.totalRow]}>
            <Text style={styles.totalLabel}>Total</Text>
            <Text style={styles.totalValue}>₹{plan.price}</Text>
          </View>
        </View>

        {/* Payment Info */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>🔒 Secure Payment</Text>
          <Text style={styles.infoText}>
            Payment is processed securely through Razorpay. We support UPI, Cards,
            Net Banking, and Wallets.
          </Text>
        </View>

        {/* Test Card Info */}
        <View style={styles.testCard}>
          <Text style={styles.testTitle}>💳 Test Cards</Text>
          <Text style={styles.testText}>
            Card: 4111 1111 1111 1111{'\n'}
            CVV: 123{'\n'}
            Expiry: Any future date{'\n'}
            UPI: success@razorpay
          </Text>
        </View>

        {/* Payment Button */}
        <TouchableOpacity
          style={styles.paymentButton}
          onPress={handlePayment}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={theme.colors.text} />
          ) : (
            <>
              <Text style={styles.paymentButtonText}>
                Pay ₹{plan.price}
              </Text>
              <Text style={styles.paymentButtonSubtext}>via Razorpay</Text>
            </>
          )}
        </TouchableOpacity>

        {/* Test Mode Button */}
        <TouchableOpacity
          style={styles.testButton}
          onPress={handleTestPayment}
          disabled={loading}
        >
          <Text style={styles.testButtonText}>Test Mode (Simulate Payment)</Text>
        </TouchableOpacity>

        {/* Cancel Button */}
        <TouchableOpacity
          style={styles.cancelButton}
          onPress={() => navigation.goBack()}
          disabled={loading}
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    paddingTop: 60,
    paddingBottom: theme.spacing.lg,
    paddingHorizontal: theme.spacing.lg,
  },
  headerTitle: {
    fontSize: theme.fonts.sizes.xl,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  content: {
    padding: theme.spacing.lg,
  },
  summaryCard: {
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    ...theme.shadows.md,
  },
  summaryTitle: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.sm,
  },
  summaryLabel: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.textSecondary,
  },
  summaryValue: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: '600',
    color: theme.colors.text,
  },
  bonusText: {
    color: theme.colors.success,
  },
  totalRow: {
    marginTop: theme.spacing.md,
    paddingTop: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.divider,
  },
  totalLabel: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  totalValue: {
    fontSize: theme.fonts.sizes.xl,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  infoCard: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  infoTitle: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  infoText: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.textSecondary,
    lineHeight: 18,
  },
  testCard: {
    backgroundColor: theme.colors.info + '20',
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.info,
  },
  testTitle: {
    fontSize: theme.fonts.sizes.sm,
    fontWeight: 'bold',
    color: theme.colors.info,
    marginBottom: theme.spacing.xs,
  },
  testText: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.text,
    lineHeight: 16,
  },
  paymentButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
    ...theme.shadows.md,
  },
  paymentButtonText: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  paymentButtonSubtext: {
    fontSize: theme.fonts.sizes.xs,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
  testButton: {
    backgroundColor: theme.colors.info,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  testButtonText: {
    fontSize: theme.fonts.sizes.sm,
    fontWeight: '600',
    color: theme.colors.background,
  },
  cancelButton: {
    padding: theme.spacing.md,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.textSecondary,
  },
});

export default PaymentScreen;