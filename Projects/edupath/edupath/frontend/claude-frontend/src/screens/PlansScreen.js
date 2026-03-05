import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { animations } from '../utils/animations';
import theme from '../config/theme';
import { toast } from 'react-toastify';
import { RefreshCw, Sparkles } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const PlansScreen = () => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const { tokenBalance, loadTokenBalance } = useAuth();
  const balanceCardRef = useRef(null);

  useEffect(() => {
    loadPackages();
  }, []);

  useEffect(() => {
    if (balanceCardRef.current) {
      animations.scaleIn(balanceCardRef.current, { scale: 0.8, duration: 0.8 });
    }
  }, []);

  const loadPackages = async () => {
    try {
      const response = await apiService.tokens.getPackages();
      setPackages(response.data.token_packages || []);
    } catch (error) {
      toast.error('Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (packageId) => {
    try {
      const response = await apiService.tokens.createOrder(packageId);
      toast.info('Payment processing...');
      // In production, integrate with payment gateway
      setTimeout(async () => {
        await loadTokenBalance();
        toast.success('Tokens added successfully!');
      }, 2000);
    } catch (error) {
      toast.error('Purchase failed');
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div style={styles.container}>
      <div ref={balanceCardRef} style={styles.balanceCard}>
        <div style={styles.balanceIcon}>💰</div>
        <div style={styles.balanceAmount}>{tokenBalance} Tokens</div>
        <button style={styles.refreshButton} onClick={loadTokenBalance}>
          <RefreshCw size={16} />
          <span>Refresh</span>
        </button>
      </div>

      <h1 style={styles.title}>Choose Your Plan</h1>
      <p style={styles.subtitle}>Get more tokens to continue learning</p>

      <div style={styles.plansGrid}>
        {packages.map((pkg, index) => (
          <PlanCard
            key={pkg.id}
            plan={pkg}
            index={index}
            onPurchase={handlePurchase}
          />
        ))}
      </div>
    </div>
  );
};

const PlanCard = ({ plan, index, onPurchase }) => {
  const cardRef = useRef(null);
  const isFeatured = plan.bonus_percentage > 0;

  useEffect(() => {
    if (cardRef.current) {
      animations.slideInUp(cardRef.current, { delay: index * 0.15 });
    }
  }, [index]);

  useEffect(() => {
    if (isFeatured && cardRef.current) {
      animations.glowPulse(cardRef.current);
    }
  }, [isFeatured]);

  return (
    <div
      ref={cardRef}
      style={{
        ...styles.planCard,
        ...(isFeatured ? styles.featuredCard : {}),
      }}
    >
      {isFeatured && (
        <div style={styles.badge}>
          <Sparkles size={14} />
          <span>Best Value</span>
        </div>
      )}
      <div style={styles.planName}>{plan.name}</div>
      <div style={styles.tokenCount}>{plan.tokens} Tokens</div>
      <div style={styles.price}>₹{plan.price_inr}</div>
      {plan.bonus_percentage > 0 && (
        <div style={styles.bonus}>+{plan.bonus_percentage}% Bonus</div>
      )}
      <button
        style={styles.purchaseButton}
        onClick={() => onPurchase(plan.id)}
      >
        Purchase
      </button>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1000px',
    margin: '0 auto',
    padding: theme.spacing.xl,
  },
  balanceCard: {
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.xl,
    textAlign: 'center',
    boxShadow: theme.shadows.lg,
    marginBottom: theme.spacing.xxl,
  },
  balanceIcon: {
    fontSize: '48px',
    marginBottom: theme.spacing.md,
  },
  balanceAmount: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.md,
    fontFamily: theme.typography.fontFamily.display,
  },
  refreshButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    padding: `${theme.spacing.xs} ${theme.spacing.md}`,
    backgroundColor: theme.colors.background,
    border: 'none',
    borderRadius: theme.borderRadius.full,
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
  },
  title: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
    fontFamily: theme.typography.fontFamily.display,
  },
  subtitle: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.neutral,
    marginBottom: theme.spacing.xxl,
    textAlign: 'center',
  },
  plansGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: theme.spacing.lg,
  },
  planCard: {
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.xl,
    textAlign: 'center',
    border: '2px solid #e5e7eb',
    position: 'relative',
  },
  featuredCard: {
    borderColor: theme.colors.primary,
  },
  badge: {
    position: 'absolute',
    top: -12,
    left: '50%',
    transform: 'translateX(-50%)',
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    padding: `4px ${theme.spacing.md}`,
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.full,
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
  },
  planName: {
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.md,
  },
  tokenCount: {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.secondary,
    marginBottom: theme.spacing.sm,
  },
  price: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.sm,
  },
  bonus: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.success,
    fontWeight: theme.typography.fontWeight.semibold,
    marginBottom: theme.spacing.lg,
  },
  purchaseButton: {
    width: '100%',
    padding: `${theme.spacing.md} 0`,
    backgroundColor: theme.colors.primary,
    color: theme.colors.dark,
    border: 'none',
    borderRadius: theme.borderRadius.md,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    cursor: 'pointer',
  },
};

export default PlansScreen;
