import axios from 'axios';
import { toast } from 'react-toastify';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('@edupath_auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error;
    
    if (response) {
      switch (response.status) {
        case 401:
          localStorage.removeItem('@edupath_auth_token');
          localStorage.removeItem('@edupath_user_data');
          window.location.href = '/login';
          toast.error('Session expired. Please login again.');
          break;
        case 402:
          toast.error('Insufficient tokens. Please purchase more.');
          break;
        case 404:
          toast.error('Resource not found.');
          break;
        case 500:
          toast.error('Something went wrong. Please try again.');
          break;
        default:
          toast.error(response.data?.message || 'An error occurred.');
      }
    } else if (error.request) {
      toast.error('Unable to connect. Please check your internet.');
    }
    
    return Promise.reject(error);
  }
);

// API Service Methods
export const apiService = {
  // Authentication
  auth: {
    signup: (data) => api.post('/api/auth/signup', data),
    login: (data) => api.post('/api/auth/login', data),
    sendOTP: (email) => api.post('/api/auth/send-otp', { email }),
    verifyOTP: (email, otp) => api.post('/api/auth/verify-otp', { email, otp }),
  },
  
  // Mentors
  mentors: {
    list: () => api.get('/api/mentors/list'),
    create: (formData) => api.post('/api/mentors/create-mentor', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  },
  
  // Chat
  chat: {
    send: (data) => api.post('/api/chat/chat', data),
    getHistory: (mentorId) => api.get(`/api/chat/history/${mentorId}`),
  },
  
  // Tokens
  tokens: {
    getBalance: () => api.get('/api/tokens/balance'),
    getPackages: () => api.get('/api/tokens/packages'),
    createOrder: (packageId) => api.post('/api/tokens/create-order', { package_id: packageId }),
  },
};

export default api;
