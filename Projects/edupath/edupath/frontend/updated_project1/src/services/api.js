import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL, STORAGE_KEYS } from '../config/constants';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ✅ Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      console.log('⚠️ Unauthorized - clearing auth');
      AsyncStorage.removeItem('@edupath_auth_token');
    }
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
// Request interceptor - Add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      
      // ✅ ADD: Debug logging
      console.log('🔐 API Request:', config.url);
      console.log('🔑 Token:', token ? 'Present' : 'MISSING!');
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        console.warn('⚠️ No auth token found for request:', config.url);
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
/*// API Methods
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
  
  // Auth
  signup: async (userData) => {
    const response = await api.post('/api/auth/signup', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },
  
  // Chat
  sendMessage: async (message, mentorId, conversationHistory = []) => {  // ✅ ADD: conversationHistory
    const response = await api.post('/api/chat', { 
      message,
      mentor_id: mentorId,
      conversation_history: conversationHistory  // ✅ ADD: Send history
    });
    return response.data;
  },
  
  // Payments
  getPlans: async () => {
    const response = await api.get('/api/payments/plans');
    return response.data;
  },
  
  createTokenOrder: async (packageId) => {
    const response = await api.post('/api/payments/create-order/tokens', {
      package_id: packageId,
    });
    return response.data;
  },
  
  verifyPayment: async (paymentData) => {
    const response = await api.post('/api/payments/verify-payment', paymentData);
    return response.data;
  },
  
  getBalance: async () => {
    const response = await api.get('/api/payments/balance');
    return response.data;
  },
   // ✅ ADD: Mentor creation
  createMentor: async (formData) => {
    const response = await api.post('/api/mentors/create-mentor', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  // ✅ ADD: List mentors
  listMentors: async () => {
    const response = await api.get('/api/mentors/list');
    return response.data;
  },
  // ✅ ADD: OTP methods
  sendOTP: async (email) => {
    const response = await api.post('/api/auth/send-otp', { email });
    return response.data;
  },
  
  verifyOTP: async (email, otp) => {
    const response = await api.post('/api/auth/verify-otp', { email, otp });
    return response.data;
  },
  getChatHistory: async (mentorId) => {
    const response = await api.get(`/api/chat/history/${mentorId}`);
    return response.data;
  },
};
**/
export const apiService = {
  // Auth
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },

  signup: async (userData) => {
    const response = await api.post('/api/auth/signup', userData);
    return response.data;
  },

  sendOTP: async (email) => {
    const response = await api.post('/api/auth/send-otp', { email });
    return response.data;
  },

  verifyOTP: async (email, otp) => {
    const response = await api.post('/api/auth/verify-otp', { email, otp });
    return response.data;
  },

  // Mentors
  listMentors: async () => {
    const response = await api.get('/api/mentors/list');
    return response.data;
  },

  createMentor: async (formData) => {
    const response = await api.post('/api/mentors/create-mentor', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Chat
  sendMessage: async (message, mentorId, conversationHistory = []) => {
    const response = await api.post('/api/chat/chat', {
      message,
      mentor_id: mentorId,
      conversation_history: conversationHistory,
    });
    return response.data;
  },

  getChatHistory: async (mentorId) => {
    const response = await api.get(`/api/chat/history/${mentorId}`);
    return response.data;
  },

  // Tokens
  getTokenBalance: async () => {
    const response = await api.get('/api/tokens/balance');
    return response.data;
  },

  getPlans: async () => {
    const response = await api.get('/api/tokens/packages');
    return response.data;
  },

  createTokenOrder: async (packageId) => {
    const response = await api.post('/api/tokens/create-order', {
      package_id: packageId,
    });
    return response.data;
  },
};

export default api;