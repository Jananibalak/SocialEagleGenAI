from openai import OpenAI
from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

class AICoach:
    """
    Personal learning coach that provides:
    - Daily check-ins and motivation
    - Progress analysis
    - Personalized recommendations
    - Adaptive learning paths
    - Struggle detection and support
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
    
        # Verify API key exists
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment variables. "
                "Please check your .env file."
            )
    
        # OpenRouter requires these specific settings
        self.client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=self.api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",  # Your app URL
            "X-Title": "EduPath Learning Assistant"   # Your app name
        }
        )
    
        self.model = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
    
        #    Coach personality traits
        self.coach_persona = {
            "name": "Alex",
            "style": "encouraging, data-driven, adaptive",
            "tone": "friendly but professional, like a supportive personal trainer"
        }
    
        print(f"✓ AI Coach initialized")
        print(f"  Using model: {self.model}")
        print(f"  API key configured: {self.api_key[:20]}...")
    # ═══════════════════════════════════════════════════════════════
    # DAILY CHECK-INS
    # ═══════════════════════════════════════════════════════════════
    
    def generate_morning_checkin(
        self, 
        user_data: Dict,
        learning_history: List[Dict],
        knowledge_state: Dict
    ) -> Dict:
        """
        Generate personalized morning check-in message
        
        Args:
            user_data: User profile and stats
            learning_history: Recent learning sessions
            knowledge_state: Current mastery levels from graph
        
        Returns:
            {
                "greeting": str,
                "motivation": str,
                "today_plan": str,
                "recommended_duration": int,
                "suggested_topics": List[str],
                "encouragement": str
            }
        """
        
        # Analyze context
        context = self._build_morning_context(user_data, learning_history, knowledge_state)
        
        prompt = f"""
You are {self.coach_persona['name']}, a {self.coach_persona['style']} personal learning coach.

STUDENT CONTEXT:
{json.dumps(context, indent=2)}

Generate a morning check-in for the student. Include:

1. PERSONALIZED GREETING
   - Reference their current streak or recent progress
   - Acknowledge any struggles or wins from yesterday
   
2. TODAY'S MOTIVATION
   - Inspire them to start the day
   - Connect to their long-term goal
   - Be specific, not generic
   
3. TODAY'S PLAN
   - Suggest what to focus on (based on knowledge graph)
   - Explain WHY this topic (show the connection)
   - Realistic time commitment
   
4. ENCOURAGEMENT
   - End on a positive, energizing note
   - Use their name: {user_data.get('full_name', 'there')}

TONE: {self.coach_persona['tone']}

Return ONLY a JSON object:
{{
  "greeting": "personalized greeting",
  "motivation": "today's motivation",
  "today_plan": "what to focus on and why",
  "recommended_duration": 60,
  "suggested_topics": ["topic1", "topic2"],
  "encouragement": "final encouragement"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are {self.coach_persona['name']}, an expert learning coach. Always return valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Slightly creative for personality
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result['timestamp'] = datetime.now().isoformat()
            result['streak'] = user_data.get('current_streak', 0)
            
            return result
            
        except Exception as e:
            print(f"Error generating morning check-in: {e}")
            return self._fallback_morning_checkin(user_data)
    
    def generate_evening_reflection(
        self,
        user_data: Dict,
        today_session: Optional[Dict],
        knowledge_gained: List[str]
    ) -> Dict:
        """
        Generate evening reflection and progress summary
        
        Args:
            user_data: User profile
            today_session: Today's learning session (if any)
            knowledge_gained: Concepts learned today
        
        Returns:
            {
                "summary": str,
                "progress_analysis": str,
                "wins": List[str],
                "areas_to_improve": List[str],
                "tomorrow_preview": str,
                "reflection_questions": List[str]
            }
        """
        
        if not today_session:
            return self._generate_missed_day_reflection(user_data)
        
        context = {
            "session": today_session,
            "knowledge_gained": knowledge_gained,
            "user_goal": user_data.get('learning_goal'),
            "total_sessions": user_data.get('total_sessions', 0),
            "streak": user_data.get('current_streak', 0)
        }
        
        prompt = f"""
You are {self.coach_persona['name']}, analyzing a student's learning session.

SESSION DATA:
{json.dumps(context, indent=2)}

Provide evening reflection with:

1. SESSION SUMMARY
   - What they learned today
   - Time invested
   - Quality assessment (based on ratings)
   
2. PROGRESS ANALYSIS
   - How today fits into their bigger goal
   - Progress toward mastery
   - Pattern observations
   
3. CELEBRATE WINS
   - Specific accomplishments (be genuine)
   - Streak continuation
   - Concepts mastered
   
4. CONSTRUCTIVE FEEDBACK
   - Areas for improvement (if any)
   - Suggestions (not criticism)
   
5. TOMORROW PREVIEW
   - What's next in their journey
   - Build anticipation
   
6. REFLECTION QUESTIONS
   - 2-3 thought-provoking questions
   - Help them think deeper about learning

TONE: Encouraging but honest. Celebrate progress, gently address struggles.

Return JSON:
{{
  "summary": "session summary",
  "progress_analysis": "progress toward goal",
  "wins": ["win1", "win2", "win3"],
  "areas_to_improve": ["area1", "area2"],
  "tomorrow_preview": "what's next",
  "reflection_questions": ["q1", "q2", "q3"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an insightful learning coach. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating evening reflection: {e}")
            return self._fallback_evening_reflection()
    
    # ═══════════════════════════════════════════════════════════════
    # PROGRESS ANALYSIS
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_learning_patterns(
        self,
        sessions: List[Dict],
        timeframe_days: int = 30
    ) -> Dict:
        """
        Analyze learning patterns over time
        
        Identifies:
        - Optimal learning times
        - Difficulty patterns
        - Consistency trends
        - Struggling areas
        - Strengths
        
        Args:
            sessions: List of recent learning sessions
            timeframe_days: How many days to analyze
        
        Returns:
            {
                "optimal_time": str,
                "average_session_length": int,
                "consistency_score": float,
                "struggling_topics": List[Dict],
                "mastered_topics": List[Dict],
                "recommendations": List[str],
                "insights": List[str]
            }
        """
        
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        # Prepare session data for analysis
        session_summary = self._prepare_session_summary(sessions)
        
        prompt = f"""
You are an expert learning analytics coach analyzing a student's learning patterns.

SESSION DATA (last {timeframe_days} days):
{json.dumps(session_summary, indent=2)}

Analyze and provide insights on:

1. OPTIMAL LEARNING TIME
   - When are they most productive?
   - Based on understanding ratings and duration
   
2. SESSION LENGTH PATTERNS
   - Average session length
   - Is it appropriate for their goals?
   
3. CONSISTENCY ANALYSIS
   - How consistent is their practice?
   - Score: 0-100 (100 = perfect consistency)
   
4. STRUGGLING AREAS
   - Topics with low understanding scores
   - Repeated difficulties
   - Patterns in struggles
   
5. STRENGTHS
   - Topics they excel at
   - Fast learning areas
   
6. ACTIONABLE RECOMMENDATIONS
   - 3-5 specific suggestions to improve
   - Based on data, not generic advice
   
7. KEY INSIGHTS
   - Interesting patterns noticed
   - Unexpected findings

Return detailed JSON analysis.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data-driven learning analytics expert. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # More factual for analysis
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Add computed metrics
            analysis['total_sessions'] = len(sessions)
            analysis['total_time_minutes'] = sum(s.get('duration_minutes', 0) for s in sessions)
            analysis['timeframe_days'] = timeframe_days
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return {"error": str(e)}
    
    def detect_struggles(
        self,
        recent_sessions: List[Dict],
        knowledge_graph_data: Dict
    ) -> Dict:
        """
        Detect if learner is struggling and provide support
        
        Struggle indicators:
        - Low understanding ratings
        - Repeated topics without improvement
        - High difficulty ratings
        - Low enjoyment
        - Dropped sessions
        
        Args:
            recent_sessions: Last 5-10 sessions
            knowledge_graph_data: Current knowledge state
        
        Returns:
            {
                "is_struggling": bool,
                "struggle_level": str (low/medium/high),
                "specific_issues": List[Dict],
                "root_causes": List[str],
                "support_plan": Dict,
                "encouragement": str
            }
        """
        
        # Calculate struggle indicators
        struggle_signals = self._calculate_struggle_signals(recent_sessions)
        
        if struggle_signals['score'] < 3:  # Not struggling
            return {
                "is_struggling": False,
                "message": "You're doing great! Keep up the momentum."
            }
        
        context = {
            "signals": struggle_signals,
            "recent_sessions": [
                {
                    "topic": s.get('topic'),
                    "understanding_before": s.get('understanding_before'),
                    "understanding_after": s.get('understanding_after'),
                    "difficulty_rating": s.get('difficulty_rating'),
                    "enjoyment_rating": s.get('enjoyment_rating')
                }
                for s in recent_sessions[-5:]
            ],
            "knowledge_gaps": knowledge_graph_data.get('missing_prerequisites', [])
        }
        
        prompt = f"""
You are a compassionate learning coach identifying and addressing student struggles.

STRUGGLE INDICATORS:
{json.dumps(context, indent=2)}

Analyze the situation:

1. CONFIRM STRUGGLE
   - Is the student genuinely struggling? (yes/no)
   - Struggle level: low/medium/high
   
2. IDENTIFY SPECIFIC ISSUES
   - What exactly are they struggling with?
   - Be specific to topics/concepts
   
3. ROOT CAUSE ANALYSIS
   - Why might they be struggling?
   - Missing prerequisites?
   - Wrong difficulty level?
   - Learning approach mismatch?
   - External factors (time, motivation)?
   
4. SUPPORT PLAN
   - Immediate actions (tonight/tomorrow)
   - Short-term adjustments (this week)
   - Long-term strategy (if needed)
   - Resources to try
   - Easier alternative paths
   
5. ENCOURAGEMENT
   - Empathetic message
   - Normalize struggle (it's part of learning)
   - Boost confidence
   - Specific praise (something they did well)

TONE: Supportive, not judgmental. Struggles are learning opportunities.

Return JSON with is_struggling, struggle_level, specific_issues, root_causes, support_plan, encouragement.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an empathetic learning coach. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error detecting struggles: {e}")
            return {"error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # LEARNING PATH GENERATION
    # ═══════════════════════════════════════════════════════════════
    
    def generate_personalized_path(
        self,
        user_goal: str,
        current_knowledge: Dict,
        available_time_per_week: int,
        knowledge_graph: Dict,
        learning_style: Optional[str] = None
    ) -> Dict:
        """
        Generate personalized learning path from current state to goal
        
        Args:
            user_goal: What user wants to learn
            current_knowledge: What they already know (from graph)
            available_time_per_week: Hours per week
            knowledge_graph: Full graph structure
            learning_style: visual/auditory/reading/kinesthetic
        
        Returns:
            {
                "path_overview": str,
                "estimated_duration_weeks": int,
                "phases": List[Dict],
                "daily_schedule": Dict,
                "milestones": List[Dict],
                "resources": List[Dict]
            }
        """
        
        context = {
            "goal": user_goal,
            "knows": list(current_knowledge.get('mastered_concepts', [])),
            "gaps": list(current_knowledge.get('missing_prerequisites', [])),
            "time_per_week": available_time_per_week,
            "learning_style": learning_style or "mixed"
        }
        
        prompt = f"""
You are an expert curriculum designer creating a personalized learning path.

STUDENT PROFILE:
Goal: {user_goal}
Current knowledge: {', '.join(context['knows']) if context['knows'] else 'Beginner'}
Knowledge gaps: {', '.join(context['gaps']) if context['gaps'] else 'None identified'}
Available time: {available_time_per_week} hours/week
Learning style: {context['learning_style']}

AVAILABLE CONCEPTS (knowledge graph):
{json.dumps(knowledge_graph.get('concepts', []), indent=2)}

Create a personalized learning path with:

1. PATH OVERVIEW
   - High-level journey from current → goal
   - Key phases
   - Estimated timeline
   
2. LEARNING PHASES
   - Phase 1: Foundations (what + why + how long)
   - Phase 2: Core concepts
   - Phase 3: Advanced topics
   - Phase 4: Mastery & projects
   Each phase: topics, duration, goals
   
3. DAILY SCHEDULE
   - How to structure study time
   - Based on available hours
   - Include practice, theory, projects
   
4. MILESTONES
   - Clear checkpoints (with dates)
   - How to measure progress
   - Celebration points
   
5. RESOURCE RECOMMENDATIONS
   - Types of resources for their learning style
   - Specific suggestions if possible
   
6. ADAPTIVE NOTES
   - How path will adjust based on progress
   - Flexibility built in

IMPORTANT:
- Respect prerequisites from graph
- Realistic timelines (not overly optimistic)
- Build in review time
- Include practice/projects

Return comprehensive JSON with all sections.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert learning path designer. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Balanced creativity and structure
                response_format={"type": "json_object"}
            )
            
            path = json.loads(response.choices[0].message.content)
            
            # Add metadata
            path['created_at'] = datetime.now().isoformat()
            path['for_user_goal'] = user_goal
            path['based_on_knowledge'] = len(context['knows'])
            
            return path
            
        except Exception as e:
            print(f"Error generating learning path: {e}")
            return {"error": str(e)}
    
    def suggest_next_topic(
        self,
        current_knowledge: Dict,
        recent_sessions: List[Dict],
        user_preferences: Dict
    ) -> Dict:
        """
        Suggest what to study next (for today/this session)
        
        Considers:
        - Prerequisites met
        - Recent study topics (avoid repetition)
        - Difficulty progression
        - User's energy level / time available
        - Variety (theory vs practice)
        
        Args:
            current_knowledge: Mastered concepts + available next
            recent_sessions: Last few sessions
            user_preferences: Time available, difficulty preference
        
        Returns:
            {
                "recommended_topic": str,
                "reasoning": str,
                "difficulty": str,
                "estimated_time": int,
                "prerequisites_check": Dict,
                "alternative_options": List[str]
            }
        """
        
        # Get topics that are ready to learn (prerequisites met)
        available_topics = current_knowledge.get('ready_to_learn', [])
        recently_studied = [s.get('topic') for s in recent_sessions[-3:]]
        
        context = {
            "available_topics": available_topics,
            "recently_studied": recently_studied,
            "mastered": list(current_knowledge.get('mastered_concepts', [])),
            "time_available": user_preferences.get('time_available', 60),
            "energy_level": user_preferences.get('energy_level', 'medium'),
            "preference": user_preferences.get('difficulty_preference', 'progressive')
        }
        
        prompt = f"""
You are a learning coach deciding what the student should study RIGHT NOW.

CONTEXT:
{json.dumps(context, indent=2)}

Decide what to study next based on:

1. PREREQUISITES
   - Only suggest topics they're ready for
   - Don't suggest recently studied topics (variety)
   
2. DIFFICULTY MATCHING
   - Match to energy level:
     * high energy → can tackle harder topics
     * medium → balanced challenge
     * low energy → review or easier topics
   
3. TIME FITTING
   - Suggest topic that fits available time
   - Better to complete than rush
   
4. LEARNING MOMENTUM
   - Build on recent wins
   - Or address recent struggles
   
5. VARIETY
   - Mix theory and practice
   - Don't burn out on hard topics

Return:
{{
  "recommended_topic": "topic name",
  "reasoning": "why this topic now",
  "difficulty": "easy/medium/hard",
  "estimated_time": minutes,
  "prerequisites_check": {{"met": [], "missing": []}},
  "alternative_options": ["topic2", "topic3"],
  "study_approach": "how to approach this topic"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an adaptive learning coach. Return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error suggesting next topic: {e}")
            return {"error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # CONVERSATIONAL COACHING
    # ═══════════════════════════════════════════════════════════════
    
    def chat(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_context: Dict
    ) -> str:
        """
        General coaching chat - answer questions, provide guidance
        
        Args:
            user_message: What user said
            conversation_history: Previous messages
            user_context: User's learning state
        
        Returns:
            Coach's response
        """
        
        # Build context-aware system prompt
        system_prompt = f"""
You are {self.coach_persona['name']}, a personal learning coach for {user_context.get('full_name', 'the student')}.

STUDENT CONTEXT:
- Goal: {user_context.get('learning_goal', 'Learn new skills')}
- Current level: {user_context.get('current_level', 'Beginner')}
- Current streak: {user_context.get('current_streak', 0)} days
- Total sessions: {user_context.get('total_sessions', 0)}
- Recently studied: {', '.join(user_context.get('recent_topics', ['Nothing yet']))}

YOUR ROLE:
- Supportive personal trainer for learning
- Data-driven (reference their progress)
- Encouraging but honest
- Practical advice, not platitudes
- Help them overcome obstacles
- Celebrate wins

TONE: {self.coach_persona['tone']}

Respond naturally to their message. Reference their specific situation.
"""
        
        # Build messages for API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,  # More conversational
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I'm having trouble right now. Can you try again in a moment?"
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _build_morning_context(
        self,
        user_data: Dict,
        learning_history: List[Dict],
        knowledge_state: Dict
    ) -> Dict:
        """Build context for morning check-in"""
        
        yesterday_session = None
        if learning_history:
            yesterday_session = learning_history[0]
        
        return {
            "name": user_data.get('full_name', 'there'),
            "goal": user_data.get('learning_goal'),
            "current_level": user_data.get('current_level'),
            "streak": user_data.get('current_streak', 0),
            "total_sessions": user_data.get('total_sessions', 0),
            "yesterday": {
                "studied": yesterday_session is not None,
                "topic": yesterday_session.get('topic') if yesterday_session else None,
                "duration": yesterday_session.get('duration_minutes') if yesterday_session else None,
                "understanding": yesterday_session.get('understanding_after') if yesterday_session else None
            },
            "knowledge": {
                "mastered_count": len(knowledge_state.get('mastered', [])),
                "ready_to_learn": knowledge_state.get('ready_to_learn', [])[:3],
                "struggling_with": knowledge_state.get('struggling', [])
            }
        }
    
    def _prepare_session_summary(self, sessions: List[Dict]) -> Dict:
        """Prepare session data for analysis"""
        
        if not sessions:
            return {}
        
        return {
            "total_sessions": len(sessions),
            "sessions": [
                {
                    "date": s.get('start_time'),
                    "topic": s.get('topic'),
                    "duration_minutes": s.get('duration_minutes'),
                    "understanding_before": s.get('understanding_before'),
                    "understanding_after": s.get('understanding_after'),
                    "difficulty_rating": s.get('difficulty_rating'),
                    "enjoyment_rating": s.get('enjoyment_rating'),
                    "concepts_mastered": s.get('concepts_mastered', [])
                }
                for s in sessions
            ]
        }
    
    def _calculate_struggle_signals(self, sessions: List[Dict]) -> Dict:
        """Calculate struggle score from recent sessions"""
        
        if not sessions:
            return {"score": 0, "signals": []}
        
        signals = []
        score = 0
        
        # Check last 5 sessions
        recent = sessions[-5:]
        
        # Signal 1: Low understanding improvement
        avg_improvement = sum(
            (s.get('understanding_after', 5) - s.get('understanding_before', 5))
            for s in recent
        ) / len(recent)
        
        if avg_improvement < 1:
            signals.append("Low understanding improvement")
            score += 2
        
        # Signal 2: High difficulty ratings
        avg_difficulty = sum(s.get('difficulty_rating', 5) for s in recent) / len(recent)
        if avg_difficulty > 7:
            signals.append("Topics feel too difficult")
            score += 2
        
        # Signal 3: Low enjoyment
        avg_enjoyment = sum(s.get('enjoyment_rating', 5) for s in recent) / len(recent)
        if avg_enjoyment < 4:
            signals.append("Low enjoyment ratings")
            score += 1
        
        # Signal 4: Repeated topics without progress
        topics = [s.get('topic') for s in recent]
        if len(topics) != len(set(topics)):  # Duplicates
            signals.append("Repeating topics without mastery")
            score += 2
        
        # Signal 5: Short sessions
        avg_duration = sum(s.get('duration_minutes', 0) for s in recent) / len(recent)
        if avg_duration < 20:
            signals.append("Very short study sessions")
            score += 1
        
        return {
            "score": score,
            "max_score": 8,
            "signals": signals,
            "metrics": {
                "avg_improvement": round(avg_improvement, 1),
                "avg_difficulty": round(avg_difficulty, 1),
                "avg_enjoyment": round(avg_enjoyment, 1),
                "avg_duration": round(avg_duration, 1)
            }
        }
    
    def _fallback_morning_checkin(self, user_data: Dict) -> Dict:
        """Fallback if API fails"""
        return {
            "greeting": f"Good morning, {user_data.get('full_name', 'there')}!",
            "motivation": "Every expert was once a beginner. Today is another step forward.",
            "today_plan": "Let's review what you learned recently and build on it.",
            "recommended_duration": 60,
            "suggested_topics": ["Review previous concepts"],
            "encouragement": "You've got this! Let's make today count."
        }
    
    def _fallback_evening_reflection(self) -> Dict:
        """Fallback if API fails"""
        return {
            "summary": "Great job completing your session today!",
            "progress_analysis": "You're making steady progress toward your goals.",
            "wins": ["Showed up and learned something new"],
            "areas_to_improve": [],
            "tomorrow_preview": "We'll continue building on what you learned today.",
            "reflection_questions": [
                "What was the most interesting thing you learned?",
                "What would you like to explore more deeply?"
            ]
        }
    
    def _generate_missed_day_reflection(self, user_data: Dict) -> Dict:
        """Generate reflection when user missed a day"""
        
        streak = user_data.get('current_streak', 0)
        
        return {
            "missed_day": True,
            "message": f"Hey {user_data.get('full_name', 'there')}, I noticed you didn't have a session today.",
            "understanding": "Life happens - no judgment here!",
            "streak_status": f"Your streak: {streak} days",
            "motivation": "Tomorrow is a fresh start. Even 15 minutes counts!",
            "suggestion": "Want to do a quick 15-minute session before bed? It's not too late.",
            "encouragement": "Remember why you started. You're capable of amazing things."
        }


# ═══════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Test the AI Coach
    """
    
    coach = AICoach()
    
    # Example user data
    user_data = {
        "full_name": "Janani",
        "learning_goal": "Learn Machine Learning",
        "current_level": "Beginner",
        "current_streak": 5,
        "total_sessions": 12,
        "total_learning_minutes": 720
    }
    
    # Example learning history
    learning_history = [
        {
            "topic": "Linear Regression",
            "duration_minutes": 45,
            "understanding_before": 3,
            "understanding_after": 7,
            "difficulty_rating": 6,
            "enjoyment_rating": 8,
            "concepts_mastered": ["Linear Regression Basics", "Cost Function"]
        }
    ]
    
    # Example knowledge state
    knowledge_state = {
        "mastered": ["Python Basics", "Variables", "Functions"],
        "ready_to_learn": ["Linear Algebra", "NumPy", "Pandas"],
        "struggling": []
    }
    
    print("="*70)
    print("TESTING AI COACH")
    print("="*70)
    
    # Test 1: Morning check-in
    print("\n[Test 1] Morning Check-in")
    print("-"*70)
    checkin = coach.generate_morning_checkin(
        user_data,
        learning_history,
        knowledge_state
    )
    print(json.dumps(checkin, indent=2))
    
    # Test 2: Evening reflection
    print("\n[Test 2] Evening Reflection")
    print("-"*70)
    reflection = coach.generate_evening_reflection(
        user_data,
        learning_history[0],
        ["Linear Regression", "Cost Function"]
    )
    print(json.dumps(reflection, indent=2))
    
    # Test 3: Next topic suggestion
    print("\n[Test 3] Next Topic Suggestion")
    print("-"*70)
    next_topic = coach.suggest_next_topic(
        knowledge_state,
        learning_history,
        {"time_available": 60, "energy_level": "high"}
    )
    print(json.dumps(next_topic, indent=2))
    
    # Test 4: Chat
    print("\n[Test 4] Coaching Chat")
    print("-"*70)
    response = coach.chat(
        "I'm feeling stuck on linear regression. The math is confusing.",
        [],
        user_data
    )
    print(f"Coach: {response}")
    
    print("\n" + "="*70)
    print("✓ AI Coach tests complete!")
    print("="*70)