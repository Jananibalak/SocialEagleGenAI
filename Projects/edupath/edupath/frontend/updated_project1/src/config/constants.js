import Constants from 'expo-constants';

// API Configuration
export const API_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:5000';

export const API_ENDPOINTS = {
  // Auth
  SIGNUP: '/api/auth/signup',
  LOGIN: '/api/auth/login',
  
  // Chat
  CHAT: '/api/chat',
  
  // Payments
  PLANS: '/api/payments/plans',
  CREATE_ORDER_TOKENS: '/api/payments/create-order/tokens',
  VERIFY_PAYMENT: '/api/payments/verify-payment',
  BALANCE: '/api/payments/balance',
  
  // Health
  HEALTH: '/health',
};

// Free trial configuration
export const FREE_TRIAL_MESSAGES = 10;

// Token costs
export const TOKEN_COSTS = {
  CHAT_MESSAGE: 1.0,
  DAILY_CHECKIN: 0.5,
  SESSION_ANALYSIS: 2.0,
  PROGRESS_REPORT: 5.0,
  LEARNING_PATH: 3.0,
};

// Razorpay configuration
export const RAZORPAY_CONFIG = {
  KEY_ID: 'rzp_test_SDwzqakYKFpnZt', // Replace with your test key
  THEME_COLOR: '#FFC107',
};

// Chat configuration
export const CHAT_CONFIG = {
  MAX_MESSAGE_LENGTH: 1000,
  TYPING_INDICATOR_DELAY: 1000,
  AUTO_SCROLL_THRESHOLD: 100,
};

// Storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: '@edupath_auth_token',
  USER_DATA: '@edupath_user_data',
  ONBOARDING_COMPLETED: '@edupath_onboarding_completed',
  MESSAGE_HISTORY: '@edupath_message_history',
};

// Onboarding flow
export const ONBOARDING_QUESTIONS = [
  {
    id: 'welcome',
    message: "Hey there! 👋 I'm your EduPath AI coach. I'm here to help you learn anything you want, stay motivated, and track your progress. What should I call you?",
    type: 'text',
  },
  {
    id: 'goals',
    message: "Nice to meet you, {name}! 🎯 What are you looking to learn or improve? (e.g., coding, data science, public speaking)",
    type: 'text',
  },
  {
    id: 'experience',
    message: "Got it! What's your current level? 📊",
    type: 'options',
    options: ['Complete Beginner', 'Some Experience', 'Intermediate', 'Advanced'],
  },
  {
    id: 'time',
    message: "How much time can you dedicate daily? ⏰",
    type: 'options',
    options: ['15-30 mins', '30-60 mins', '1-2 hours', '2+ hours'],
  },
  {
    id: 'motivation',
    message: "What motivates you most? 🚀",
    type: 'options',
    options: ['Career growth', 'Personal interest', 'Exam/Certification', 'Build projects'],
  },
  {
    id: 'complete',
    message: "Perfect! 🎉 I've created your personalized learning path. Let's get started! You have {freeMessages} free messages to try me out. Ready to begin your learning journey?",
    type: 'complete',
  },
];

export default {
  API_URL,
  API_ENDPOINTS,
  FREE_TRIAL_MESSAGES,
  TOKEN_COSTS,
  RAZORPAY_CONFIG,
  CHAT_CONFIG,
  STORAGE_KEYS,
  ONBOARDING_QUESTIONS,
};