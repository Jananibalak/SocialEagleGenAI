import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../services/api';
import { STORAGE_KEYS } from '../config/constants';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokenBalance, setTokenBalance] = useState(0);
  const [freeMessagesLeft, setFreeMessagesLeft] = useState(10);

  // ✅ FIX: Load user on app start
  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      const userData = await AsyncStorage.getItem(STORAGE_KEYS.USER_DATA);
      
      if (token && userData) {
        setUser(JSON.parse(userData));
        // Load token balance if logged in
        await loadTokenBalance();
      }
    } catch (error) {
      console.error('Error loading user:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTokenBalance = async () => {
    try {
      const response = await apiService.getBalance();
      setTokenBalance(response.balance || 0);
    } catch (error) {
      console.error('Error loading balance:', error);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await apiService.login(credentials);
      
      // ✅ CRITICAL: Save token first
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.access_token);
      
      // Then save user data
      const userData = {
        id: response.user_id,
        username: response.username,
        email: credentials.email,
      };
      await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
      
      setUser(userData);
      await loadTokenBalance();
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

const signup = async (credentials) => {
    try {
      console.log('📝 Attempting signup:', { ...credentials, password: '***' });
      
      const response = await apiService.signup(credentials);
      
      if (response.access_token) {
        // Save token
        await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.access_token);
        
        // Save user data
        const userData = {
          id: response.user_id,
          username: response.username,
          email: credentials.email,
        };
        await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
        
        setUser(userData);
        
        // Load token balance
        try {
          await loadTokenBalance();
        } catch (error) {
          console.error('Error loading initial balance:', error);
          setTokenBalance(50); // Default
        }
        
        console.log('✅ Signup successful');
        return { success: true };
      } else {
        return { 
          success: false, 
          error: response.error || 'Signup failed' 
        };
      }
    } catch (error) {
      console.error('❌ Signup error:', error);
      console.error('Error response:', error.response?.data);
      
      return { 
        success: false, 
        error: error.response?.data?.error || 'Signup failed. Please try again.' 
      };
    }
  };

const logout = async () => {
    try {
      // Clear all auth data
      await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      await AsyncStorage.removeItem(STORAGE_KEYS.USER_DATA);
      await AsyncStorage.removeItem(STORAGE_KEYS.MESSAGE_HISTORY);
      
      // ✅ ADD: Clear any other stored data
      await AsyncStorage.removeItem('@edupath_user_preferences');
      
      // Reset state
      setUser(null);
      setTokenBalance(0);
      setFreeMessagesLeft(10);
      
      console.log('✅ Logged out successfully');
      
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const useFreeMessage = () => {
    if (freeMessagesLeft > 0) {
      setFreeMessagesLeft(prev => prev - 1);
    }
  };

  const value = {
    user,
    loading,
    tokenBalance,
    freeMessagesLeft,
    login,
    signup,
    logout,
    loadTokenBalance,
    useFreeMessage,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};