import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from shared.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile
    full_name = Column(String)
    learning_goal = Column(String)  # e.g., "Learn Machine Learning"
    current_level = Column(String)  # e.g., "Beginner", "Intermediate"
    
    # Preferences
    daily_checkin_time = Column(String, default="09:00")  # HH:MM format
    preferred_learning_duration = Column(Integer, default=60)  # minutes
    learning_style = Column(String)  # visual, auditory, reading, kinesthetic
    
    # Stats
    total_sessions = Column(Integer, default=0)
    total_learning_minutes = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    mastery_score = Column(Float, default=0.0)  # 0-100
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_checkin = Column(DateTime(timezone=True))
    last_active = Column(DateTime(timezone=True))
    
    # Settings
    settings = Column(JSON, default={})  # Flexible settings storage


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Session info
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # What was learned
    topic = Column(String)  # Main topic covered
    subtopics = Column(JSON)  # List of subtopics
    resources_used = Column(JSON)  # List of resource IDs
    
    # Self-assessment
    understanding_before = Column(Integer)  # 1-10 scale
    understanding_after = Column(Integer)  # 1-10 scale
    difficulty_rating = Column(Integer)  # 1-10 scale
    enjoyment_rating = Column(Integer)  # 1-10 scale
    
    # AI Coach notes
    coach_feedback = Column(String)
    concepts_mastered = Column(JSON)  # List of concept names
    concepts_struggling = Column(JSON)
    next_recommended = Column(JSON)  # Next topics to study
    
    # Metadata
    notes = Column(String)  # User's notes from session
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Goal details
    title = Column(String, nullable=False)
    description = Column(String)
    target_topic = Column(String)  # Main topic/skill to master
    
    # Timeline
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Progress
    status = Column(String, default="active")  # active, completed, abandoned
    progress_percentage = Column(Float, default=0.0)  # 0-100
    
    # Milestones
    milestones = Column(JSON)  # List of milestone dicts
    # Example: [
    #   {"name": "Complete basics", "completed": true, "date": "2024-01-15"},
    #   {"name": "Build first project", "completed": false}
    # ]
    
    # Tracking
    sessions_count = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)  # minutes