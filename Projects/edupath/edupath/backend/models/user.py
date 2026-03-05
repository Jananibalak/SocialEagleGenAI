from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
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
    mobile_number = Column(String)
    learning_goal = Column(String)
    current_level = Column(String, default="Beginner")

    # Tokens & Subscription
    token_balance = Column(Float, default=0.0)
    razorpay_customer_id = Column(String, unique=True)

    # Stats
    total_sessions = Column(Integer, default=0)
    total_learning_minutes = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    mastery_score = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_checkin = Column(DateTime(timezone=True))
    last_active = Column(DateTime(timezone=True))

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)

    # Session info
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    topic = Column(String)

    # Ratings
    understanding_before = Column(Integer)
    understanding_after = Column(Integer)
    difficulty_rating = Column(Integer)
    enjoyment_rating = Column(Integer)

    # Notes
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
