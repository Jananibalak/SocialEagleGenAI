import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import { Feather } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  FadeInRight,
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  withSequence,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import Colors from '../constants/colors';
import { showAlert } from '../utils/alert';

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

const MessageBubble = ({ message, index }) => {
  const isUser = message.sender === 'user';
  
  return (
    <Animated.View
      entering={FadeInDown.delay(index * 30).duration(300)}
      style={[styles.messageContainer, isUser ? styles.userMessageContainer : styles.aiMessageContainer]}
    >
      {isUser ? (
        <LinearGradient
          colors={[Colors.accent, Colors.accentDark]}
          style={styles.messageBubble}
        >
          <Text style={styles.userMessageText}>{message.text}</Text>
        </LinearGradient>
      ) : (
        <View style={[styles.messageBubble, styles.aiMessageBubble]}>
          <Text style={styles.aiMessageText}>{message.text}</Text>
        </View>
      )}
      {message.sources && Object.keys(message.sources).length > 0 && (
        <Pressable
          style={styles.sourcesButton}
          onPress={() => {
            if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          }}
        >
          <Feather name="bookmark" size={12} color={Colors.textMuted} />
          <Text style={styles.sourcesText}>Sources</Text>
        </Pressable>
      )}
    </Animated.View>
  );
};

const TypingIndicator = () => {
  const dot1 = useSharedValue(0);
  const dot2 = useSharedValue(0);
  const dot3 = useSharedValue(0);

  useEffect(() => {
    dot1.value = withSequence(
      withTiming(1, { duration: 400 }),
      withTiming(0, { duration: 400 })
    );
    dot2.value = withSequence(
      withTiming(0, { duration: 200 }),
      withTiming(1, { duration: 400 }),
      withTiming(0, { duration: 400 })
    );
    dot3.value = withSequence(
      withTiming(0, { duration: 400 }),
      withTiming(1, { duration: 400 }),
      withTiming(0, { duration: 400 })
    );
  }, []);

  const dot1Style = useAnimatedStyle(() => ({
    opacity: dot1.value,
  }));
  const dot2Style = useAnimatedStyle(() => ({
    opacity: dot2.value,
  }));
  const dot3Style = useAnimatedStyle(() => ({
    opacity: dot3.value,
  }));

  return (
    <View style={styles.typingContainer}>
      <View style={styles.typingBubble}>
        <Animated.View style={[styles.typingDot, dot1Style]} />
        <Animated.View style={[styles.typingDot, dot2Style]} />
        <Animated.View style={[styles.typingDot, dot3Style]} />
      </View>
    </View>
  );
};

const ChatScreen = ({ route }) => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const { user, tokenBalance, freeMessagesLeft, useFreeMessage, loadTokenBalance } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  const flatListRef = useRef(null);
  const sendButtonScale = useSharedValue(1);

  const mentorId = route.params?.mentorId;
  const mentorName = route.params?.mentorName || 'Your Mentor';

  const getStorageKey = () => {
    if (!user?.id || !mentorId) return null;
    return `@edupath_chat_${user.id}_${mentorId}`;
  };

  useFocusEffect(
    React.useCallback(() => {
      if (mentorId && user?.id) {
        loadMessages();
      }
    }, [mentorId, user?.id])
  );

  const loadMessages = async () => {
    try {
      if (!mentorId) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiService.getChatHistory(mentorId);
        if (response.messages && response.messages.length > 0) {
          setMessages(response.messages);
          const storageKey = getStorageKey();
          if (storageKey) {
            await AsyncStorage.setItem(storageKey, JSON.stringify(response.messages));
          }
          setLoading(false);
          return;
        }
      } catch (apiError) {
        console.error('Database fetch failed:', apiError);
      }

      const storageKey = getStorageKey();
      if (storageKey) {
        const savedMessages = await AsyncStorage.getItem(storageKey);
        if (savedMessages) {
          setMessages(JSON.parse(savedMessages));
        } else {
          setMessages([]);
        }
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const saveMessages = async (newMessages) => {
    try {
      if (!mentorId || !user?.id) return;
      const storageKey = getStorageKey();
      if (storageKey) {
        await AsyncStorage.setItem(storageKey, JSON.stringify(newMessages));
      }
    } catch (error) {
      console.error('Error saving messages:', error);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || !mentorId) return;

    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    sendButtonScale.value = withSequence(
      withTiming(0.85, { duration: 100 }),
      withSpring(1, { damping: 8 })
    );

    const userMessage = {
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    saveMessages(updatedMessages);
    setInputText('');

    if (tokenBalance <= 0 && freeMessagesLeft <= 0) {
      showAlert(
        'No Messages Left',
        'You have used all your free messages. Would you like to purchase tokens?',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Buy Tokens', onPress: () => navigation.navigate('PlansTab') },
        ]
      );
      return;
    }

    setIsTyping(true);

    try {
      const historyToSend = updatedMessages.slice(-20).map(msg => ({
        sender: msg.sender,
        text: msg.text,
        timestamp: msg.timestamp,
      }));

      const response = await apiService.sendMessage(
        userMessage.text,
        mentorId,
        historyToSend
      );

      if (tokenBalance <= 0) {
        useFreeMessage();
      }

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        sources: response.sources || {},
      };

      const finalMessages = [...updatedMessages, aiMessage];
      setMessages(finalMessages);
      saveMessages(finalMessages);
      await loadTokenBalance();

      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      console.error('Error sending message:', error);
      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);

      if (error.response?.status === 402) {
        showAlert(
          'Insufficient Tokens',
          'You need more tokens to continue chatting.',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Buy Tokens', onPress: () => navigation.navigate('PlansTab') },
          ]
        );
      } else {
        showAlert('Error', 'Failed to send message. Please try again.');
      }
    } finally {
      setIsTyping(false);
    }
  };

  const sendButtonStyle = useAnimatedStyle(() => ({
    transform: [{ scale: sendButtonScale.value }],
  }));

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
          <Pressable onPress={() => navigation.goBack()} hitSlop={12}>
            <Feather name="arrow-left" size={22} color={Colors.white} />
          </Pressable>
          <Text style={styles.headerTitle}>{mentorName}</Text>
          <View style={{ width: 22 }} />
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={Colors.accent} />
          <Text style={styles.loadingText}>Opening conversation...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={[styles.header, { paddingTop: insets.top + 12 }]}>
        <Pressable
          onPress={() => {
            if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            navigation.goBack();
          }}
          hitSlop={12}
        >
          <Feather name="arrow-left" size={22} color={Colors.white} />
        </Pressable>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>{mentorName}</Text>
          <Text style={styles.headerSubtitle}>AI Learning Mentor</Text>
        </View>
        <View style={{ width: 22 }} />
      </View>

      <KeyboardAvoidingView
        style={styles.chatContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={({ item, index }) => <MessageBubble message={item} index={index} />}
          keyExtractor={(item) => item.id}
          contentContainerStyle={[
            styles.messagesList,
            { paddingBottom: insets.bottom + 80 },
          ]}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: false })}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <LinearGradient
                colors={[Colors.accent, Colors.accentDark]}
                style={styles.emptyIcon}
              >
                <Feather name="message-circle" size={32} color={Colors.primaryDark} />
              </LinearGradient>
              <Text style={styles.emptyTitle}>Start the conversation</Text>
              <Text style={styles.emptyText}>Ask your mentor anything to begin learning</Text>
            </View>
          }
        />
        {isTyping && <TypingIndicator />}

        <View style={[styles.inputContainer, { paddingBottom: insets.bottom + 12 }]}>
          <View style={styles.inputWrapper}>
            <TextInput
              style={styles.input}
              placeholder="Ask your mentor..."
              placeholderTextColor={Colors.textMuted}
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={500}
            />
            <AnimatedPressable
              style={[styles.sendButton, sendButtonStyle]}
              onPress={handleSend}
              disabled={!inputText.trim() || isTyping}
            >
              <LinearGradient
                colors={[Colors.accent, Colors.accentDark]}
                style={styles.sendButtonGradient}
              >
                <Feather name="send" size={18} color={Colors.primaryDark} />
              </LinearGradient>
            </AnimatedPressable>
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.06)',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 18,
    color: Colors.white,
  },
  headerSubtitle: {
    fontFamily: 'Inter_400Regular',
    fontSize: 12,
    color: Colors.textMuted,
    marginTop: 2,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 14,
    fontFamily: 'Inter_400Regular',
    color: Colors.textSecondary,
  },
  chatContainer: {
    flex: 1,
  },
  messagesList: {
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  messageContainer: {
    marginBottom: 12,
    maxWidth: '80%',
  },
  userMessageContainer: {
    alignSelf: 'flex-end',
  },
  aiMessageContainer: {
    alignSelf: 'flex-start',
  },
  messageBubble: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 16,
  },
  aiMessageBubble: {
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  userMessageText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    color: Colors.primaryDark,
    lineHeight: 20,
  },
  aiMessageText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    color: Colors.white,
    lineHeight: 20,
  },
  sourcesButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 6,
  },
  sourcesText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 11,
    color: Colors.textMuted,
  },
  typingContainer: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  typingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 16,
    alignSelf: 'flex-start',
    gap: 4,
  },
  typingDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.accent,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingTop: 80,
  },
  emptyIcon: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  emptyTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 18,
    color: Colors.white,
    marginBottom: 6,
  },
  emptyText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  inputContainer: {
    paddingHorizontal: 16,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.06)',
    backgroundColor: Colors.primary,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
  },
  input: {
    flex: 1,
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    color: Colors.white,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    maxHeight: 100,
  },
  sendButton: {
    borderRadius: 22,
    overflow: 'hidden',
  },
  sendButtonGradient: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 22,
  },
});

export default ChatScreen;
