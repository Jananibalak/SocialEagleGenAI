import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS } from '../config/constants';

export const clearOnboardingData = async () => {
  try {
    await AsyncStorage.removeItem(STORAGE_KEYS.ONBOARDING_COMPLETED);
    await AsyncStorage.removeItem('@edupath_user_preferences');
    console.log('✅ Cleared onboarding data');
  } catch (error) {
    console.error('Error clearing storage:', error);
  }
};

// ✅ Call this once to clean up
export const clearAllData = async () => {
  try {
    await AsyncStorage.clear();
    console.log('✅ Cleared all storage');
  } catch (error) {
    console.error('Error clearing storage:', error);
  }
};