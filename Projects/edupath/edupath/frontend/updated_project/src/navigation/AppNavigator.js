import React, { useEffect, useState } from 'react';
import { Text, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import Colors from "../constants/colors";
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../context/AuthContext';
import { STORAGE_KEYS } from '../config/constants';
import PageTurnTransition from '../components/PageTurnTransition';
import { Feather } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';

// Screens
import LoginScreen from '../screens/LoginScreen';
import SignupScreen from '../screens/SignupScreen';
import ChatScreen from '../screens/ChatScreen';
import PlansScreen from '../screens/PlansScreen';
import PaymentScreen from '../screens/PaymentScreen';
import ProfileScreen from '../screens/ProfileScreen';
import CreateMentorScreen from '../screens/CreateMentorScreen'; 
import LibraryScreen from '../screens/LibraryScreen'; 
import theme from '../config/theme';
import AnalyticsScreen from '../screens/AnalyticsScreen';
const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Main Tab Navigator (for authenticated users)
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: Colors.accent,
        tabBarInactiveTintColor: 'rgba(255,255,255,0.4)',
        tabBarStyle: {
          position: 'absolute',
          backgroundColor: Platform.OS === 'ios' ? 'rgba(14, 50, 72, 0.9)' : Colors.primary,
          borderTopWidth: 1,
          borderTopColor: 'rgba(255,255,255,0.06)',
          paddingBottom: Platform.OS === 'ios' ? 20 : 8,
          paddingTop: 8,
          height: Platform.OS === 'ios' ? 85 : 65,
          elevation: 0,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontFamily: 'Inter_600SemiBold',
          marginTop: -4,
        },
        tabBarBackground: () => (
          Platform.OS === 'ios' ? (
            <BlurView
              intensity={80}
              tint="dark"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
              }}
            />
          ) : null
        ),
      }}
    >
      <Tab.Screen
        name="LibraryTab"
        component={LibraryScreen}
        options={{
          tabBarLabel: 'Library',
          tabBarIcon: ({ color, focused }) => (
            <Feather 
              name="book-open" 
              size={focused ? 24 : 22} 
              color={color}
            />
          ),
        }}
      />
      {/* ✅ ADD THIS */}
      <Tab.Screen
        name="AnalyticsTab"
        component={AnalyticsScreen}
        options={{
          tabBarLabel: 'Analytics',
          tabBarIcon: ({ color, focused }) => (
            <Feather 
              name="flag" 
              size={focused ? 24 : 22} 
              color={color}
            />
          ),
        }}
      />
      <Tab.Screen
        name="PlansTab"
        component={PlansScreen}
        options={{
          tabBarLabel: 'Plans',
          tabBarIcon: ({ color, focused }) => (
            <Feather 
              name="zap" 
              size={focused ? 24 : 22} 
              color={color}
            />
          ),
        }}
      />
      
      <Tab.Screen
        name="ProfileTab"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
          tabBarIcon: ({ color, focused }) => (
            <Feather 
              name="user" 
              size={focused ? 24 : 22} 
              color={color}
            />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

// Auth Navigator
function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: Colors.primary },
        animation: "slide_from_right",
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Signup" component={SignupScreen} />
    </Stack.Navigator>
  );
}

// Main Navigator
function AppNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return null;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator 
        screenOptions={{ 
          headerShown: false,
          contentStyle: { backgroundColor: Colors.primary },
        }}
      >
        {!user ? (
          <Stack.Screen name="Auth" component={AuthStack} />
        ) : (
          <>
            <Stack.Screen name="MainTabs" component={MainTabs} />
            
            <Stack.Screen
              name="CreateMentor"
              component={CreateMentorScreen}
              options={{
                headerShown: false,
                presentation: 'modal',
              }}
            />
            
            <Stack.Screen
              name="MentorChat"
              component={ChatScreen}
              options={{
                headerShown: false,
                animation: 'slide_from_right',
              }}
            />
            
            <Stack.Screen
              name="Payment"
              component={PaymentScreen}
              options={{
                headerShown: false,
                animation: 'slide_from_right',
              }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default AppNavigator;