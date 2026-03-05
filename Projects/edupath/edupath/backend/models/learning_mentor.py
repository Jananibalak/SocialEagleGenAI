from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from shared.database import Base

class LearningMentor(Base):
    __tablename__ = "learning_mentors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Mentor identity
    name = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    avatar_emoji = Column(String, default='📚')
    personality = Column(String)
    
    # ✅ ADD: Learning Plan
    learning_plan = Column(Text)  # JSON string of the plan
    current_day = Column(Integer, default=1)  # Which day of the plan
    plan_status = Column(String, default='active')  # active, completed, paused
    
    # Learning goal
    goal_description = Column(Text)
    target_days = Column(Integer)
    deadline = Column(DateTime)
    
    # Stats
    total_messages = Column(Integer, default=0)
    knowledge_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True))
    last_ai_message = Column(Text)
    
class KnowledgeScroll(Base):
    __tablename__ = "knowledge_scrolls"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey('learning_mentors.id'), nullable=False)
    
    # File info
    file_name = Column(String, nullable=False)
    file_type = Column(String)  # pdf, docx, txt, youtube
    file_url = Column(String)  # Storage path
    file_size = Column(Integer)
    
    # Content
    extracted_text = Column(Text)
    summary = Column(Text)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
class MentorMessage(Base):
    __tablename__ = "mentor_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey('learning_mentors.id'), nullable=False)
    
    sender = Column(String, nullable=False)  # 'user' or 'ai'
    message_text = Column(Text, nullable=False)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    tokens_used = Column(Integer, default=0)
    def __repr__(self):
        return f"<MentorMessage {self.id} from {self.sender}>"