from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from backend.models.user import User, LearningSession
from backend.services.ai_coach_advanced import AdvancedAICoach
from backend.services.knowledge_graph import KnowledgeGraphService

class CheckinService:
    def __init__(self):
        self.coach = AdvancedAICoach()
        self.kg = KnowledgeGraphService()

    def generate_morning_checkin(self, db: Session, user_id: int) -> Dict:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        recent_sessions = db.query(LearningSession)\
            .filter(LearningSession.user_id == user_id)\
            .order_by(LearningSession.start_time.desc())\
            .limit(10)\
            .all()

        sessions_data = [
            {
                "topic": s.topic,
                "duration_minutes": s.duration_minutes,
                "understanding_after": s.understanding_after
            }
            for s in recent_sessions
        ]

        knowledge_state = self.kg.get_user_knowledge_state(user_id)

        user_data = {
            "full_name": user.full_name,
            "learning_goal": user.learning_goal,
            "current_level": user.current_level,
            "current_streak": user.current_streak,
            "total_sessions": user.total_sessions
        }

        checkin = self.coach.generate_morning_checkin(
            user_data=user_data,
            learning_history=sessions_data,
            knowledge_state=knowledge_state
        )

        user.last_checkin = datetime.now()
        db.commit()

        return checkin

    def start_session(self, db: Session, user_id: int, topic: str, understanding_before: int) -> Dict:
        session = LearningSession(
            user_id=user_id,
            start_time=datetime.now(),
            topic=topic,
            understanding_before=understanding_before
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return {
            "session_id": session.id,
            "topic": topic,
            "started_at": session.start_time.isoformat()
        }

    def end_session(self, db: Session, session_id: int, understanding_after: int, difficulty_rating: int, enjoyment_rating: int, notes: str = None) -> Dict:
        session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            return {"error": "Session not found"}

        session.end_time = datetime.now()
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
        session.understanding_after = understanding_after
        session.difficulty_rating = difficulty_rating
        session.enjoyment_rating = enjoyment_rating
        session.notes = notes

        user = db.query(User).filter(User.id == session.user_id).first()
        user.total_sessions += 1
        user.total_learning_minutes += session.duration_minutes

        db.commit()

        return {
            "session_id": session.id,
            "duration_minutes": session.duration_minutes,
            "improvement": understanding_after - session.understanding_before
        }
