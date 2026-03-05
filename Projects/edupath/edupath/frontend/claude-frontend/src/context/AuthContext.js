import React, { createContext, useState, useContext, useEffect } from 'react';
import { apiService } from '../services/api';
import { toast } from 'react-toastify';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tokenBalance, setTokenBalance] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load user data from localStorage on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('@edupath_auth_token');
      const userData = localStorage.getItem('@edupath_user_data');
      
      if (token && userData) {
        try {
          setUser(JSON.parse(userData));
          setIsAuthenticated(true);
          await loadTokenBalance();
        } catch (error) {
          console.error('Error initializing auth:', error);
          logout();
        }
      }
      setLoading(false);
    };
    
    initializeAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const response = await apiService.auth.login(credentials);
      const { access_token, user_id, username } = response.data;
      
      const userData = { id: user_id, username, email: credentials.email };
      
      localStorage.setItem('@edupath_auth_token', access_token);
      localStorage.setItem('@edupath_user_data', JSON.stringify(userData));
      
      setUser(userData);
      setIsAuthenticated(true);
      
      await loadTokenBalance();
      
      toast.success(`Welcome back, ${username}!`);
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.response?.data?.message || 'Login failed' };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await apiService.auth.signup(userData);
      const { access_token, user_id, username } = response.data;
      
      const user = { id: user_id, username, email: userData.email };
      
      localStorage.setItem('@edupath_auth_token', access_token);
      localStorage.setItem('@edupath_user_data', JSON.stringify(user));
      
      setUser(user);
      setIsAuthenticated(true);
      
      await loadTokenBalance();
      
      toast.success(`Account created successfully! Welcome, ${username}!`);
      return { success: true };
    } catch (error) {
      console.error('Signup error:', error);
      return { success: false, error: error.response?.data?.message || 'Signup failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('@edupath_auth_token');
    localStorage.removeItem('@edupath_user_data');
    setUser(null);
    setIsAuthenticated(false);
    setTokenBalance(0);
    toast.info('Logged out successfully');
  };

  const loadTokenBalance = async () => {
    try {
      const response = await apiService.tokens.getBalance();
      setTokenBalance(response.data.balance || 0);
    } catch (error) {
      console.error('Error loading token balance:', error);
    }
  };

  const updateTokenBalance = (newBalance) => {
    setTokenBalance(newBalance);
  };

  const value = {
    user,
    tokenBalance,
    isAuthenticated,
    loading,
    login,
    signup,
    logout,
    loadTokenBalance,
    updateTokenBalance,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
