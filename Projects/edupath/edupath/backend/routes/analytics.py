# 📊 COMPLETE ANALYTICS WITH OPENROUTER GPT-4O-MINI INSIGHTS

from flask import Blueprint, jsonify, request
from backend.auth.jwt_handler import require_auth
from shared.database import SessionLocal
from backend.models.learning_mentor import MentorMessage, LearningMentor, KnowledgeScroll
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import requests
import os
import json

analytics_bp = Blueprint('analytics', __name__)

# ✅ OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

@analytics_bp.route('/stats', methods=['GET'])
@require_auth
def get_user_analytics():
    """Get comprehensive analytics with GPT-4o-mini powered creative insights"""
    try:
        db = SessionLocal()
        user_id = request.user_id
        
        # Get all user's mentors
        mentors = db.query(LearningMentor).filter_by(user_id=user_id).all()
        
        if not mentors:
            return jsonify({
                'success': True,
                'analytics': get_empty_analytics()
            }), 200
        
        # Collect comprehensive stats
        mentor_stats = []
        total_user_messages = 0
        total_tokens = 0
        total_knowledge_points = 0
        total_scrolls = 0
        active_dates_global = set()
        all_messages_by_hour = [0] * 24
        all_messages_by_day = [0] * 7
        
        now = datetime.now(timezone.utc)
        
        # ✅ PROCESS EACH MENTOR WITH ALL FIELDS
        for mentor in mentors:
            # Get messages
            messages = db.query(MentorMessage).filter(
                MentorMessage.mentor_id == mentor.id
            ).order_by(MentorMessage.timestamp).all()
            
            user_messages = [m for m in messages if m.sender == 'user']
            ai_messages = [m for m in messages if m.sender == 'ai']
            
            # Get knowledge scrolls
            scrolls = db.query(KnowledgeScroll).filter(
                KnowledgeScroll.mentor_id == mentor.id
            ).all()
            
            # Calculate streak
            current_streak, longest_streak, active_dates = calculate_mentor_streak(user_messages)
            
            # Token usage
            mentor_tokens = sum(m.tokens_used for m in messages if m.tokens_used)
            total_tokens += mentor_tokens
            
            # Activity patterns
            activity_by_hour = [0] * 24
            activity_by_day = [0] * 7
            for msg in user_messages:
                msg_time = msg.timestamp
                if msg_time.tzinfo is None:
                    msg_time = msg_time.replace(tzinfo=timezone.utc)
                activity_by_hour[msg_time.hour] += 1
                activity_by_day[msg_time.weekday()] += 1
                all_messages_by_hour[msg_time.hour] += 1
                all_messages_by_day[msg_time.weekday()] += 1
            
            # Last activity
            if user_messages:
                last_message = max(user_messages, key=lambda m: m.timestamp)
                last_msg_time = last_message.timestamp
                if last_msg_time.tzinfo is None:
                    last_msg_time = last_msg_time.replace(tzinfo=timezone.utc)
                days_since_last = (now - last_msg_time).days
            else:
                last_msg_time = None
                days_since_last = None
            
            # Status determination
            if mentor.plan_status == 'completed':
                status = 'completed'
            elif mentor.plan_status == 'paused':
                status = 'paused'
            elif current_streak > 0:
                status = 'active'
            elif days_since_last and days_since_last <= 7:
                status = 'recent'
            else:
                status = 'inactive'
            
            # Learning progress
            progress_percentage = 0
            if mentor.target_days and mentor.target_days > 0:
                progress_percentage = (mentor.current_day / mentor.target_days) * 100
            
            # Peak hour
            peak_hour = activity_by_hour.index(max(activity_by_hour)) if max(activity_by_hour) > 0 else 0
            
            # Scroll stats
            scroll_stats = {
                'total_scrolls': len(scrolls),
                'processed': sum(1 for s in scrolls if s.processed_at),
                'total_size_mb': round(sum(s.file_size or 0 for s in scrolls) / (1024 * 1024), 2),
                'file_types': count_file_types(scrolls),
            }
            
            mentor_stats.append({
                'mentor_id': mentor.id,
                'mentor_name': mentor.name,
                'mentor_emoji': mentor.avatar_emoji or '📚',  # ✅ CORRECT FIELD
                'topic': mentor.topic,
                'personality': mentor.personality,
                
                # Messages
                'message_count': len(user_messages),
                'total_conversations': len(messages),
                'ai_responses': len(ai_messages),
                
                # Streak & Activity
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'db_current_streak': mentor.current_streak,  # From DB
                'active_days': len(active_dates),
                'last_message_date': last_msg_time.isoformat() if last_msg_time else None,
                'days_since_last': days_since_last,
                'status': status,
                
                # Learning Plan
                'plan_status': mentor.plan_status,
                'current_day': mentor.current_day,
                'target_days': mentor.target_days,
                'progress_percentage': round(progress_percentage, 1),
                'goal_description': mentor.goal_description,
                'deadline': mentor.deadline.isoformat() if mentor.deadline else None,
                
                # Knowledge & Tokens
                'knowledge_points': mentor.knowledge_points or 0,
                'tokens_used': mentor_tokens,
                'avg_tokens_per_message': round(mentor_tokens / len(messages), 2) if messages else 0,
                'knowledge_per_token': round(mentor.knowledge_points / mentor_tokens, 4) if mentor_tokens > 0 else 0,
                
                # Scrolls
                'scrolls': scroll_stats,
                
                # Activity patterns
                'activity_by_hour': activity_by_hour,
                'activity_by_day': activity_by_day,
                'peak_hour': peak_hour,
            })
            
            total_user_messages += len(user_messages)
            total_knowledge_points += (mentor.knowledge_points or 0)
            total_scrolls += len(scrolls)
            active_dates_global.update(active_dates)
        
        # Sort by knowledge points
        mentor_stats.sort(key=lambda x: x['knowledge_points'], reverse=True)
        
        # Global statistics
        active_mentors = sum(1 for m in mentor_stats if m['status'] == 'active')
        total_current_streaks = sum(m['current_streak'] for m in mentor_stats)
        longest_current_streak = max((m['current_streak'] for m in mentor_stats), default=0)
        global_peak_hour = all_messages_by_hour.index(max(all_messages_by_hour)) if max(all_messages_by_hour) > 0 else 0
        
        # ✅ GENERATE CREATIVE GPT-4O-MINI INSIGHTS
        llm_insights = generate_gpt_insights(
            mentor_stats,
            total_user_messages,
            total_knowledge_points,
            active_mentors,
            len(mentors)
        )
        
        # Standard insights
        standard_insights = generate_standard_insights(
            mentor_stats,
            total_user_messages,
            len(mentors),
            active_mentors,
            total_current_streaks
        )
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_messages': total_user_messages,
                'active_days': len(active_dates_global),
                'mentors_count': len(mentors),
                'total_knowledge_points': total_knowledge_points,
                'total_tokens_used': total_tokens,
                'total_scrolls': total_scrolls,
                
                'mentor_stats': mentor_stats,
                'llm_insights': llm_insights,  # ✅ Creative GPT insights
                'global_insights': standard_insights,
                
                'activity_summary': {
                    'total_mentors': len(mentors),
                    'active_mentors': active_mentors,
                    'completed_mentors': sum(1 for m in mentor_stats if m['status'] == 'completed'),
                    'paused_mentors': sum(1 for m in mentor_stats if m['status'] == 'paused'),
                    'total_streaks': total_current_streaks,
                    'longest_streak': longest_current_streak,
                    'global_peak_hour': global_peak_hour,
                    'activity_by_hour': all_messages_by_hour,
                    'activity_by_day': all_messages_by_day,
                    'avg_knowledge_per_message': round(total_knowledge_points / total_user_messages, 2) if total_user_messages > 0 else 0,
                }
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching analytics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


def calculate_mentor_streak(messages):
    """Calculate streak for a specific mentor"""
    if not messages:
        return 0, 0, set()
    
    dates = []
    for m in messages:
        msg_time = m.timestamp
        if msg_time.tzinfo is None:
            msg_time = msg_time.replace(tzinfo=timezone.utc)
        dates.append(msg_time.date())
    
    dates = sorted(set(dates))
    active_dates = set(dates)
    
    if not dates:
        return 0, 0, set()
    
    today = datetime.now(timezone.utc).date()
    
    # Calculate current streak
    current_streak = 0
    if dates[-1] == today or dates[-1] == today - timedelta(days=1):
        current_streak = 1
        check_date = dates[-1] - timedelta(days=1)
        
        for i in range(len(dates) - 2, -1, -1):
            if dates[i] == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
    
    # Calculate longest streak
    longest_streak = 1
    temp_streak = 1
    
    for i in range(1, len(dates)):
        if dates[i] == dates[i-1] + timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    return current_streak, longest_streak, active_dates


def count_file_types(scrolls):
    """Count scrolls by file type"""
    types = defaultdict(int)
    for scroll in scrolls:
        types[scroll.file_type or 'unknown'] += 1
    return dict(types)


def generate_gpt_insights(mentor_stats, total_messages, total_knowledge_points, active_mentors, total_mentors):
    """
    🤖 USE GPT-4O-MINI (via OpenRouter) TO GENERATE CREATIVE, ENCOURAGING INSIGHTS
    Focus on learning progress, motivation, and achievements - not tokens!
    """
    try:
        if not OPENROUTER_API_KEY:
            print("⚠️ No OpenRouter API key found, using fallback insights")
            return get_fallback_gpt_insights(mentor_stats, total_messages, total_knowledge_points)
        
        # Prepare data for GPT
        mentors_summary = []
        for m in mentor_stats[:5]:  # Top 5 mentors
            mentors_summary.append({
                'name': m['mentor_name'],
                'emoji': m['mentor_emoji'],
                'topic': m['topic'],
                'messages': m['message_count'],
                'knowledge_points': m['knowledge_points'],
                'streak': m['current_streak'],
                'progress': m['progress_percentage'],
                'status': m['status'],
                'days_active': m['active_days'],
            })
        
        prompt = f"""You are an enthusiastic learning coach analyzing a student's progress. Generate 3-4 creative, encouraging insights based on their learning data.

Student's Learning Summary:
- Total messages: {total_messages}
- Knowledge points earned: {total_knowledge_points}
- Active mentors: {active_mentors}/{total_mentors}
- Mentors: {json.dumps(mentors_summary, indent=2)}

Generate insights that:
1. Celebrate achievements (streaks, knowledge points, consistency)
2. Encourage continued learning (gentle nudges for inactive mentors)
3. Highlight interesting patterns (favorite topics, learning style)
4. Provide motivational messages (you're building expertise!)

Format each insight as JSON:
{{
  "type": "celebration|encouragement|pattern|motivation",
  "icon": "fire|star|target|trophy|book|zap|award|smile|check-circle",
  "title": "Short catchy title (max 40 chars)",
  "message": "Encouraging message (max 80 chars)"
}}

Return ONLY a valid JSON array of 3-4 insights. No markdown, no explanations, just the JSON array."""

        # ✅ Call OpenRouter with GPT-4o-mini
        response = requests.post(
            OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            insights_text = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            insights_text = insights_text.strip()
            
            # Remove markdown code blocks if present
            if insights_text.startswith('```'):
                insights_text = insights_text.split('```')[1]
                if insights_text.startswith('json'):
                    insights_text = insights_text[4:]
            
            # Parse JSON
            llm_insights = json.loads(insights_text)
            
            # Validate and limit to 4 insights
            if isinstance(llm_insights, list) and len(llm_insights) > 0:
                return llm_insights[:4]
            else:
                return get_fallback_gpt_insights(mentor_stats, total_messages, total_knowledge_points)
        else:
            print(f"⚠️ OpenRouter API error: {response.status_code}")
            return get_fallback_gpt_insights(mentor_stats, total_messages, total_knowledge_points)
            
    except Exception as e:
        print(f"⚠️ GPT insights generation failed: {e}")
        import traceback
        traceback.print_exc()
        return get_fallback_gpt_insights(mentor_stats, total_messages, total_knowledge_points)


def get_fallback_gpt_insights(mentor_stats, total_messages, total_knowledge_points):
    """Fallback creative insights if GPT fails"""
    insights = []
    
    # Knowledge points celebration
    if total_knowledge_points > 500:
        insights.append({
            'type': 'celebration',
            'icon': 'trophy',
            'title': 'Knowledge Master! 🏆',
            'message': f'{total_knowledge_points} points earned! You\'re building real expertise!'
        })
    elif total_knowledge_points > 100:
        insights.append({
            'type': 'celebration',
            'icon': 'star',
            'title': 'Growing Strong! ⭐',
            'message': f'{total_knowledge_points} knowledge points! Keep the momentum going!'
        })
    elif total_knowledge_points > 0:
        insights.append({
            'type': 'motivation',
            'icon': 'smile',
            'title': 'Great Start!',
            'message': f'{total_knowledge_points} points earned! You\'re on your way!'
        })
    
    # Streak celebration
    if mentor_stats:
        top = mentor_stats[0]
        if top['current_streak'] >= 7:
            insights.append({
                'type': 'pattern',
                'icon': 'fire',
                'title': f'{top["mentor_emoji"]} {top["mentor_name"]} Champion!',
                'message': f'Incredible {top["current_streak"]}-day streak! You\'re unstoppable!'
            })
        elif top['current_streak'] >= 3:
            insights.append({
                'type': 'encouragement',
                'icon': 'zap',
                'title': f'{top["mentor_emoji"]} On Fire!',
                'message': f'{top["current_streak"]}-day streak! Consistency is key!'
            })
    
    # Multi-mentor engagement
    active_count = sum(1 for m in mentor_stats if m['status'] == 'active')
    if active_count >= 3:
        insights.append({
            'type': 'encouragement',
            'icon': 'award',
            'title': 'Multi-Tasking Legend!',
            'message': f'{active_count} active mentors! Your curiosity knows no bounds!'
        })
    elif active_count >= 2:
        insights.append({
            'type': 'positive',
            'icon': 'check-circle',
            'title': 'Diverse Learner!',
            'message': f'{active_count} topics active! Love your versatility!'
        })
    
    # Message milestone
    if total_messages >= 100:
        insights.append({
            'type': 'celebration',
            'icon': 'trophy',
            'title': 'Century Club! 🎉',
            'message': f'{total_messages} messages sent! You\'re dedicated!'
        })
    
    return insights[:4]


def generate_standard_insights(mentor_stats, total_messages, total_mentors, active_mentors, total_streaks):
    """Standard insights (not LLM-powered)"""
    insights = []
    
    # Active mentors
    if active_mentors == total_mentors and total_mentors > 1:
        insights.append({
            'type': 'achievement',
            'icon': 'check-circle',
            'title': 'Full Engagement! 🎯',
            'message': f'All {total_mentors} mentors are active!'
        })
    elif active_mentors > 0:
        insights.append({
            'type': 'positive',
            'icon': 'activity',
            'title': 'Multi-Topic Learning',
            'message': f'{active_mentors} of {total_mentors} mentors active!'
        })
    
    # Inactive mentors
    inactive = [m for m in mentor_stats if m['status'] == 'inactive' and m['message_count'] > 0]
    if inactive:
        m = inactive[0]
        insights.append({
            'type': 'reminder',
            'icon': 'clock',
            'title': f'{m["mentor_emoji"]} {m["mentor_name"]} Waiting',
            'message': f'{m["days_since_last"]} days idle. Resume {m["topic"]}?'
        })
    
    # Completed mentors
    completed = [m for m in mentor_stats if m['status'] == 'completed']
    if completed:
        insights.append({
            'type': 'achievement',
            'icon': 'award',
            'title': f'{len(completed)} Plans Completed! 🎓',
            'message': 'You\'re crushing your learning goals!'
        })
    
    return insights[:5]


def get_empty_analytics():
    """Return empty analytics structure"""
    return {
        'total_messages': 0,
        'active_days': 0,
        'mentors_count': 0,
        'total_knowledge_points': 0,
        'total_tokens_used': 0,
        'total_scrolls': 0,
        'mentor_stats': [],
        'llm_insights': [],
        'global_insights': [{
            'type': 'motivation',
            'icon': 'plus-circle',
            'title': 'Start Your Journey!',
            'message': 'Create your first mentor and begin learning!'
        }],
        'activity_summary': {
            'total_mentors': 0,
            'active_mentors': 0,
            'completed_mentors': 0,
            'paused_mentors': 0,
            'total_streaks': 0,
            'longest_streak': 0,
            'global_peak_hour': 0,
            'activity_by_hour': [0] * 24,
            'activity_by_day': [0] * 7,
            'avg_knowledge_per_message': 0,
        }
    }