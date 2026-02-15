import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { animations } from '../utils/animations';
import theme from '../config/theme';
import { toast } from 'react-toastify';
import { Plus, ChevronRight, Flame } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const LibraryScreen = () => {
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const cardsRef = useRef([]);

  useEffect(() => {
    loadMentors();
  }, []);

  useEffect(() => {
    if (mentors.length > 0 && cardsRef.current.length > 0) {
      animations.staggerSlideIn(cardsRef.current, {
        x: -100,
        opacity: 0,
        stagger: 0.1,
        duration: 0.6,
      });
    }
  }, [mentors]);

  const loadMentors = async () => {
    try {
      const response = await apiService.mentors.list();
      setMentors(response.data.mentors || []);
    } catch (error) {
      toast.error('Failed to load mentors');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.headerTitle}>
          {mentors.length} {mentors.length === 1 ? 'Mentor' : 'Mentors'}
        </h1>
        <button
          style={styles.newButton}
          onClick={() => navigate('/create-mentor')}
        >
          <Plus size={20} />
          <span>New</span>
        </button>
      </div>

      {mentors.length === 0 ? (
        <EmptyState navigate={navigate} />
      ) : (
        <div style={styles.mentorList}>
          {mentors.map((mentor, index) => (
            <MentorCard
              key={mentor.id}
              mentor={mentor}
              ref={(el) => (cardsRef.current[index] = el)}
              onClick={() => navigate(`/chat/${mentor.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const MentorCard = React.forwardRef(({ mentor, onClick }, ref) => {
  const cardRef = useRef(null);

  const handleMouseEnter = () => {
    if (cardRef.current) {
      animations.hoverLift(cardRef.current);
    }
  };

  const handleMouseLeave = () => {
    if (cardRef.current) {
      animations.fadeIn(cardRef.current, { y: 0, boxShadow: 'none', duration: 0.3 });
    }
  };

  return (
    <div
      ref={(el) => {
        cardRef.current = el;
        if (ref) {
          if (typeof ref === 'function') ref(el);
          else ref.current = el;
        }
      }}
      style={styles.card}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div style={styles.cardLeft}>
        <div style={styles.avatar}>{mentor.emoji || '📖'}</div>
      </div>

      <div style={styles.cardCenter}>
        <div style={styles.mentorName}>{mentor.name}</div>
        <div style={styles.mentorTopic}>{mentor.topic}</div>
        {mentor.last_message && (
          <div style={styles.lastMessage}>{mentor.last_message}</div>
        )}
      </div>

      <div style={styles.cardRight}>
        <div style={styles.badges}>
          {mentor.streak > 0 && (
            <div style={styles.streakBadge}>
              <Flame size={14} color={theme.colors.primary} />
              <span>{mentor.streak}</span>
            </div>
          )}
          {mentor.scrolls_count > 0 && (
            <div style={styles.scrollBadge}>{mentor.scrolls_count} 📜</div>
          )}
        </div>
        <ChevronRight size={20} color={theme.colors.neutral} />
      </div>
    </div>
  );
});

const EmptyState = ({ navigate }) => {
  const emptyRef = useRef(null);

  useEffect(() => {
    if (emptyRef.current) {
      animations.pulse(emptyRef.current, { scale: [1, 1.05, 1], duration: 2 });
    }
  }, []);

  return (
    <div style={styles.emptyContainer}>
      <div ref={emptyRef} style={styles.emptyContent}>
        <div style={styles.emptyIcon}>📚</div>
        <h2 style={styles.emptyTitle}>Create Your First Mentor</h2>
        <p style={styles.emptyText}>
          Upload a PDF or document to create an AI mentor that helps you learn
        </p>
        <button
          style={styles.createButton}
          onClick={() => navigate('/create-mentor')}
        >
          <Plus size={20} />
          <span>Create Mentor</span>
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: theme.spacing.lg,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.xl,
  },
  headerTitle: {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    fontFamily: theme.typography.fontFamily.display,
  },
  newButton: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
    backgroundColor: theme.colors.primary,
    color: theme.colors.dark,
    border: 'none',
    borderRadius: theme.borderRadius.full,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    cursor: 'pointer',
    transition: theme.transitions.base,
  },
  mentorList: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.sm,
  },
  card: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.white,
    borderRadius: theme.borderRadius.lg,
    border: `1px solid #e5e7eb`,
    cursor: 'pointer',
    transition: theme.transitions.base,
  },
  cardLeft: {
    flexShrink: 0,
  },
  avatar: {
    width: '60px',
    height: '60px',
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.background,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '32px',
  },
  cardCenter: {
    flex: 1,
    minWidth: 0,
  },
  mentorName: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.xs,
  },
  mentorTopic: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.secondary,
    marginBottom: theme.spacing.xs,
  },
  lastMessage: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  cardRight: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: theme.spacing.xs,
  },
  badges: {
    display: 'flex',
    gap: theme.spacing.xs,
  },
  streakBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '2px',
    padding: `2px ${theme.spacing.xs}`,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.sm,
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.dark,
  },
  scrollBadge: {
    padding: `2px ${theme.spacing.xs}`,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.sm,
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.neutral,
  },
  emptyContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
  },
  emptyContent: {
    textAlign: 'center',
    maxWidth: '400px',
  },
  emptyIcon: {
    fontSize: '80px',
    marginBottom: theme.spacing.lg,
  },
  emptyTitle: {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.md,
    fontFamily: theme.typography.fontFamily.display,
  },
  emptyText: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.neutral,
    marginBottom: theme.spacing.xl,
    lineHeight: '1.6',
  },
  createButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    padding: `${theme.spacing.md} ${theme.spacing.xl}`,
    backgroundColor: theme.colors.primary,
    color: theme.colors.dark,
    border: 'none',
    borderRadius: theme.borderRadius.full,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    cursor: 'pointer',
    transition: theme.transitions.base,
  },
};

export default LibraryScreen;
