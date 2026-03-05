import React, { useEffect, useState } from 'react';
import { Text } from 'react-native'; // ✅ ADDED: Import Text component
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import Colors from "../constants/colors";
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../context/AuthContext';
import { STORAGE_KEYS } from '../config/constants';
import PageTurnTransition from '../components/PageTurnTransition';

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

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Main Tab Navigator (for authenticated users)
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: theme.colors.goldLeaf, // ✅ Gold for active
        tabBarInactiveTintColor: theme.colors.inkFaded,
        tabBarStyle: {
          backgroundColor: theme.colors.backgroundSecondary,
          borderTopWidth: 2,
          borderTopColor: theme.colors.border,
          paddingBottom: 8,
          paddingTop: 8,
          height: 65,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
          marginTop: -5,
        },
      }}
    >
      {/* ✅ CHANGED: Library is now the first tab (main screen) */}
      <Tab.Screen
        name="LibraryTab"
        component={LibraryScreen}
        options={{
          tabBarLabel: 'Library',
          tabBarIcon: ({ color, focused }) => (
            <Text style={{ fontSize: 24 }}>
              {focused ? '📚' : '📖'}
            </Text>
          ),
        }}
      />
      
      {/* ✅ KEEP: Tokens tab */}
      <Tab.Screen
        name="PlansTab"
        component={PlansScreen}
        options={{
          tabBarLabel: 'Tokens',
          tabBarIcon: ({ color, focused }) => (
            <Text style={{ fontSize: 24 }}>
              {focused ? '💰' : '🪙'}
            </Text>
          ),
        }}
      />
      
      {/* ✅ CHANGED: Chronicle instead of Profile */}
      <Tab.Screen
        name="ProfileTab"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Chronicle',
          tabBarIcon: ({ color, focused }) => (
            <Text style={{ fontSize: 24 }}>
              {focused ? '📊' : '📈'}
            </Text>
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
    return null; // Or add a loading screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!user ? (
          // ✅ NOT LOGGED IN: Show auth screens
          <Stack.Screen name="Auth" component={AuthStack} />
        ) : (
          // ✅ LOGGED IN: Show main app (NO ONBOARDING)
          <>
            {/* Main app with Library as home */}
            <Stack.Screen name="MainTabs" component={MainTabs} />
            
            {/* Create Mentor Screen (modal) */}
            <Stack.Screen
              name="CreateMentor"
              component={CreateMentorScreen}
              options={{
                headerShown: true,
                title: 'Summon Mentor',
                headerStyle: { 
                  backgroundColor: theme.colors.backgroundSecondary,
                  borderBottomWidth: 2,
                  borderBottomColor: theme.colors.goldLeaf,
                },
                headerTintColor: theme.colors.ink,
                headerTitleStyle: {
                  fontWeight: 'bold',
                  fontSize: 20,
                },
              }}
            />
            
            {/* Individual Mentor Chat Screen */}
            <Stack.Screen
              name="MentorChat"
              component={ChatScreen}
              options={({ route }) => ({
                headerShown: true,
                title: route.params?.mentorName || 'Chat',
                headerStyle: { 
                  backgroundColor: theme.colors.backgroundSecondary,
                  borderBottomWidth: 2,
                  borderBottomColor: theme.colors.goldLeaf,
                },
                headerTintColor: theme.colors.ink,
              })}
            />
            
            {/* Payment screen */}
            <Stack.Screen
              name="Payment"
              component={PaymentScreen}
              options={{
                headerShown: true,
                title: 'Complete Payment',
                headerStyle: { backgroundColor: theme.colors.goldLeaf },
                headerTintColor: theme.colors.ink,
                headerTitleStyle: {
                  fontWeight: '600',
                },
              }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default AppNavigator;