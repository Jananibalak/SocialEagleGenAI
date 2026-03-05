import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { showAlert } from '../utils/alert';
import Colors from '../constants/colors';

// ✅ Token packages - Simple and clear
const TOKEN_PACKAGES = [
  {
    id: 'starter_pack',
    tokens: 50,
    price: 175,
    color: ['#60a5fa', '#3b82f6'],
    popular: false,
  },
  {
    id: 'power_pack',
    tokens: 100,
    price: 300,
    color: [Colors.accent, Colors.accentDark],
    popular: true,
  },
  {
    id: 'mega_pack',
    tokens: 200,
    price: 500,
    color: ['#a78bfa', '#8b5cf6'],
    popular: false,
  },
];

const TokenPackageCard = ({ package: pkg, onPress, purchasing }) => {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.packageCard,
        pressed && styles.packageCardPressed,
      ]}
      onPress={() => onPress(pkg)}
      disabled={purchasing}
    >
      <LinearGradient colors={pkg.color} style={styles.packageGradient}>
        {pkg.popular && (
          <View style={styles.popularBadge}>
            <Text style={styles.popularText}>POPULAR</Text>
          </View>
        )}
        
        <View style={styles.packageHeader}>
          <Feather name="zap" size={32} color="rgba(255,255,255,0.9)" />
          <Text style={styles.packageTokens}>{pkg.tokens}</Text>
          <Text style={styles.packageTokensLabel}>Tokens</Text>
        </View>

        <View style={styles.packagePricing}>
          <Text style={styles.packagePrice}>₹{pkg.price}</Text>
          <Text style={styles.packagePricePerToken}>
            ₹{(pkg.price / pkg.tokens).toFixed(2)}/token
          </Text>
        </View>

        <View style={styles.packageButton}>
          {purchasing ? (
            <ActivityIndicator size="small" color={Colors.primaryDark} />
          ) : (
            <>
              <Text style={styles.packageButtonText}>Buy Now</Text>
              <Feather name="arrow-right" size={16} color={Colors.primaryDark} />
            </>
          )}
        </View>
      </LinearGradient>
    </Pressable>
  );
};

const PlansScreen = () => {
  const insets = useSafeAreaInsets();
  const { tokenBalance, loadTokenBalance } = useAuth();
  const [purchasing, setPurchasing] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState(null);

  const handlePurchase = async (pkg) => {
    if (purchasing) return;

    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }

    setSelectedPackage(pkg.id);
    setPurchasing(true);

    try {
      console.log('📦 Creating order for:', pkg);
      
      // Create Razorpay order
      const orderResponse = await apiService.createTokenOrder(pkg.id);
      
      if (!orderResponse.success) {
        throw new Error(orderResponse.error || 'Failed to create order');
      }

      console.log('✅ Order created:', orderResponse.order_id);

      // ✅ Initialize Razorpay payment
      const options = {
        key: orderResponse.razorpay_key,
        amount: orderResponse.amount,
        currency: 'INR',
        name: 'EduPath',
        description: `${pkg.tokens} Tokens`,
        order_id: orderResponse.order_id,
        handler: async function (response) {
          console.log('💳 Payment successful:', response);
          
          try {
            // Verify payment with backend
            const verifyResponse = await apiService.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });

            if (verifyResponse.success) {
              if (Platform.OS !== 'web') {
                Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
              }
              
              showAlert(
                'Success! 🎉',
                `${pkg.tokens} tokens added to your account!`
              );
              
              // Reload balance
              await loadTokenBalance();
            } else {
              throw new Error('Payment verification failed');
            }
          } catch (verifyError) {
            console.error('❌ Verification error:', verifyError);
            showAlert('Error', 'Payment verification failed. Contact support.');
          } finally {
            setPurchasing(false);
            setSelectedPackage(null);
          }
        },
        prefill: {
          name: '',
          email: '',
          contact: '',
        },
        theme: {
          color: Colors.accent,
        },
        modal: {
          ondismiss: function() {
            console.log('❌ Payment cancelled');
            setPurchasing(false);
            setSelectedPackage(null);
          }
        }
      };

      // Open Razorpay checkout
      if (typeof window !== 'undefined' && window.Razorpay) {
        const rzp = new window.Razorpay(options);
        rzp.open();
      } else {
        throw new Error('Razorpay SDK not loaded');
      }

    } catch (error) {
      console.error('❌ Purchase error:', error);
      
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
      
      showAlert(
        'Purchase Failed',
        error.response?.data?.error || error.message || 'Something went wrong. Please try again.'
      );
      
      setPurchasing(false);
      setSelectedPackage(null);
    }
  };

  return (
    <View style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.headerTitle}>Buy Tokens</Text>
        <Feather name="shopping-bag" size={22} color={Colors.white} />
      </View>

      <ScrollView
        contentContainerStyle={[styles.scrollContent, { paddingBottom: insets.bottom + 100 }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Current Balance */}
        <Animated.View entering={FadeInDown.duration(500)} style={styles.balanceCard}>
          <LinearGradient
            colors={['rgba(245, 203, 125, 0.15)', 'rgba(245, 203, 125, 0.1)']}
            style={styles.balanceGradient}
          >
            <View style={styles.balanceContent}>
              <Feather name="zap" size={24} color={Colors.accent} />
              <View style={styles.balanceText}>
                <Text style={styles.balanceLabel}>Current Balance</Text>
                <Text style={styles.balanceValue}>{tokenBalance || 0} Tokens</Text>
              </View>
            </View>
          </LinearGradient>
        </Animated.View>

        {/* Info Box */}
        <Animated.View entering={FadeInDown.delay(100).duration(500)} style={styles.infoBox}>
          <Feather name="info" size={16} color={Colors.accent} />
          <Text style={styles.infoText}>
            Tokens are used for AI conversations with your mentors. More tokens = more learning!
          </Text>
        </Animated.View>

        {/* Token Packages */}
        <Text style={styles.sectionTitle}>Choose Your Plan</Text>
        
        {TOKEN_PACKAGES.map((pkg, index) => (
          <Animated.View
            key={pkg.id}
            entering={FadeInDown.delay((index + 2) * 100).duration(500)}
          >
            <TokenPackageCard
              package={pkg}
              onPress={handlePurchase}
              purchasing={purchasing && selectedPackage === pkg.id}
            />
          </Animated.View>
        ))}

        {/* Payment Info */}
        <Animated.View entering={FadeInDown.delay(500).duration(500)} style={styles.paymentInfo}>
          <Text style={styles.paymentInfoTitle}>💳 Secure Payment</Text>
          <Text style={styles.paymentInfoText}>
            • Powered by Razorpay{'\n'}
            • UPI, Cards, NetBanking accepted{'\n'}
            • Instant token delivery{'\n'}
            • 100% secure transactions
          </Text>
        </Animated.View>
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
    padding: 20,
  },
  balanceCard: {
    borderRadius: 16,
    marginBottom: 16,
    overflow: 'hidden',
  },
  balanceGradient: {
    padding: 20,
  },
  balanceContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  balanceText: {
    flex: 1,
  },
  balanceLabel: {
    fontFamily: 'Inter_500Medium',
    fontSize: 13,
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  balanceValue: {
    fontFamily: 'Inter_700Bold',
    fontSize: 24,
    color: Colors.white,
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    backgroundColor: 'rgba(245, 203, 125, 0.1)',
    padding: 14,
    borderRadius: 12,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: 'rgba(245, 203, 125, 0.2)',
  },
  infoText: {
    flex: 1,
    fontFamily: 'Inter_400Regular',
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
  sectionTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 18,
    color: Colors.white,
    marginBottom: 16,
  },
  packageCard: {
    borderRadius: 16,
    marginBottom: 16,
    overflow: 'hidden',
  },
  packageCardPressed: {
    opacity: 0.9,
    transform: [{ scale: 0.98 }],
  },
  packageGradient: {
    padding: 20,
    position: 'relative',
  },
  popularBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.25)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  popularText: {
    fontFamily: 'Inter_700Bold',
    fontSize: 10,
    color: Colors.white,
    letterSpacing: 0.5,
  },
  packageHeader: {
    alignItems: 'center',
    marginBottom: 16,
  },
  packageTokens: {
    fontFamily: 'Inter_800ExtraBold',
    fontSize: 48,
    color: Colors.white,
    marginTop: 8,
  },
  packageTokensLabel: {
    fontFamily: 'Inter_500Medium',
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  packagePricing: {
    alignItems: 'center',
    marginBottom: 20,
  },
  packagePrice: {
    fontFamily: 'Inter_700Bold',
    fontSize: 32,
    color: Colors.white,
  },
  packagePricePerToken: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
    marginTop: 4,
  },
  packageButton: {
    backgroundColor: Colors.white,
    borderRadius: 12,
    paddingVertical: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  packageButtonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.primaryDark,
  },
  paymentInfo: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  paymentInfoTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.white,
    marginBottom: 8,
  },
  paymentInfoText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: Colors.textSecondary,
    lineHeight: 18,
  },
});

export default PlansScreen;