from datetime import datetime, timedelta, time
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

# Absolute imports
from backend.models.user import User, LearningSession
from backend.services.ai_coach import AICoach
from backend.services.knowledge_graph import KnowledgeGraphService
import pytz

class CheckinService:
    """
    Manages daily check-ins and learning accountability
    
    Features:
    1. Morning check-ins (motivation + today's plan)
    2. Evening reflections (progress analysis)
    3. Streak tracking
    4. Missed day handling
    5. Reminder scheduling
    """
    
    def __init__(self):
        self.coach = AICoach()
        self.kg = KnowledgeGraphService()
    
    # ═══════════════════════════════════════════════════════════════
    # MORNING CHECK-IN
    # ═══════════════════════════════════════════════════════════════
    
    def generate_morning_checkin(
        self,
        db: Session,
        user_id: int
    ) -> Dict:
        """
        Generate personalized morning check-in
        
        Returns:
        {
            "greeting": str,
            "motivation": str,
            "today_plan": str,
            "suggested_topics": List[str],
            "recommended_duration": int,
            "streak_info": Dict,
            "timestamp": str
        }
        """
        
        # Get user data
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get recent learning history
        recent_sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(10)\
            .all()
        
        # Convert to dicts
        sessions_data = [
            {
                "topic": s.topic,
                "duration_minutes": s.duration_minutes,
                "understanding_before": s.understanding_before,
                "understanding_after": s.understanding_after,
                "difficulty_rating": s.difficulty_rating,
                "start_time": s.start_time.isoformat() if s.start_time else None
            }
            for s in recent_sessions
        ]
        
        # Get knowledge state from graph
        knowledge_state = self.kg.get_user_knowledge_state(user_id)
        
        # Build user data dict
        user_data = {
            "full_name": user.full_name,
            "learning_goal": user.learning_goal,
            "current_level": user.current_level,
            "current_streak": user.current_streak,
            "total_sessions": user.total_sessions,
            "total_learning_minutes": user.total_learning_minutes
        }
        
        # Generate AI check-in
        checkin = self.coach.generate_morning_checkin(
            user_data=user_data,
            learning_history=sessions_data,
            knowledge_state=knowledge_state
        )
        
        # Add streak info
        checkin["streak_info"] = {
            "current": user.current_streak,
            "longest": user.longest_streak,
            "status": self._get_streak_status(user.current_streak),
            "next_milestone": self._next_streak_milestone(user.current_streak)
        }
        
        # Update last check-in time
        user.last_checkin = datetime.now()
        db.commit()
        
        return checkin
    
    # ═══════════════════════════════════════════════════════════════
    # EVENING REFLECTION
    # ═══════════════════════════════════════════════════════════════
    
    def generate_evening_reflection(
        self,
        db: Session,
        user_id: int
    ) -> Dict:
        """
        Generate evening reflection based on today's session
        
        Returns reflection with progress analysis and encouragement
        """
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get today's session
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_session = db.query(LearningSession)\
            .filter(
                LearningSession.user_id == user_id,
                LearningSession.start_time >= today_start
            )\
            .order_by(LearningSession.start_time.desc())\
            .first()
        
        if not today_session:
            # No session today - missed day reflection
            return self._generate_missed_day_reflection(user)
        
        # Convert session to dict
        session_data = {
            "topic": today_session.topic,
            "duration_minutes": today_session.duration_minutes,
            "understanding_before": today_session.understanding_before,
            "understanding_after": today_session.understanding_after,
            "difficulty_rating": today_session.difficulty_rating,
            "enjoyment_rating": today_session.enjoyment_rating,
            "notes": today_session.notes
        }
        
        # Get concepts learned
        knowledge_gained = today_session.concepts_mastered or []
        
        # Build user data
        user_data = {
            "full_name": user.full_name,
            "learning_goal": user.learning_goal,
            "total_sessions": user.total_sessions,
            "current_streak": user.current_streak
        }
        
        # Generate AI reflection
        reflection = self.coach.generate_evening_reflection(
            user_data=user_data,
            today_session=session_data,
            knowledge_gained=knowledge_gained
        )
        
        # Add session summary
        reflection["session_summary"] = {
            "topic": today_session.topic,
            "duration": today_session.duration_minutes,
            "improvement": today_session.understanding_after - today_session.understanding_before,
            "concepts_learned": len(knowledge_gained)
        }
        
        return reflection
    
    # ═══════════════════════════════════════════════════════════════
    # STREAK TRACKING
    # ═══════════════════════════════════════════════════════════════
    
    def update_streak(
        self,
        db: Session,
        user_id: int,
        session_completed: bool = True
    ) -> Dict:
        """
        Update user's learning streak
        
        Args:
            user_id: User ID
            session_completed: True if user completed session today
        
        Returns:
            {
                "current_streak": int,
                "longest_streak": int,
                "streak_status": str,
                "milestone_reached": bool
            }
        """
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        today = datetime.now().date()
        
        if user.last_active:
            last_active_date = user.last_active.date()
            days_since_last = (today - last_active_date).days
        else:
            days_since_last = 999  # First time
        
        old_streak = user.current_streak
        milestone_reached = False
        
        if session_completed:
            if days_since_last == 0:
                # Already studied today - no change
                pass
            elif days_since_last == 1:
                # Consecutive day - increment streak
                user.current_streak += 1
                
                # Check milestone
                if user.current_streak in [7, 14, 30, 60, 100, 365]:
                    milestone_reached = True
            else:
                # Missed days - reset streak
                user.current_streak = 1
            
            # Update longest streak
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
            
            # Update last active
            user.last_active = datetime.now()
        else:
            # Missed day
            if days_since_last > 1:
                user.current_streak = 0
        
        db.commit()
        
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "streak_status": self._get_streak_status(user.current_streak),
            "milestone_reached": milestone_reached,
            "milestone": user.current_streak if milestone_reached else None,
            "streak_changed": old_streak != user.current_streak
        }
    
    def check_streak_at_risk(
        self,
        db: Session,
        user_id: int
    ) -> Dict:
        """
        Check if user's streak is at risk (didn't study today)
        
        Returns:
        {
            "at_risk": bool,
            "current_streak": int,
            "hours_remaining": float,
            "message": str
        }
        """
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Check if studied today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_session = db.query(LearningSession)\
            .filter(
                LearningSession.user_id == user_id,
                LearningSession.start_time >= today_start
            )\
            .first()
        
        if today_session:
            return {
                "at_risk": False,
                "current_streak": user.current_streak,
                "message": "Streak safe! You've already studied today."
            }
        
        # Calculate hours remaining
        now = datetime.now()
        end_of_day = now.replace(hour=23, minute=59, second=59)
        hours_remaining = (end_of_day - now).total_seconds() / 3600
        
        return {
            "at_risk": True,
            "current_streak": user.current_streak,
            "hours_remaining": round(hours_remaining, 1),
            "message": f"Your {user.current_streak}-day streak is at risk! Study today to keep it alive.",
            "urgency": "high" if hours_remaining < 3 else "medium" if hours_remaining < 6 else "low"
        }
    
    # ═══════════════════════════════════════════════════════════════
    # SESSION LOGGING
    # ═══════════════════════════════════════════════════════════════
    
    def start_session(
        self,
        db: Session,
        user_id: int,
        topic: str,
        understanding_before: int
    ) -> Dict:
        """
        Start a new learning session
        
        Returns session ID and suggested focus
        """
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Create session
        session = LearningSession(
            user_id=user_id,
            start_time=datetime.now(),
            topic=topic,
            understanding_before=understanding_before
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Get AI suggestions for this session
        knowledge_state = self.kg.get_user_knowledge_state(user_id)
        recent_sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(5)\
            .all()
        
        recent_data = [
            {"topic": s.topic, "understanding_after": s.understanding_after}
            for s in recent_sessions
        ]
        
        user_prefs = {
            "time_available": user.preferred_learning_duration or 60,
            "energy_level": "medium"
        }
        
        suggestions = self.coach.suggest_next_topic(
            current_knowledge=knowledge_state,
            recent_sessions=recent_data,
            user_preferences=user_prefs
        )
        
        return {
            "session_id": session.id,
            "topic": topic,
            "started_at": session.start_time.isoformat(),
            "suggestions": suggestions,
            "message": f"Session started! Focus on {topic}."
        }
    
    def end_session(
        self,
        db: Session,
        session_id: int,
        understanding_after: int,
        difficulty_rating: int,
        enjoyment_rating: int,
        notes: Optional[str] = None,
        concepts_mastered: Optional[List[str]] = None
    ) -> Dict:
        """
        End a learning session and update progress
        
        This is where the magic happens:
        1. Calculate duration
        2. Update session record
        3. Update concept mastery in graph
        4. Update user stats
        5. Update streak
        6. Generate feedback
        """
        
        session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            return {"error": "Session not found"}
        
        # Calculate duration
        session.end_time = datetime.now()
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
        
        # Update session data
        session.understanding_after = understanding_after
        session.difficulty_rating = difficulty_rating
        session.enjoyment_rating = enjoyment_rating
        session.notes = notes
        session.concepts_mastered = concepts_mastered or []
        
        # Update user stats
        user = db.query(User).filter(User.id == session.user_id).first()
        user.total_sessions += 1
        user.total_learning_minutes += session.duration_minutes
        
        # Update streak
        streak_update = self.update_streak(db, session.user_id, session_completed=True)
        
        # Update concept mastery in knowledge graph
        mastery_updates = []
        for concept in (concepts_mastered or []):
            mastery = self.kg.update_concept_mastery(
                user_id=session.user_id,
                concept_name=concept,
                session_data={
                    "understanding_before": session.understanding_before,
                    "understanding_after": understanding_after,
                    "duration_minutes": session.duration_minutes,
                    "difficulty_rating": difficulty_rating,
                    "enjoyment_rating": enjoyment_rating
                }
            )
            mastery_updates.append(mastery)
        
        # Generate AI feedback
        improvement = understanding_after - session.understanding_before
        
        feedback = self._generate_session_feedback(
            improvement=improvement,
            difficulty=difficulty_rating,
            enjoyment=enjoyment_rating,
            duration=session.duration_minutes,
            mastery_updates=mastery_updates,
            streak=streak_update
        )
        
        db.commit()
        
        return {
            "session_id": session.id,
            "duration_minutes": session.duration_minutes,
            "improvement": improvement,
            "concepts_mastered": len(mastery_updates),
            "mastery_updates": mastery_updates,
            "streak": streak_update,
            "feedback": feedback,
            "celebration": streak_update.get("milestone_reached", False)
        }
    
    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def _get_streak_status(self, streak: int) -> str:
        """Get motivational streak status"""
        if streak == 0:
            return "New beginning"
        elif streak < 3:
            return "Building momentum"
        elif streak < 7:
            return "Getting consistent"
        elif streak < 14:
            return "Week warrior"
        elif streak < 30:
            return "Habit forming"
        elif streak < 60:
            return "Dedicated learner"
        elif streak < 100:
            return "Learning machine"
        else:
            return "Legend"
    
    def _next_streak_milestone(self, current: int) -> int:
        """Get next streak milestone"""
        milestones = [7, 14, 30, 60, 100, 365]
        for milestone in milestones:
            if current < milestone:
                return milestone
        return 500  # Next after 365
    
    def _generate_missed_day_reflection(self, user: User) -> Dict:
        """Generate reflection when user missed a day"""
        
        return {
            "missed_day": True,
            "message": f"Hey {user.full_name}, I noticed you didn't have a session today.",
            "understanding": "Life happens - no judgment here! 💙",
            "streak_status": {
                "current": user.current_streak,
                "at_risk": True,
                "message": f"Your {user.current_streak}-day streak is safe for now, but study tomorrow to keep it!"
            },
            "motivation": "Even 15 minutes counts. Tomorrow is a fresh start!",
            "quick_action": {
                "suggestion": "Do a quick 10-minute review before bed?",
                "benefit": "It'll keep your streak alive and help retention!"
            },
            "encouragement": "Remember why you started. You're capable of amazing things. See you tomorrow! 🌟"
        }
    
    def _generate_session_feedback(
        self,
        improvement: int,
        difficulty: int,
        enjoyment: int,
        duration: int,
        mastery_updates: List[Dict],
        streak: Dict
    ) -> Dict:
        """Generate personalized feedback after session"""
        
        feedback = {
            "overall": "",
            "highlights": [],
            "suggestions": []
        }
        
        # Overall assessment
        if improvement >= 5:
            feedback["overall"] = "Excellent progress! You crushed this session! 🚀"
        elif improvement >= 3:
            feedback["overall"] = "Great work! Solid improvement today. 💪"
        elif improvement >= 1:
            feedback["overall"] = "Good session! You're moving forward. 👍"
        elif improvement == 0:
            feedback["overall"] = "You showed up - that's what matters. Let's review this tomorrow."
        else:
            feedback["overall"] = "Tough session, but don't give up. Sometimes we need to revisit concepts."
        
        # Highlights
        if mastery_updates:
            mastered = [m for m in mastery_updates if m.get("mastered")]
            if mastered:
                feedback["highlights"].append(
                    f"🎉 Mastered {len(mastered)} concepts: {', '.join([m['concept'] for m in mastered])}"
                )
        
        if streak.get("milestone_reached"):
            feedback["highlights"].append(
                f"🔥 MILESTONE! {streak['current_streak']}-day streak! You're a learning machine!"
            )
        elif streak.get("streak_changed") and streak["current_streak"] > 0:
            feedback["highlights"].append(
                f"✨ {streak['current_streak']}-day streak maintained!"
            )
        
        if enjoyment >= 8:
            feedback["highlights"].append("😊 You really enjoyed this topic - that's powerful!")
        
        # Suggestions
        if difficulty >= 8 and improvement < 3:
            feedback["suggestions"].append(
                "This topic is challenging. Consider breaking it into smaller pieces tomorrow."
            )
        
        if duration < 20:
            feedback["suggestions"].append(
                "Short session today. Try for 30-45 minutes next time for better retention."
            )
        elif duration > 90:
            feedback["suggestions"].append(
                "Long session! Remember to take breaks. Shorter, focused sessions often work better."
            )
        
        if enjoyment < 5:
            feedback["suggestions"].append(
                "Low enjoyment rating. Try a different resource or approach to this topic."
            )
        
        return feedback
    
    # ═══════════════════════════════════════════════════════════════
    # DAILY SUMMARY
    # ═══════════════════════════════════════════════════════════════
    
    def get_daily_summary(
        self,
        db: Session,
        user_id: int
    ) -> Dict:
        """
        Get complete summary for today
        
        Returns:
        {
            "date": str,
            "session_completed": bool,
            "session_details": Dict,
            "streak": Dict,
            "progress_today": Dict,
            "tomorrow_preview": str
        }
        """
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get today's session
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_session = db.query(LearningSession)\
            .filter(
                LearningSession.user_id == user_id,
                LearningSession.start_time >= today_start
            )\
            .first()
        
        summary = {
            "date": datetime.now().date().isoformat(),
            "session_completed": today_session is not None,
            "streak": {
                "current": user.current_streak,
                "longest": user.longest_streak,
                "status": self._get_streak_status(user.current_streak)
            }
        }
        
        if today_session:
            summary["session_details"] = {
                "topic": today_session.topic,
                "duration_minutes": today_session.duration_minutes,
                "improvement": today_session.understanding_after - today_session.understanding_before if today_session.understanding_after else 0,
                "concepts_mastered": len(today_session.concepts_mastered or [])
            }
        else:
            summary["session_details"] = None
            summary["reminder"] = "No session today - your streak is at risk!"
        
        # Get knowledge state for tomorrow preview
        knowledge_state = self.kg.get_user_knowledge_state(user_id)
        
        if knowledge_state.get("ready_to_learn"):
            next_topics = knowledge_state["ready_to_learn"][:3]
            summary["tomorrow_preview"] = f"Tomorrow's suggestions: {', '.join([t['concept'] for t in next_topics])}"
        else:
            summary["tomorrow_preview"] = "Keep building on what you learned today!"
        
        return summary


# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test the Check-in Service"""
    
    from shared.database import SessionLocal, engine, Base
    from models.user import User, LearningSession
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    print("="*70)
    print("TESTING CHECK-IN SERVICE")
    print("="*70)
    
    # Create test database session
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = User(
            username="janani_test",
            email="janani@test.com",
            hashed_password="hashed",
            full_name="Janani",
            learning_goal="Learn Machine Learning",
            current_level="Beginner",
            current_streak=5,
            total_sessions=12,
            total_learning_minutes=720
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"\n✓ Created test user: {test_user.full_name} (ID: {test_user.id})")
        
        # Initialize service
        checkin_service = CheckinService()
        
        # Test 1: Morning check-in
        print("\n[Test 1] Morning Check-in")
        print("-"*70)
        morning = checkin_service.generate_morning_checkin(db, test_user.id)
        print(f"Greeting: {morning.get('greeting', 'N/A')}")
        print(f"Today's Plan: {morning.get('today_plan', 'N/A')[:100]}...")
        print(f"Streak: {morning.get('streak_info', {})}")
        
        # Test 2: Start session
        print("\n[Test 2] Start Learning Session")
        print("-"*70)
        session_start = checkin_service.start_session(
            db=db,
            user_id=test_user.id,
            topic="Linear Algebra",
            understanding_before=4
        )
        print(f"Session ID: {session_start.get('session_id')}")
        print(f"Started at: {session_start.get('started_at')}")
        
        # Test 3: End session
        print("\n[Test 3] End Learning Session")
        print("-"*70)
        session_end = checkin_service.end_session(
            db=db,
            session_id=session_start['session_id'],
            understanding_after=8,
            difficulty_rating=6,
            enjoyment_rating=7,
            notes="Great session on vectors!",
            concepts_mastered=["Vectors", "Matrix Operations"]
        )
        print(f"Duration: {session_end.get('duration_minutes')} minutes")
        print(f"Improvement: +{session_end.get('improvement')}")
        print(f"Streak: {session_end.get('streak', {}).get('current_streak')} days")
        print(f"Feedback: {session_end.get('feedback', {}).get('overall')}")
        
        # Test 4: Evening reflection
        print("\n[Test 4] Evening Reflection")
        print("-"*70)
        reflection = checkin_service.generate_evening_reflection(db, test_user.id)
        print(f"Summary: {reflection.get('summary', 'N/A')[:100]}...")
        print(f"Wins: {len(reflection.get('wins', []))} wins identified")
        
        # Test 5: Daily summary
        print("\n[Test 5] Daily Summary")
        print("-"*70)
        summary = checkin_service.get_daily_summary(db, test_user.id)
        print(f"Date: {summary.get('date')}")
        print(f"Session completed: {summary.get('session_completed')}")
        print(f"Current streak: {summary.get('streak', {}).get('current')}")
        
        print("\n" + "="*70)
        print("✓ Check-in Service tests complete!")
        print("="*70)
        
    finally:
        # Cleanup
        db.query(LearningSession).delete()
        db.query(User).delete()
        db.commit()
        db.close()