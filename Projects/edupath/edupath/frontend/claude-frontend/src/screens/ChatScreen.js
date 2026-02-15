import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { animations } from '../utils/animations';
import theme from '../config/theme';
import { toast } from 'react-toastify';
import { ArrowLeft, Send } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const ChatScreen = () => {
  const { mentorId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [mentor, setMentor] = useState(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  useEffect(() => {
    loadChatHistory();
  }, [mentorId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await apiService.chat.getHistory(mentorId);
      setMessages(response.data.messages || []);
      // Load mentor info from mentors list
      const mentorsResponse = await apiService.mentors.list();
      const currentMentor = mentorsResponse.data.mentors?.find(m => m.id === mentorId);
      setMentor(currentMentor);
    } catch (error) {
      toast.error('Failed to load chat history');
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      animations.scrollToBottom(messagesContainerRef.current);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || sending) return;

    const userMessage = {
      id: `temp_${Date.now()}`,
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setSending(true);

    try {
      const conversationHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text,
      }));

      const response = await apiService.chat.send({
        message: input,
        mentor_id: mentorId,
        conversation_history: conversationHistory,
      });

      const aiMessage = {
        id: `ai_${Date.now()}`,
        text: response.data.response,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        sources: response.data.sources,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      toast.error('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <button style={styles.backButton} onClick={() => navigate('/library')}>
          <ArrowLeft size={24} />
        </button>
        <div style={styles.avatar}>{mentor?.emoji || '📖'}</div>
        <div style={styles.headerInfo}>
          <div style={styles.mentorName}>{mentor?.name || 'Mentor'}</div>
          <div style={styles.mentorTopic}>{mentor?.topic || 'Learning'}</div>
        </div>
      </div>

      <div ref={messagesContainerRef} style={styles.messagesContainer}>
        {messages.map((message, index) => (
          <Message key={message.id || index} message={message} />
        ))}
        {sending && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputBar}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question..."
          style={styles.input}
          disabled={sending}
        />
        <button
          onClick={handleSend}
          style={{
            ...styles.sendButton,
            opacity: input.trim() && !sending ? 1 : 0.5,
          }}
          disabled={!input.trim() || sending}
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

const Message = ({ message }) => {
  const messageRef = useRef(null);
  const isUser = message.sender === 'user';

  useEffect(() => {
    if (messageRef.current) {
      animations.slideInRight(messageRef.current, {
        x: isUser ? 100 : -100,
        opacity: 0,
        duration: 0.4,
      });
    }
  }, []);

  return (
    <div
      ref={messageRef}
      style={{
        ...styles.messageWrapper,
        justifyContent: isUser ? 'flex-end' : 'flex-start',
      }}
    >
      <div
        style={{
          ...styles.bubble,
          ...(isUser ? styles.userBubble : styles.aiBubble),
        }}
      >
        <div style={styles.messageText}>{message.text}</div>
        {message.sources && (
          <div style={styles.sources}>
            {message.sources.knowledge_graph?.map((source, idx) => (
              <span key={idx} style={styles.sourceChip}>📄 {source}</span>
            ))}
            {message.sources.web_search?.map((source, idx) => (
              <span key={idx} style={styles.sourceChip}>🌐 {source}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const TypingIndicator = () => {
  const dotsRef = useRef([]);

  useEffect(() => {
    if (dotsRef.current.length === 3) {
      animations.typingDots(dotsRef.current);
    }
  }, []);

  return (
    <div style={styles.messageWrapper}>
      <div style={{ ...styles.bubble, ...styles.aiBubble }}>
        <div style={styles.typingDots}>
          {[0, 1, 2].map(i => (
            <span
              key={i}
              ref={el => (dotsRef.current[i] = el)}
              style={styles.dot}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: 'calc(100vh - 64px)',
    backgroundColor: theme.colors.background,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.white,
    borderBottom: '1px solid #e5e7eb',
  },
  backButton: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: theme.spacing.xs,
    color: theme.colors.dark,
  },
  avatar: {
    width: '40px',
    height: '40px',
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.background,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
  },
  headerInfo: {
    flex: 1,
  },
  mentorName: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.dark,
  },
  mentorTopic: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: theme.spacing.lg,
  },
  messageWrapper: {
    display: 'flex',
    marginBottom: theme.spacing.md,
  },
  bubble: {
    maxWidth: '70%',
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.lg,
  },
  userBubble: {
    backgroundColor: theme.colors.primary,
    color: theme.colors.dark,
    borderBottomRightRadius: theme.borderRadius.sm,
  },
  aiBubble: {
    backgroundColor: theme.colors.white,
    color: theme.colors.dark,
    borderBottomLeftRadius: theme.borderRadius.sm,
    border: '1px solid #e5e7eb',
  },
  messageText: {
    fontSize: theme.typography.fontSize.base,
    lineHeight: '1.6',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  sources: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: theme.spacing.xs,
    marginTop: theme.spacing.sm,
  },
  sourceChip: {
    fontSize: theme.typography.fontSize.xs,
    padding: `2px ${theme.spacing.xs}`,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.sm,
    color: theme.colors.neutral,
  },
  typingDots: {
    display: 'flex',
    gap: theme.spacing.xs,
    alignItems: 'center',
  },
  dot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: theme.colors.neutral,
  },
  inputBar: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.white,
    borderTop: '1px solid #e5e7eb',
  },
  input: {
    flex: 1,
    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
    fontSize: theme.typography.fontSize.base,
    border: `2px solid #e5e7eb`,
    borderRadius: theme.borderRadius.full,
    outline: 'none',
  },
  sendButton: {
    width: '44px',
    height: '44px',
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.primary,
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: theme.colors.dark,
    transition: theme.transitions.base,
  },
};

export default ChatScreen;
