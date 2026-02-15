import { Alert, Platform } from 'react-native';

export const showAlert = (title, message, buttons) => {
  if (Platform.OS === 'web') {
    if (!buttons || buttons.length === 0) {
      window.alert(`${title}\n\n${message || ''}`);
      return;
    }
    
    if (buttons.length === 1) {
      window.alert(`${title}\n\n${message || ''}`);
      if (buttons[0].onPress) buttons[0].onPress();
      return;
    }
    
    const confirmed = window.confirm(`${title}\n\n${message || ''}`);
    
    if (confirmed) {
      const confirmButton = buttons.find(btn => 
        btn.style === 'destructive' || btn.text !== 'Cancel'
      ) || buttons[buttons.length - 1];
      if (confirmButton.onPress) confirmButton.onPress();
    } else {
      const cancelButton = buttons.find(btn => 
        btn.style === 'cancel' || btn.text === 'Cancel'
      );
      if (cancelButton && cancelButton.onPress) cancelButton.onPress();
    }
  } else {
    Alert.alert(title, message, buttons);
  }
};

export default showAlert;