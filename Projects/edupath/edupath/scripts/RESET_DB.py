"""Reset database - DESTROYS ALL DATA!"""
from sqlalchemy import text
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import engine, SessionLocal
from backend.models.user import User
from backend.models.token_transaction import TokenTransaction, TransactionType
from backend.models.learning_mentor import LearningMentor, KnowledgeScroll, MentorMessage

def reset_database():
    """Drop all tables and recreate"""
    
    print("⚠️  WARNING: This will DELETE ALL DATA!")
    response = input("Type 'YES' to confirm: ")
    
    if response != 'YES':
        print("❌ Aborted")
        return
    
    print("🗑️  Dropping all tables...")
    
    # Drop tables in reverse order (due to foreign keys)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS mentor_messages CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS knowledge_scrolls CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS learning_mentors CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS token_transactions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS learning_sessions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    
    print("✅ All tables dropped")
    
    print("🔨 Creating new tables...")
    
    # Import Base and create all tables
    from shared.database import Base
    Base.metadata.create_all(bind=engine)
    
    print("✅ All tables created with new schema")
    print("✅ Database reset complete!")
    print("\n💡 You can now create new users and mentors")

if __name__ == "__main__":
    reset_database()