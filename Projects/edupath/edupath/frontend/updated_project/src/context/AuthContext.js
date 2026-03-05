// ✅ FIX #2: FRONTEND - Fix Logout Issue

// File: frontend/src/context/AuthContext.js

import React, { createContext, useState, useEffect, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../services/api';
import { STORAGE_KEYS, FREE_TRIAL_MESSAGES } from '../config/constants';

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
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokenBalance, setTokenBalance] = useState(0);
  const [freeMessagesLeft, setFreeMessagesLeft] = useState(FREE_TRIAL_MESSAGES);

  // Load user data on mount
  useEffect(() => {
    loadUserData();
  }, []);

  // Load token balance when user changes
  useEffect(() => {
    if (user) {
      loadTokenBalance();
    }
  }, [user]);

  const loadUserData = async () => {
    try {
      const storedToken = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      const storedUser = await AsyncStorage.getItem(STORAGE_KEYS.USER_DATA);

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTokenBalance = async () => {
    try {
      const response = await apiService.getTokenBalance();
      setTokenBalance(response.balance || 0);
    } catch (error) {
      console.error('Error loading token balance:', error);
    }
  };

  const signup = async (userData) => {
    try {
      const response = await apiService.signup(userData);
      
      if (response.access_token) {
        await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.access_token);
        
        const userInfo = {
          id: response.user_id,
          email: userData.email,
          username: userData.username,
          full_name: userData.full_name,
        };
        
        await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userInfo));
        
        setToken(response.access_token);
        setUser(userInfo);
        
        return { success: true };
      }
      
      return { success: false, error: 'No token received' };
    } catch (error) {
      console.error('Signup error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Signup failed',
      };
    }
  };

  const login = async (credentials) => {
    try {
      const response = await apiService.login(credentials);
      
      if (response.access_token) {
        await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.access_token);
        
        const userInfo = {
          id: response.user_id,
          email: credentials.email,
          username: response.username || credentials.email.split('@')[0],
        };
        
        await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userInfo));
        
        setToken(response.access_token);
        setUser(userInfo);
        
        return { success: true };
      }
      
      return { success: false, error: 'No token received' };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
      };
    }
  };

  // ✅ FIX: Improved logout with proper state reset
  const logout = async () => {
    try {
      console.log('🚪 Starting logout process...');
      
      // Clear all AsyncStorage keys
      const keysToRemove = [
        STORAGE_KEYS.AUTH_TOKEN,
        STORAGE_KEYS.USER_DATA,
        STORAGE_KEYS.MESSAGE_HISTORY,
        STORAGE_KEYS.ONBOARDING_COMPLETED,
        '@edupath_user_preferences',
      ];
      
      await AsyncStorage.multiRemove(keysToRemove);
      console.log('✅ AsyncStorage cleared');
      
      // Reset all state
      setToken(null);
      setUser(null);
      setTokenBalance(0);
      setFreeMessagesLeft(FREE_TRIAL_MESSAGES);
      
      console.log('✅ State reset complete');
      
      return { success: true };
    } catch (error) {
      console.error('❌ Logout error:', error);
      return { success: false, error: error.message };
    }
  };

  const updateTokenBalance = (newBalance) => {
    setTokenBalance(newBalance);
  };

  const useFreeMessage = () => {
    if (freeMessagesLeft > 0) {
      setFreeMessagesLeft(prev => prev - 1);
      return true;
    }
    return false;
  };

  const value = {
    user,
    token,
    loading,
    tokenBalance,
    freeMessagesLeft,
    signup,
    login,
    logout,
    loadTokenBalance,
    updateTokenBalance,
    useFreeMessage,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;