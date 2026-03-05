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
  ActivityIndicator,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { useFocusEffect } from '@react-navigation/native';
import theme from '../config/theme';
import TopNavbar from '../components/TopNavbar';
import ChatBubble from '../components/ChatBubble';

const ChatScreen = ({ navigation, route }) => {
  const { user, tokenBalance, freeMessagesLeft, useFreeMessage, loadTokenBalance } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  const flatListRef = useRef(null);

  const mentorId = route.params?.mentorId;
  const mentorName = route.params?.mentorName || 'Your Mentor';

  // ✅ FIX: Define getStorageKey function
  const getStorageKey = () => {
    if (!user?.id || !mentorId) {
      console.error('❌ Cannot generate storage key: missing user.id or mentorId');
      return null;
    }
    return `@edupath_chat_${user.id}_${mentorId}`;
  };

  // Load messages when screen comes into focus
  useFocusEffect(
    React.useCallback(() => {
      if (mentorId && user?.id) {
        console.log(`📱 Chat screen focused for mentor ${mentorId}`);
        loadMessages();
      }
    }, [mentorId, user?.id])
  );

  const loadMessages = async () => {
    try {
      if (!mentorId) {
        console.error('❌ Cannot load messages: missing mentorId');
        setLoading(false);
        return;
      }

      console.log(`📂 Loading messages from database for mentor ${mentorId}`);
      
      // ✅ Fetch from database
      try {
        const response = await apiService.getChatHistory(mentorId);
        
        if (response.messages && response.messages.length > 0) {
          console.log(`✅ Loaded ${response.messages.length} messages from database`);
          setMessages(response.messages);
          
          // Also save to AsyncStorage as backup
          const storageKey = getStorageKey();
          if (storageKey) {
            await AsyncStorage.setItem(storageKey, JSON.stringify(response.messages));
          }
          
          setLoading(false);
          return;
        } else {
          console.log(`📭 No messages found in database for mentor ${mentorId}`);
        }
      } catch (apiError) {
        console.error('⚠️ Database fetch failed:', apiError);
      }
      
      // ✅ Fallback to AsyncStorage
      console.log('🔄 Trying AsyncStorage fallback...');
      const storageKey = getStorageKey();
      
      if (storageKey) {
        const savedMessages = await AsyncStorage.getItem(storageKey);
        
        if (savedMessages) {
          const parsed = JSON.parse(savedMessages);
          console.log(`✅ Loaded ${parsed.length} messages from AsyncStorage`);
          setMessages(parsed);
        } else {
          console.log('📭 No messages in AsyncStorage either');
          setMessages([]);
        }
      } else {
        setMessages([]);
      }
      
    } catch (error) {
      console.error('❌ Error loading messages:', error);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const saveMessages = async (newMessages) => {
    try {
      if (!mentorId || !user?.id) {
        console.error('❌ Cannot save messages: missing mentorId or user.id');
        return;
      }

      const storageKey = getStorageKey();
      if (storageKey) {
        await AsyncStorage.setItem(storageKey, JSON.stringify(newMessages));
        console.log(`💾 Saved ${newMessages.length} messages to AsyncStorage`);
      }
    } catch (error) {
      console.error('❌ Error saving messages:', error);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || !mentorId) {
      console.log('⚠️ Cannot send: empty message or no mentor ID');
      return;
    }

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
      Alert.alert(
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
      console.log(`📤 Sending message to mentor ${mentorId}`);
      
      const historyToSend = updatedMessages.slice(-20).map(msg => ({
        sender: msg.sender,
        text: msg.text,
        timestamp: msg.timestamp
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
    } catch (error) {
      console.error('❌ Error sending message:', error);

      if (error.response?.status === 402) {
        Alert.alert(
          'Insufficient Tokens',
          'You need more tokens to continue chatting.',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Buy Tokens', onPress: () => navigation.navigate('PlansTab') },
          ]
        );
      } else {
        Alert.alert('Error', 'Failed to send message. Please try again.');
      }
    } finally {
      setIsTyping(false);
    }
  };

  const renderMessage = ({ item }) => (
    <ChatBubble
      message={item.text}
      sender={item.sender}
      timestamp={item.timestamp}
      sources={item.sources}
    />
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <TopNavbar title={mentorName} showProfile={false} />
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={styles.loadingText}>Opening conversation...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <TopNavbar title={mentorName} showProfile={false} />
      
      <KeyboardAvoidingView
        style={styles.chatContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.messagesList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
          onLayout={() => flatListRef.current?.scrollToEnd()}
        />

        {isTyping && (
          <View style={styles.typingContainer}>
            <ActivityIndicator size="small" color={theme.colors.primary} />
            <Text style={styles.typingText}>{mentorName} is thinking...</Text>
          </View>
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your message..."
            placeholderTextColor={theme.colors.textLight}
            multiline
            maxLength={500}
          />
          <TouchableOpacity
            style={[styles.sendButton, !inputText.trim() && styles.sendButtonDisabled]}
            onPress={handleSend}
            disabled={!inputText.trim() || isTyping}
          >
            <Text style={styles.sendButtonText}>→</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  chatContainer: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: theme.spacing.md,
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.textSecondary,
  },
  messagesList: {
    padding: theme.spacing.lg,
  },
  typingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.backgroundSecondary,
  },
  typingText: {
    marginLeft: theme.spacing.sm,
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    backgroundColor: theme.colors.backgroundSecondary,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    ...theme.shadows.sm,
  },
  input: {
    flex: 1,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.xl,
    borderWidth: 1,
    borderColor: theme.colors.border,
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
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    ...theme.shadows.md,
  },
  sendButtonDisabled: {
    backgroundColor: theme.colors.border,
    opacity: 0.5,
  },
  sendButtonText: {
    fontSize: 24,
    fontWeight: theme.fonts.weights.bold,
    color: theme.colors.secondaryDeep,
  },
});

export default ChatScreen;