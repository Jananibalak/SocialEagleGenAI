import React, { useState, useEffect, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';

import { Text } from 'react-native'; // ✅ ADDED: Import Text component
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';
import { useFonts } from 'expo-font';
import { Cinzel_400Regular, Cinzel_700Bold } from '@expo-google-fonts/cinzel';
import { CrimsonText_400Regular, CrimsonText_600SemiBold } from '@expo-google-fonts/crimson-text';
import { DancingScript_400Regular } from '@expo-google-fonts/dancing-script';
// In App.js, add temporarily:
import { clearOnboardingData } from './src/utils/clearStorage';



export default function App() {
    let [fontsLoaded] = useFonts({
    Cinzel_400Regular,
    Cinzel_700Bold,
    CrimsonText_400Regular,
    CrimsonText_600SemiBold,
    DancingScript_400Regular,
  });

  useEffect(() => {
  clearOnboardingData(); // ✅ Clear old onboarding data
}, []);


  if (!fontsLoaded) {
    return <Text>Loading ancient texts...</Text>;
  }
  return (
    <AuthProvider>
      <StatusBar style="dark" />
      <AppNavigator />
    </AuthProvider>
  );
}