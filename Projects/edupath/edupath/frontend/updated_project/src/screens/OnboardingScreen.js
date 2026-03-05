import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../context/AuthContext';
import { STORAGE_KEYS, ONBOARDING_QUESTIONS, FREE_TRIAL_MESSAGES } from '../config/constants';
import ChatBubble from '../components/ChatBubble';
import theme from '../config/theme';

const OnboardingScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [inputText, setInputText] = useState('');
  const [showOptions, setShowOptions] = useState(false);
  const [userResponses, setUserResponses] = useState({});
  const flatListRef = useRef(null);

  useEffect(() => {
    askQuestion(0);
  }, []);

  const askQuestion = (index) => {
    const question = ONBOARDING_QUESTIONS[index];
    let messageText = question.message;

    // Replace placeholders - check both userResponses and just-set name
    const userName = userResponses.name || '';
    if (userName) {
      messageText = messageText.replace('{name}', userName);
    }
    messageText = messageText.replace('{freeMessages}', FREE_TRIAL_MESSAGES);

    const aiMessage = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'ai',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, aiMessage]);
    setShowOptions(question.type === 'options');
  };

  const handleTextResponse = () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentQuestion = ONBOARDING_QUESTIONS[currentQuestionIndex];
    
    // Special handling for name - save it immediately for next question
    let updatedResponses = { ...userResponses };
    if (currentQuestion.id === 'welcome') {
      updatedResponses.name = inputText.trim();
      setUserResponses(updatedResponses);
    } else {
      updatedResponses[currentQuestion.id] = inputText.trim();
      setUserResponses(updatedResponses);
    }

    setInputText('');
    moveToNextQuestion();
  };

  const handleOptionResponse = (option) => {
    const userMessage = {
      id: Date.now().toString(),
      text: option,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentQuestion = ONBOARDING_QUESTIONS[currentQuestionIndex];
    const updatedResponses = {
      ...userResponses,
      [currentQuestion.id]: option,
    };
    setUserResponses(updatedResponses);

    setShowOptions(false);
    moveToNextQuestion();
  };

  const moveToNextQuestion = () => {
    const nextIndex = currentQuestionIndex + 1;

    if (nextIndex < ONBOARDING_QUESTIONS.length) {
      setTimeout(() => {
        setCurrentQuestionIndex(nextIndex);
        askQuestion(nextIndex);
      }, 800);
    } else {
      completeOnboarding();
    }
  };

const completeOnboarding = async () => {
    try {
      console.log('Completing onboarding...');
      await AsyncStorage.setItem(STORAGE_KEYS.ONBOARDING_COMPLETED, 'true');
      
      await AsyncStorage.setItem(
        '@edupath_user_preferences',
        JSON.stringify(userResponses)
      );

      console.log('Onboarding complete, navigation will trigger automatically');
      // Don't navigate - let AppNavigator handle it by checking onboarding status
      // The useEffect in AppNavigator will detect the change
    } catch (error) {
      console.error('Error completing onboarding:', error);
    }
  };

const skipOnboarding = async () => {
    try {
      console.log('Skipping onboarding...');
      await AsyncStorage.setItem(STORAGE_KEYS.ONBOARDING_COMPLETED, 'true');
      // Don't navigate - let AppNavigator handle it
    } catch (error) {
      console.error('Error skipping onboarding:', error);
    }
  };
  const scrollToBottom = () => {
    if (flatListRef.current && messages.length > 0) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const renderMessage = ({ item }) => (
    <ChatBubble
      message={item.text}
      sender={item.sender}
      timestamp={item.timestamp}
    />
  );

  const currentQuestion = ONBOARDING_QUESTIONS[currentQuestionIndex];

return (
    <View style={styles.outerContainer}>
      {/* ✅ ADD: Responsive wrapper */}
      <View style={styles.container}>
       <View style={styles.header}>
        <Text style={styles.headerTitle}>Welcome to EduPath</Text>
        <TouchableOpacity onPress={skipOnboarding}>
          <Text style={styles.skipButton}>Skip</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messagesList}
        onContentSizeChange={scrollToBottom}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        {showOptions && currentQuestion?.options ? (
          <View style={styles.optionsContainer}>
            {currentQuestion.options.map((option, index) => (
              <TouchableOpacity
                key={index}
                style={styles.optionButton}
                onPress={() => handleOptionResponse(option)}
              >
                <Text style={styles.optionText}>{option}</Text>
              </TouchableOpacity>
            ))}
          </View>
        ) : currentQuestion?.type !== 'complete' ? (
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              placeholder="Type your answer..."
              placeholderTextColor={theme.colors.textLight}
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={500}
            />
            <TouchableOpacity
              style={[
                styles.sendButton,
                !inputText.trim() && styles.sendButtonDisabled,
              ]}
              onPress={handleTextResponse}
              disabled={!inputText.trim()}
            >
              <Text style={styles.sendButtonText}>Send</Text>
            </TouchableOpacity>
          </View>
        ) : (
  // ✅ ADD THIS: "Get Started" button for complete screen
  <View style={styles.completeContainer}>
    <TouchableOpacity
      style={styles.getStartedButton}
      onPress={completeOnboarding}
    >
      <Text style={styles.getStartedText}>🚀 Get Started</Text>
    </TouchableOpacity>
  </View>
)}
    </KeyboardAvoidingView>
      </View>
      {/* ✅ CLOSE: Responsive wrapper */}
    </View>
  );
};

const styles = StyleSheet.create({
  // Add to styles object
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.md,
    backgroundColor: theme.colors.background,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  headerTitle: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  skipButton: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  outerContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,  // White background outside chat
    alignItems: 'center',  // Center the chat container
  },
  container: {
    flex: 1,
    backgroundColor: theme.colors.chatBackground,
    width: '100%',
    maxWidth: theme.maxWidths.chat,  // 900px max width on desktop
  },
  messagesList: {
    padding: theme.spacing.md,
    flexGrow: 1,
  },
  optionsContainer: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  optionButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
    alignItems: 'center',
  },
  optionText: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: '600',
    color: theme.colors.text,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  input: {
    flex: 1,
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.lg,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.text,
    maxHeight: 100,
    marginRight: theme.spacing.sm,
  },
  sendButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.full,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: theme.colors.border,
  },
  sendButtonText: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  sendButtonText: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  // ✅ ADD THESE NEW STYLES:
  completeContainer: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  getStartedButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  getStartedText: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
});

export default OnboardingScreen;